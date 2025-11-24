from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import msgpack
import json
from datetime import datetime
try:
    from ..message_interface import MessageBase
    from ..message_types import MessageType
except ImportError:
    from ..message_interface import MessageBase, MessageType




class CommandID:
    """Available system commands"""
    
    SetMode = 0
    
    Calibrate = 1
    
    
    @classmethod
    def get_name(cls, value: int) -> str:
        """Get enum name from value"""
        mapping = {
            
            0: "SetMode",
            
            1: "Calibrate",
            
        }
        return mapping.get(value, f"Unknown({value})")



@dataclass
class SystemCommandMsg(MessageBase):
    """System command message for controlling application modes and operations"""
    
    # Fields
    
    command_id: int = 0  # Command identifier (0=SetMode, 1=Calibrate)
    
    command_params: Dict[str, str] = field(default_factory=dict)  # Additional command parameters for future extensibility
    
    
    def __post_init__(self):
        """Initialize parent class after dataclass initialization"""
        super().__init__()
    
    def get_message_type(self) -> MessageType:
        """Get the message type for this message"""
        return MessageType.SystemCommand
    
    def _get_fields_data(self) -> List[Any]:
        """Get field values as list for serialization (matching C++ field order)"""
        return [
            
            self.command_id,
            
            self.command_params,
            
        ]
    
    def _set_fields_data(self, fields_data: List[Any]) -> None:
        """Set field values from list during deserialization"""
        if len(fields_data) != 2:
            raise ValueError(f"Expected 2 fields, got {len(fields_data)}")
        
        
        self.command_id = fields_data[0]
        
        self.command_params = fields_data[1]
        
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemCommandMsg':
        """Create instance from dictionary"""
        kwargs = {}
        
        if 'command_id' in data:
            
            kwargs['command_id'] = data['command_id']
            
        
        if 'command_params' in data:
            
            kwargs['command_params'] = data['command_params']
            
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        
        
        result['command_id'] = self.command_id
        
        
        
        result['command_params'] = self.command_params
        
        
        return result
    
    # Field accessors (mirroring C++ style)
    
    def get_command_id(self) -> int:
        """Get command_id"""
        return self.command_id
    
    def set_command_id(self, value: int) -> None:
        """Set command_id"""
        self.command_id = value
    
    
    def get_command_params(self) -> Dict[str, str]:
        """Get command_params"""
        return self.command_params
    
    def set_command_params(self, value: Dict[str, str]) -> None:
        """Set command_params"""
        self.command_params = value
    
    
    
    @classmethod
    def from_msgpack(cls, data: bytes) -> 'SystemCommandMsg':
        """Deserialize from msgpack"""
        instance = cls()
        instance.deserialize(data)
        return instance
    
    def to_msgpack(self) -> bytes:
        """Serialize to msgpack"""
        return self.serialize()
    
    def __str__(self) -> str:
        return f"SystemCommandMsg({', '.join(f'{k}={v}' for k, v in self.to_dict().items())})"