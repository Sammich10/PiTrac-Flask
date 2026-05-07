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
import json
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
        
        # Camera-specific latest frames for clients
        # Structure: {camera_id: {"frame_data": bytes, "metadata": dict}}
        self.latest_frames = {}
        self.lock = threading.Lock()
        
        # SSE clients for real-time updates
        # Structure: {camera_id: [callback1, callback2, ...]}
        self.sse_clients = defaultdict(list)
        
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
    
    def subscribe_camera(self, camera_id, callback=None):
        """Subscribe to frames from a specific camera"""
        if callback:
            with self.lock:
                self.sse_clients[camera_id].append(callback)
        return True
    
    def unsubscribe_camera(self, camera_id, callback=None):
        """Unsubscribe from camera frames"""
        if callback:
            with self.lock:
                if camera_id in self.sse_clients:
                    try:
                        self.sse_clients[camera_id].remove(callback)
                        if not self.sse_clients[camera_id]:
                            del self.sse_clients[camera_id]
                    except ValueError:
                        pass
    
    def get_latest_frame(self, camera_id):
        """Get the latest frame for a camera"""
        with self.lock:
            return self.latest_frames.get(camera_id)
    
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
                        # frame_bytes = self._process_frame(frame_msg)
                        frame_data = self._extract_frame_data(frame_msg)
                        if frame_data is not None:
                            # Distribute to subscribers
                            self._distribute_frame(frame_msg.camera_id, frame_data)
                            
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
    
    def _extract_frame_data(self, frame_msg):
        """Extract raw frame data and metadata"""
        try:
            if not isinstance(frame_msg, CameraFrameMsg):
                raise ValueError("Invalid frame data type")
            
            # Process image data to ensure it's streamable
            image_data = frame_msg.image_data
            if isinstance(image_data, bytes) and len(image_data) > 0:
                # Check if it's already JPEG
                if image_data[:2] != b'\xff\xd8':
                    # Try to decode and re-encode as JPEG
                    try:
                        nparr = np.frombuffer(image_data, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if frame is not None:
                            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            image_data = buffer.tobytes()
                    except:
                        return None
                
                frame_data = {
                    "image_data": image_data,
                    "metadata": {
                        "camera_id": frame_msg.camera_id,
                        "frame_number": frame_msg.frame_number,
                        "timestamp": frame_msg.capture_timestamp,
                        "fps": frame_msg.fps,
                        "exposure": frame_msg.metadata.get("ExposureTime", None),
                        "fov_scale": frame_msg.metadata.get("FOVScale", None),
                        "gain": frame_msg.metadata.get("AnalogGain", None)
                    }
                }
                return frame_data
            
            return None
            
        except Exception as e:
            print(f"Frame data extraction error: {e}")
            return None
    
    def _distribute_frame(self, camera_id, frame_data):
        """Distribute frame to all subscribers of this camera"""
        with self.lock:
            # Store latest frame
            self.latest_frames[camera_id] = frame_data
            
            # Immediately call all SSE callbacks for this camera
            if camera_id in self.sse_clients:
                for callback in self.sse_clients[camera_id][:]:
                    try:
                        callback(frame_data)
                    except Exception as e:
                        print(f"SSE callback error: {e}")
                        # Remove broken callback
                        self.sse_clients[camera_id].remove(callback)


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
        
        # Get latest frame immediately if available
        latest_frame_data = distributor.get_latest_frame(camera_id)
        if latest_frame_data and latest_frame_data.get("image_data"):
            frame_bytes = latest_frame_data["image_data"]
            response = (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n'
                      b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n'
                      b'\r\n' + 
                      frame_bytes + 
                      b'\r\n')
            yield response
        
        # For streaming, we'll still use the old event system but simplified
        import threading
        client_event = threading.Event()
        frame_buffer = {"data": None}
        
        def frame_callback(frame_data):
            frame_buffer["data"] = frame_data
            client_event.set()
        
        distributor.subscribe_camera(camera_id, frame_callback)
        
        try:
            while True:
                try:
                    if client_event.wait(timeout=1.0):
                        client_event.clear()
                        frame_data = frame_buffer["data"]
                        if frame_data and frame_data.get("image_data"):
                            frame_bytes = frame_data["image_data"]
                            response = (b'--frame\r\n'
                                      b'Content-Type: image/jpeg\r\n'
                                      b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n'
                                      b'\r\n' + 
                                      frame_bytes + 
                                      b'\r\n')
                            yield response
                    else:
                        continue
                        
                except Exception as e:
                    current_app.logger.error(f"Error in frame generation for {camera_id}: {e}")
                    break
        finally:
            distributor.unsubscribe_camera(camera_id, frame_callback)


def generate_sse_stream(app, camera_id):
    """Generator for Server-Sent Events stream with frame data and metadata"""
    with app.app_context():
        distributor = get_frame_distributor()
        
        # Send initial frame if available
        latest_frame_data = distributor.get_latest_frame(camera_id)
        if latest_frame_data:
            image_b64 = base64.b64encode(latest_frame_data["image_data"]).decode('utf-8')
            data = {
                "image": f"data:image/jpeg;base64,{image_b64}",
                "metadata": latest_frame_data["metadata"]
            }
            yield f"data: {json.dumps(data)}\n\n"
        
        # Setup callback for new frames
        import queue
        frame_queue = queue.Queue(maxsize=1)
        
        def frame_callback(frame_data):
            try:
                # Clear queue and add new frame (no buffering)
                while not frame_queue.empty():
                    try:
                        frame_queue.get_nowait()
                    except queue.Empty:
                        break
                frame_queue.put_nowait(frame_data)
            except queue.Full:
                pass  # Skip if can't add immediately
        
        distributor.subscribe_camera(camera_id, frame_callback)
        
        try:
            while True:
                try:
                    frame_data = frame_queue.get(timeout=1.0)
                    if frame_data and frame_data.get("image_data"):
                        image_b64 = base64.b64encode(frame_data["image_data"]).decode('utf-8')
                        data = {
                            "image": f"data:image/jpeg;base64,{image_b64}",
                            "metadata": frame_data["metadata"]
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                except queue.Empty:
                    # Send keepalive
                    yield f"data: {json.dumps({'keepalive': True})}\n\n"
                except Exception as e:
                    current_app.logger.error(f"SSE error for {camera_id}: {e}")
                    break
        finally:
            distributor.unsubscribe_camera(camera_id, frame_callback)


@bp.route('/camera/<camera_id>')
def camera_feed(camera_id):
    """Video streaming route for specific camera"""
    current_app.logger.info(f"Starting video feed for camera: {camera_id}")
    return Response(generate_frames_for_camera(current_app._get_current_object(), camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/sse/<camera_id>')
def camera_sse_feed(camera_id):
    """Server-Sent Events stream for specific camera with metadata"""
    current_app.logger.info(f"Starting SSE feed for camera: {camera_id}")
    return Response(generate_sse_stream(current_app._get_current_object(), camera_id),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Access-Control-Allow-Origin': '*'
                    })


@bp.route('/camera0')
def camera0_feed():
    """Convenience route for Camera_0"""
    return camera_feed('Camera_0')


@bp.route('/camera1') 
def camera1_feed():
    """Convenience route for Camera_1"""
    return camera_feed('Camera_1')


@bp.route('/sse/camera0')
def camera0_sse_feed():
    """SSE route for Camera_0"""
    return camera_sse_feed('Camera_0')


@bp.route('/sse/camera1')
def camera1_sse_feed():
    """SSE route for Camera_1"""
    return camera_sse_feed('Camera_1')


@bp.route('/video_feed')
def video_feed():
    """Legacy route - defaults to Camera_0"""
    current_app.logger.info("Starting legacy video feed (Camera_0)")
    return camera0_feed()
