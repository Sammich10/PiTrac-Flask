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




class AckStatus:
    """Acknowledgment status codes"""
    
    Success = 0
    
    Failure = 1
    
    Invalid = 2
    
    Timeout = 3
    
    Retry = 4
    
    Partial = 5
    
    
    @classmethod
    def get_name(cls, value: int) -> str:
        """Get enum name from value"""
        mapping = {
            
            0: "Success",
            
            1: "Failure",
            
            2: "Invalid",
            
            3: "Timeout",
            
            4: "Retry",
            
            5: "Partial",
            
        }
        return mapping.get(value, f"Unknown({value})")



@dataclass
class AckMessage(MessageBase):
    """Acknowledgment message that contains the original message data for confirmation"""
    
    # Fields
    
    ack_status: int = 0  # Acknowledgment status (0=Success, 1=Failure, 2=Invalid, 3=Timeout)
    
    original_message_type: int = 0  # Type of the original message being acknowledged
    
    original_timestamp: int = 0  # Timestamp of the original message in microseconds since epoch
    
    
    def __post_init__(self):
        """Initialize parent class after dataclass initialization"""
        super().__init__()
    
    def get_message_type(self) -> MessageType:
        """Get the message type for this message"""
        return MessageType.AckMessage
    
    def _get_fields_data(self) -> List[Any]:
        """Get field values as list for serialization (matching C++ field order)"""
        return [
            
            self.ack_status,
            
            self.original_message_type,
            
            self.original_timestamp,
            
        ]
    
    def _set_fields_data(self, fields_data: List[Any]) -> None:
        """Set field values from list during deserialization"""
        if len(fields_data) != 3:
            raise ValueError(f"Expected 3 fields, got {len(fields_data)}")
        
        
        self.ack_status = fields_data[0]
        
        self.original_message_type = fields_data[1]
        
        self.original_timestamp = fields_data[2]
        
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AckMessage':
        """Create instance from dictionary"""
        kwargs = {}
        
        if 'ack_status' in data:
            
            kwargs['ack_status'] = data['ack_status']
            
        
        if 'original_message_type' in data:
            
            kwargs['original_message_type'] = data['original_message_type']
            
        
        if 'original_timestamp' in data:
            
            kwargs['original_timestamp'] = data['original_timestamp']
            
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        
        
        result['ack_status'] = self.ack_status
        
        
        
        result['original_message_type'] = self.original_message_type
        
        
        
        result['original_timestamp'] = self.original_timestamp
        
        
        return result
    
    # Field accessors (mirroring C++ style)
    
    def get_ack_status(self) -> int:
        """Get ack_status"""
        return self.ack_status
    
    def set_ack_status(self, value: int) -> None:
        """Set ack_status"""
        self.ack_status = value
    
    
    def get_original_message_type(self) -> int:
        """Get original_message_type"""
        return self.original_message_type
    
    def set_original_message_type(self, value: int) -> None:
        """Set original_message_type"""
        self.original_message_type = value
    
    
    def get_original_timestamp(self) -> int:
        """Get original_timestamp"""
        return self.original_timestamp
    
    def set_original_timestamp(self, value: int) -> None:
        """Set original_timestamp"""
        self.original_timestamp = value
    
    
    
    @classmethod
    def from_msgpack(cls, data: bytes) -> 'AckMessage':
        """Deserialize from msgpack"""
        instance = cls()
        instance.deserialize(data)
        return instance
    
    def to_msgpack(self) -> bytes:
        """Serialize to msgpack"""
        return self.serialize()
    
    def __str__(self) -> str:
        return f"AckMessage({', '.join(f'{k}={v}' for k, v in self.to_dict().items())})"