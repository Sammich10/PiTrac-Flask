import zmq
import msgpack
import cv2
import numpy as np
import threading

from app.routes.messages.Common import ZMQ_CONTEXT
from app.routes.messages.Frame import CameraFrameMessage

latest_images = [None, None]  # Store latest frames for each camera
stop_event = threading.Event()

def zmq_receiver(cam_index, zmq_url):
    global latest_images, stop_event
    print("Starting ZMQ receiver for camera", cam_index)
    socket = ZMQ_CONTEXT.socket(zmq.SUB)
    socket.connect(zmq_url)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    while not stop_event.is_set():
        msg_bytes = socket.recv()
        # print(f"Received frame from camera {cam_index}, size: {len(msg_bytes)} bytes")
        frameMessage = CameraFrameMessage.deserialize(msg_bytes)
        frameData = frameMessage.getFrameData()
        if frameData is not None:
            latest_images[cam_index] = frameData["frame"]
            # print(f"Updated latest image for camera {cam_index}")
        else:
            print(f"Failed to parse frame message for camera {cam_index}")
    print("ZMQ receiver for camera", cam_index, "stopped.")
    # Clear latest image on stop
    latest_images[cam_index] = None
    socket.close()
