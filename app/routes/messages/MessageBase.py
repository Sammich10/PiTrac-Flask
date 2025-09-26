import abc
import enum
import msgpack
import time
from datetime import datetime, timezone, timedelta

class Message_Type(enum.Enum):
    CAMERA_FRAME        = 0
    CAMERA_FRAME_RAW    = 1
    SYSTEM_COMMAND      = 6
    ACK_MESSAGE         = 7


class MessageInterface(abc.ABC):
    @abc.abstractmethod
    def get_message_type(self):
        pass

    @abc.abstractmethod
    def get_timestamp(self):
        pass

    @abc.abstractmethod
    def set_timestamp(self, timestamp):
        pass

    @abc.abstractmethod
    def to_zmq_message(self):
        pass

    @abc.abstractmethod
    def from_zmq_message(self, msg):
        pass

    @abc.abstractmethod
    def to_string(self):
        pass

class MessageBase(MessageInterface):
    def __init__(self, msg_type: int):
        self.message_type = msg_type
        self.timestamp = datetime.now(timezone.utc)

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
        
    def get_message_type(self):
        return self.message_type

    def to_zmq_message(self):
        # Serialize to msgpack buffer
        buffer = self.serialize()
        return buffer  # For pyzmq, you can send this as bytes

    def from_zmq_message(self, msg):
        # msg is expected to be bytes
        self.deserialize(msg)

    @abc.abstractmethod
    def to_string(self):
        pass

    def pack_common_fields(self):
        # Returns a tuple of (message_type, timestamp_ms)
        timestamp_ms = int(time.time() * 1000)
        return [int(self.get_message_type()), timestamp_ms]

    @abc.abstractmethod
    def serialize(self):
        pass
        
    @abc.abstractmethod
    def deserialize(self, data):
        pass
