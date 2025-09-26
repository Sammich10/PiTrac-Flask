import msgpack
import numpy as np
import cv2
from datetime import datetime, timezone

from .MessageBase import MessageBase
from .MessageBase import Message_Type

class CameraFrameMessage(MessageBase):
    def __init__(self, camera_id, frame_number, capture_timestamp_ms, fps, frame, timestamp=None):
        super().__init__()
        self.message_type = Message_Type.CAMERA_FRAME.value
        self.camera_id = camera_id
        self.frame_number = frame_number
        self.capture_timestamp_ms = capture_timestamp_ms
        self.fps = fps
        self.frame = frame  # numpy array (BGR image)
        if timestamp is not None:
            self.timestamp = timestamp

    def serialize(self):
        # Encode frame as JPEG
        ret, jpg = cv2.imencode('.jpg', self.frame)
        if not ret:
            raise ValueError("Failed to encode frame as JPEG")
        encoded_frame = jpg.tobytes()
        # Pack as list, matching parse_frame_msg
        data = self.pack_common_fields()
        data.extend([
            self.camera_id,
            self.frame_number,
            self.capture_timestamp_ms,
            self.fps,
            list(encoded_frame)
        ])
        return msgpack.packb(data)

    @classmethod
    def deserialize(cls, msg_bytes):
        unpacked = msgpack.unpackb(msg_bytes, raw=False)
        # Unpack message fields
        (
            message_type,
            timestamp_ms,
            camera_id,
            frame_number,
            capture_timestamp_ms,
            fps,
            encoded_frame
        ) = unpacked
        # Decode JPEG to numpy array
        jpg_bytes = bytes(encoded_frame)
        img_array = np.frombuffer(jpg_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        obj = CameraFrameMessage(camera_id, frame_number, capture_timestamp_ms, fps, frame, timestamp)
        obj.message_type = message_type
        return obj
    
    def get_message_type(self):
        return self.message_type

    def set_message_type(self, message_type):
        self.message_type = message_type

    def get_camera_id(self):
        return self.camera_id

    def set_camera_id(self, camera_id):
        self.camera_id = camera_id

    def get_frame_number(self):
        return self.frame_number

    def set_frame_number(self, frame_number):
        self.frame_number = frame_number

    def get_capture_timestamp_ms(self):
        return self.capture_timestamp_ms

    def set_capture_timestamp_ms(self, capture_timestamp_ms):
        self.capture_timestamp_ms = capture_timestamp_ms

    def get_fps(self):
        return self.fps

    def set_fps(self, fps):
        self.fps = fps

    def get_frame(self):
        return self.frame

    def set_frame(self, frame):
        self.frame = frame

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def getFrameData(self):
        return {
            "message_type": self.message_type,
            "timestamp_ms": int(self.timestamp.timestamp() * 1000),
            "camera_id": self.camera_id,
            "frame_number": self.frame_number,
            "capture_timestamp_ms": self.capture_timestamp_ms,
            "fps": self.fps,
            "frame": self.frame
        }
    

