from dataclasses import dataclass
import datetime
from time import timezone
import msgpack
from app.routes.messages.MessageBase import MessageBase, Message_Type, MessageInterface
from app.routes.messages import SystemCommand, Frame

@dataclass
class Status:
    Success = 0
    Failure = 1
    InvalidCommand = 2
    Timeout = 3
    
class AckMessage(MessageBase):
    def __init__(self, original_message_type : int, original_message_timestamp : int, status: int):
        super().__init__(Message_Type.ACK_MESSAGE.value)
        self.original_message_type = original_message_type
        self.original_timestamp = original_message_timestamp
        self.status = status

    def serialize(self) -> bytes:
        data = self.pack_common_fields()
        data.extend([
            self.original_message_type,
            int(self.original_timestamp.timestamp()),
            self.status
        ])
        return msgpack.packb(data)

    @classmethod
    def deserialize(cls, data: bytes) -> 'AckMessage':
        unpacker = msgpack.Unpacker()
        unpacker.feed(data)
        objs = []
        for obj in unpacker:
            objs.append(obj)
            print(f"Deserialized object: {obj}")
        if len(objs) < 1:
            raise ValueError("Invalid data for AckMessage, no objects found")
        ack = objs[0]
        if len(ack) < 3:
            raise ValueError("Invalid data for AckMessage, insufficient fields")
        if len(objs) < 2:
            raise ValueError("Invalid data for AckMessage, no original message found")
        orig_msg = objs[1]
        if len(orig_msg) < 3:
            raise ValueError("Invalid data for AckMessage original message, insufficient fields")
        msg = cls(
            original_message_type=orig_msg[0],
            original_message_timestamp=orig_msg[1],
            status=ack[2]
        )
        msg.set_timestamp(ack[1])
        return msg
    
    def get_status(self):
        return self.status

    def get_original_message_type(self):
        return self.original_message_type

    def to_string(self):
        return f"AckMessage(original_type={self.original_message_type}, original_timestamp={self.original_timestamp}, status={self.status})"
    
