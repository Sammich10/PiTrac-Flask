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
    
    original_message_data: bytes = b''  # Serialized data of the original message
    
    original_timestamp: int = 0  # Timestamp of the original message in microseconds since epoch
    
    ack_timestamp: int = 0  # Timestamp when acknowledgment was created
    
    error_message: str = ""  # Error description if status is Failure or Invalid
    
    metadata: Dict[str, str] = field(default_factory=dict)  # Additional acknowledgment metadata
    
    
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
            
            self.original_message_data,
            
            self.original_timestamp,
            
            self.ack_timestamp,
            
            self.error_message,
            
            self.metadata,
            
        ]
    
    def _set_fields_data(self, fields_data: List[Any]) -> None:
        """Set field values from list during deserialization"""
        if len(fields_data) != 7:
            raise ValueError(f"Expected 7 fields, got {len(fields_data)}")
        
        
        self.ack_status = fields_data[0]
        
        self.original_message_type = fields_data[1]
        
        self.original_message_data = fields_data[2]
        
        self.original_timestamp = fields_data[3]
        
        self.ack_timestamp = fields_data[4]
        
        self.error_message = fields_data[5]
        
        self.metadata = fields_data[6]
        
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AckMessage':
        """Create instance from dictionary"""
        kwargs = {}
        
        if 'ack_status' in data:
            
            kwargs['ack_status'] = data['ack_status']
            
        
        if 'original_message_type' in data:
            
            kwargs['original_message_type'] = data['original_message_type']
            
        
        if 'original_message_data' in data:
            
            # Handle binary data
            if isinstance(data['original_message_data'], str):
                kwargs['original_message_data'] = data['original_message_data'].encode('utf-8')
            else:
                kwargs['original_message_data'] = data['original_message_data']
            
        
        if 'original_timestamp' in data:
            
            kwargs['original_timestamp'] = data['original_timestamp']
            
        
        if 'ack_timestamp' in data:
            
            kwargs['ack_timestamp'] = data['ack_timestamp']
            
        
        if 'error_message' in data:
            
            kwargs['error_message'] = data['error_message']
            
        
        if 'metadata' in data:
            
            kwargs['metadata'] = data['metadata']
            
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        
        
        result['ack_status'] = self.ack_status
        
        
        
        result['original_message_type'] = self.original_message_type
        
        
        
        # Handle binary data
        if isinstance(self.original_message_data, bytes):
            import base64
            result['original_message_data'] = base64.b64encode(self.original_message_data).decode('utf-8')
        else:
            result['original_message_data'] = self.original_message_data
        
        
        
        result['original_timestamp'] = self.original_timestamp
        
        
        
        result['ack_timestamp'] = self.ack_timestamp
        
        
        
        result['error_message'] = self.error_message
        
        
        
        result['metadata'] = self.metadata
        
        
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
    
    
    def get_original_message_data(self) -> bytes:
        """Get original_message_data"""
        return self.original_message_data
    
    def set_original_message_data(self, value: bytes) -> None:
        """Set original_message_data"""
        self.original_message_data = value
    
    
    def get_original_timestamp(self) -> int:
        """Get original_timestamp"""
        return self.original_timestamp
    
    def set_original_timestamp(self, value: int) -> None:
        """Set original_timestamp"""
        self.original_timestamp = value
    
    
    def get_ack_timestamp(self) -> int:
        """Get ack_timestamp"""
        return self.ack_timestamp
    
    def set_ack_timestamp(self, value: int) -> None:
        """Set ack_timestamp"""
        self.ack_timestamp = value
    
    
    def get_error_message(self) -> str:
        """Get error_message"""
        return self.error_message
    
    def set_error_message(self, value: str) -> None:
        """Set error_message"""
        self.error_message = value
    
    
    def get_metadata(self) -> Dict[str, str]:
        """Get metadata"""
        return self.metadata
    
    def set_metadata(self, value: Dict[str, str]) -> None:
        """Set metadata"""
        self.metadata = value
    
    
    
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