from enum import Enum
from dataclasses import dataclass
from typing import Union
import msgpack
from app.routes.messages.MessageBase import MessageBase, Message_Type  # Adjust import as needed

@dataclass
class CommandID():
    CHANGE_MODE = 0
    CALIBRATE = 1

@dataclass
class SystemMode():
    STANDBY         = 0
    VIEWFINDER      = 1
    CALIBRATION     = 2
    LAUNCH_MONITOR  = 3
    DIAGNOSTICS     = 4
    MAX_MODE        = 5

@dataclass
class StartPayload:
    start_param: int

@dataclass
class StopPayload:
    force: bool

@dataclass
class ModeChangePayload:
    mode: int

# Union of all possible payload types
CommandPayload = Union[StartPayload, StopPayload, ModeChangePayload]

class SystemCommandMsg(MessageBase):
    def __init__(self, command_id: CommandID, payload: CommandPayload):
        super().__init__(Message_Type.SYSTEM_COMMAND.value)
        self._command_id = command_id
        self._payload = payload

    def serialize(self) -> bytes:
        data = self.pack_common_fields()
        data.extend([
            self.command_id
        ])
        if isinstance(self.payload, ModeChangePayload):
            data.extend([self.payload.mode])
        elif isinstance(self.payload, StartPayload):
            data.extend([self.payload.start_param])
        elif isinstance(self.payload, StopPayload):
            data.extend([self.payload.force])
        else:
            raise ValueError("Unknown payload type")
        return msgpack.packb(data)

    @classmethod
    def deserialize(cls, data: bytes) -> 'SystemCommandMsg':
        # TODO: Implement deserialization logic later... may not be needed
        pass

    @property
    def command_id(self) -> CommandID:
        return self._command_id

    @command_id.setter
    def command_id(self, value: CommandID):
        self._command_id = value

    @property
    def payload(self) -> CommandPayload:
        return self._payload

    @payload.setter
    def payload(self, value: CommandPayload):
        self._payload = value
        
    def to_string(self) -> str:
        return f"SystemCommandMsg(command_id={self._command_id}, payload={self._payload})"
