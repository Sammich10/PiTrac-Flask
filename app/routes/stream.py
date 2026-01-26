from flask import (
    Blueprint, Flask, render_template, Response, request, jsonify, 
    redirect, url_for, session, current_app
)
import cv2
import numpy as np
import base64
import binascii
import time
import zmq
import threading
import queue
from collections import defaultdict
from ..messages.external.CameraFrameMsg import CameraFrameMsg

bp = Blueprint('stream', __name__, url_prefix='/stream')

# Global frame distributor
frame_distributor = None

class FrameDistributor:
    """Centralized frame receiver that distributes to multiple clients"""
    
    def __init__(self, pitrac_connection):
        self.pitrac = pitrac_connection
        self.running = False
        self.thread = None
        
        # Camera-specific frame queues for clients
        # Structure: {camera_id: [queue1, queue2, ...]}
        self.client_queues = defaultdict(list)
        self.lock = threading.Lock()
        
    def start(self):
        """Start the frame receiver thread"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._receive_frames, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the frame receiver thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def subscribe_camera(self, camera_id, max_queue_size=5):
        """Subscribe to frames from a specific camera"""
        client_queue = queue.Queue(maxsize=max_queue_size)
        
        with self.lock:
            self.client_queues[camera_id].append(client_queue)
        
        return client_queue
    
    def unsubscribe_camera(self, camera_id, client_queue):
        """Unsubscribe from camera frames"""
        with self.lock:
            if camera_id in self.client_queues:
                try:
                    self.client_queues[camera_id].remove(client_queue)
                    if not self.client_queues[camera_id]:
                        del self.client_queues[camera_id]
                except ValueError:
                    pass
    
    def _receive_frames(self):
        """Background thread that receives and distributes frames"""
        while self.running:
            try:
                if not self.pitrac.framesocket:
                    time.sleep(0.1)
                    continue
                
                # Non-blocking receive
                if self.pitrac.framesocket.poll(100):
                    data = self.pitrac.framesocket.recv(zmq.NOBLOCK)
                    
                    # Deserialize frame
                    try:
                        frame_msg = CameraFrameMsg()
                        frame_msg.deserialize(data)
                        
                        # Process frame into bytes
                        frame_bytes = self._process_frame(frame_msg)
                        if frame_bytes:
                            # Distribute to subscribers
                            self._distribute_frame(frame_msg.camera_id, frame_bytes)
                            
                    except Exception as e:
                        print(f"Frame processing error: {e}")
                        continue
                        
            except zmq.Again:
                continue
            except Exception as e:
                print(f"Frame receive error: {e}")
                time.sleep(0.1)
    
    def _process_frame(self, frame_msg):
        """Process frame message into streamable bytes"""
        try:
            if isinstance(frame_msg.image_data, bytes):
                frame_bytes = frame_msg.image_data
                
                # Validate JPEG data
                if len(frame_bytes) > 0:
                    if frame_bytes[:2] == b'\xff\xd8':
                        return frame_bytes
                    else:
                        # Try OpenCV decoding and re-encoding
                        nparr = np.frombuffer(frame_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            return buffer.tobytes()
            
            return None
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return None
    
    def _distribute_frame(self, camera_id, frame_bytes):
        """Distribute frame to all subscribers of this camera"""
        with self.lock:
            if camera_id in self.client_queues:
                for client_queue in self.client_queues[camera_id][:]:  # Copy to avoid modification during iteration
                    try:
                        # Non-blocking put, drop frame if queue is full
                        client_queue.put_nowait(frame_bytes)
                    except queue.Full:
                        # Drop oldest frame and add new one
                        try:
                            client_queue.get_nowait()
                            client_queue.put_nowait(frame_bytes)
                        except queue.Empty:
                            pass


def get_frame_distributor():
    """Get or create global frame distributor"""
    global frame_distributor
    
    if frame_distributor is None:
        pitrac = current_app.pitrac_connection
        frame_distributor = FrameDistributor(pitrac)
        frame_distributor.start()
    
    return frame_distributor


def get_pitrac():
    """Helper to get PiTrac connection from current app"""
    return current_app.pitrac_connection


def generate_frames_for_camera(app, camera_id):
    """Generator function that yields frames from the frame distributor for a specific camera"""
    with app.app_context():
        distributor = get_frame_distributor()
        client_queue = distributor.subscribe_camera(camera_id)
        
        try:
            while True:
                try:
                    # Get frame from queue with timeout
                    frame_bytes = client_queue.get(timeout=1.0)
                    # Stream with proper multipart boundary
                    response = (b'--frame\r\n'
                              b'Content-Type: image/jpeg\r\n'
                              b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n'
                              b'\r\n' + 
                              frame_bytes + 
                              b'\r\n')
                    yield response
                    
                except queue.Empty:
                    # Send a small keepalive frame to prevent browser timeout
                    continue
                except Exception as e:
                    current_app.logger.error(f"Error in frame generation for {camera_id}: {e}")
                    break
        finally:
            # Clean up subscription
            distributor.unsubscribe_camera(camera_id, client_queue)


@bp.route('/camera/<camera_id>')
def camera_feed(camera_id):
    """Video streaming route for specific camera"""
    current_app.logger.info(f"Starting video feed for camera: {camera_id}")
    return Response(generate_frames_for_camera(current_app._get_current_object(), camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/camera0')
def camera0_feed():
    """Convenience route for Camera_0"""
    return camera_feed('Camera_0')


@bp.route('/camera1') 
def camera1_feed():
    """Convenience route for Camera_1"""
    return camera_feed('Camera_1')


@bp.route('/video_feed')
def video_feed():
    """Legacy route - defaults to Camera_0"""
    current_app.logger.info("Starting legacy video feed (Camera_0)")
    return camera0_feed()
