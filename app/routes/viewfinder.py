from flask import(
    Blueprint, Flask, render_template, Response, request, jsonify, redirect, url_for, session
)
import threading
import cv2
import numpy as np
import time
import os

from app.routes.messages.Frame import zmq_receiver, latest_images, stop_event
from app.routes.messages.Common import PI_IP

bp = Blueprint('viewfinder', __name__, url_prefix='/viewfinder')

stream_1_receiver_thread = threading.Thread(target=zmq_receiver, args=(0, f"tcp://{PI_IP}:5555"), daemon=False)
stream_2_receiver_thread = threading.Thread(target=zmq_receiver, args=(1, f"tcp://{PI_IP}:5556"), daemon=False)

# For now redirect to viewfinder
@bp.route("/")
def viewfinder():
    if not stream_1_receiver_thread.is_alive():
         stream_1_receiver_thread.start()
    if not stream_2_receiver_thread.is_alive():
         stream_2_receiver_thread.start()
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
            else:
                # If no image yet, send a blank frame or wait
                blank_image = np.zeros((480, 640, 3), dtype=np.uint8)
                ret, jpeg = cv2.imencode('.jpg', blank_image)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(0.1)  # Adjust frame rate as needed
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
@bp.route("/stop_stream", methods=["POST"])
def stop_stream():
    stop_event.set()
    return '', 204

# Start ZMQ receiver threads for each camera

# Replace <PI_IP> with your Pi's IP address in the above URLs
