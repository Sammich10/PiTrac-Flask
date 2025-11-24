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


@dataclass
class CameraFrameMsg(MessageBase):
    """Camera frame data with encoded image and metadata"""
    
    # Fields
    
    camera_id: str = ""  # Unique camera identifier
    
    frame_number: int = 0  # Sequential frame number
    
    capture_timestamp: int = 0  # Capture time in microseconds since epoch
    
    fps: float = 0.0  # Frames per second
    
    image_data: bytes = b''  # Encoded image data (JPEG/PNG/etc)
    
    metadata: Dict[str, str] = field(default_factory=dict)  # Additional frame metadata (codec, quality, etc)
    
    
    def __post_init__(self):
        """Initialize parent class after dataclass initialization"""
        super().__init__()
    
    def get_message_type(self) -> MessageType:
        """Get the message type for this message"""
        return MessageType.CameraFrame
    
    def _get_fields_data(self) -> List[Any]:
        """Get field values as list for serialization (matching C++ field order)"""
        return [
            
            self.camera_id,
            
            self.frame_number,
            
            self.capture_timestamp,
            
            self.fps,
            
            self.image_data,
            
            self.metadata,
            
        ]
    
    def _set_fields_data(self, fields_data: List[Any]) -> None:
        """Set field values from list during deserialization"""
        if len(fields_data) != 6:
            raise ValueError(f"Expected 6 fields, got {len(fields_data)}")
        
        
        self.camera_id = fields_data[0]
        
        self.frame_number = fields_data[1]
        
        self.capture_timestamp = fields_data[2]
        
        self.fps = fields_data[3]
        
        self.image_data = fields_data[4]
        
        self.metadata = fields_data[5]
        
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraFrameMsg':
        """Create instance from dictionary"""
        kwargs = {}
        
        if 'camera_id' in data:
            
            kwargs['camera_id'] = data['camera_id']
            
        
        if 'frame_number' in data:
            
            kwargs['frame_number'] = data['frame_number']
            
        
        if 'capture_timestamp' in data:
            
            kwargs['capture_timestamp'] = data['capture_timestamp']
            
        
        if 'fps' in data:
            
            kwargs['fps'] = data['fps']
            
        
        if 'image_data' in data:
            
            # Handle binary data
            if isinstance(data['image_data'], str):
                kwargs['image_data'] = data['image_data'].encode('utf-8')
            else:
                kwargs['image_data'] = data['image_data']
            
        
        if 'metadata' in data:
            
            kwargs['metadata'] = data['metadata']
            
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        
        
        result['camera_id'] = self.camera_id
        
        
        
        result['frame_number'] = self.frame_number
        
        
        
        result['capture_timestamp'] = self.capture_timestamp
        
        
        
        result['fps'] = self.fps
        
        
        
        # Handle binary data
        if isinstance(self.image_data, bytes):
            import base64
            result['image_data'] = base64.b64encode(self.image_data).decode('utf-8')
        else:
            result['image_data'] = self.image_data
        
        
        
        result['metadata'] = self.metadata
        
        
        return result
    
    # Field accessors (mirroring C++ style)
    
    def get_camera_id(self) -> str:
        """Get camera_id"""
        return self.camera_id
    
    def set_camera_id(self, value: str) -> None:
        """Set camera_id"""
        self.camera_id = value
    
    
    def get_frame_number(self) -> int:
        """Get frame_number"""
        return self.frame_number
    
    def set_frame_number(self, value: int) -> None:
        """Set frame_number"""
        self.frame_number = value
    
    
    def get_capture_timestamp(self) -> int:
        """Get capture_timestamp"""
        return self.capture_timestamp
    
    def set_capture_timestamp(self, value: int) -> None:
        """Set capture_timestamp"""
        self.capture_timestamp = value
    
    
    def get_fps(self) -> float:
        """Get fps"""
        return self.fps
    
    def set_fps(self, value: float) -> None:
        """Set fps"""
        self.fps = value
    
    
    def get_image_data(self) -> bytes:
        """Get image_data"""
        return self.image_data
    
    def set_image_data(self, value: bytes) -> None:
        """Set image_data"""
        self.image_data = value
    
    
    def get_metadata(self) -> Dict[str, str]:
        """Get metadata"""
        return self.metadata
    
    def set_metadata(self, value: Dict[str, str]) -> None:
        """Set metadata"""
        self.metadata = value
    
    
    
    @classmethod
    def from_msgpack(cls, data: bytes) -> 'CameraFrameMsg':
        """Deserialize from msgpack"""
        instance = cls()
        instance.deserialize(data)
        return instance
    
    def to_msgpack(self) -> bytes:
        """Serialize to msgpack"""
        return self.serialize()
    
    def __str__(self) -> str:
        return f"CameraFrameMsg({', '.join(f'{k}={v}' for k, v in self.to_dict().items())})"