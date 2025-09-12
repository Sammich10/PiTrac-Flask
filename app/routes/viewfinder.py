from flask import(
    Blueprint, Flask, render_template, Response, request, jsonify, redirect, url_for, session
)
import zmq
import msgpack
import threading
import cv2
import numpy as np
import time
import os

bp = Blueprint('viewfinder', __name__, url_prefix='/viewfinder')

latest_images = [None, None]  # Store latest frames for each camera
PI_IP = "192.168.86.22"

# For now redirect to viewfinder
@bp.route("/")
def viewfinder():
    return render_template("viewfinder/viewfinder.html")

@bp.route("/stream/<int:cam_index>")
def stream(cam_index):
    def generate():
        while True:
            if latest_images[cam_index] is not None:
                ret, jpeg = cv2.imencode('.jpg', latest_images[cam_index])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    

def zmq_receiver(cam_index, zmq_url):
    print("Starting ZMQ receiver for camera", cam_index)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(zmq_url)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    while True:
        msg_bytes = socket.recv()
        # print(f"Received frame from camera {cam_index}, size: {len(msg_bytes)} bytes")
        frame_data = parse_frame_msg(msg_bytes)
        latest_images[cam_index] = frame_data["frame"]

def parse_frame_msg(msg_bytes):
    # Unpack the msgpack message
    unpacked = msgpack.unpackb(msg_bytes, raw=False)
    # unpacked is a list of 7 elements
    (
        message_type,
        timestamp_ms,
        camera_id,
        frame_number,
        capture_timestamp_ms,
        fps,
        encoded_frame
    ) = unpacked
    
    # Convert encoded_frame (list of ints) to bytes
    jpg_bytes = bytes(encoded_frame)
    # Decode JPEG to numpy array
    img_array = np.frombuffer(jpg_bytes, dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # Return metadata and frame
    return {
        "message_type": message_type,
        "timestamp_ms": timestamp_ms,
        "camera_id": camera_id,
        "frame_number": frame_number,
        "capture_timestamp_ms": capture_timestamp_ms,
        "fps": fps,
        "frame": frame
    }

# Start ZMQ receiver threads for each camera
threading.Thread(target=zmq_receiver, args=(0, f"tcp://{PI_IP}:5555"), daemon=True).start()
threading.Thread(target=zmq_receiver, args=(1, f"tcp://{PI_IP}:5556"), daemon=True).start()
# Replace <PI_IP> with your Pi's IP address in the above URLs
