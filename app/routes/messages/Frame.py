import zmq
import msgpack
import cv2
import numpy as np
import threading

from app.routes.messages.Common import ZMQ_CONTEXT

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
        frame_data = parse_frame_msg(msg_bytes)
        latest_images[cam_index] = frame_data["frame"]
    print("ZMQ receiver for camera", cam_index, "stopped.")
    socket.close()

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
