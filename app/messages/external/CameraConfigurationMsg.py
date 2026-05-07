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
class CameraConfigurationMsg(MessageBase):
    """Camera configuration details including settings and capabilities"""
    
    # Fields
    
    camera_id: int = 0  # Unique camera identifier
    
    resolution_width: int = 0  # Camera resolution width in pixels
    
    resolution_height: int = 0  # Camera resolution height in pixels
    
    frame_rate: float = 0.0  # Camera frame rate in frames per second
    
    exposure_time_us: int = 0  # Camera exposure time in microseconds
    
    analog_gain: float = 0.0  # Camera analog gain value
    
    fov_scale: float = 0.0  # Camera field of view scale factor
    
    
    def __post_init__(self):
        """Initialize parent class after dataclass initialization"""
        super().__init__()
    
    def get_message_type(self) -> MessageType:
        """Get the message type for this message"""
        return MessageType.CameraConfiguration
    
    def _get_fields_data(self) -> List[Any]:
        """Get field values as list for serialization (matching C++ field order)"""
        return [
            
            self.camera_id,
            
            self.resolution_width,
            
            self.resolution_height,
            
            self.frame_rate,
            
            self.exposure_time_us,
            
            self.analog_gain,
            
            self.fov_scale,
            
        ]
    
    def _set_fields_data(self, fields_data: List[Any]) -> None:
        """Set field values from list during deserialization"""
        if len(fields_data) != 7:
            raise ValueError(f"Expected 7 fields, got {len(fields_data)}")
        
        
        self.camera_id = fields_data[0]
        
        self.resolution_width = fields_data[1]
        
        self.resolution_height = fields_data[2]
        
        self.frame_rate = fields_data[3]
        
        self.exposure_time_us = fields_data[4]
        
        self.analog_gain = fields_data[5]
        
        self.fov_scale = fields_data[6]
        
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraConfigurationMsg':
        """Create instance from dictionary"""
        kwargs = {}
        
        if 'camera_id' in data:
            
            kwargs['camera_id'] = data['camera_id']
            
        
        if 'resolution_width' in data:
            
            kwargs['resolution_width'] = data['resolution_width']
            
        
        if 'resolution_height' in data:
            
            kwargs['resolution_height'] = data['resolution_height']
            
        
        if 'frame_rate' in data:
            
            kwargs['frame_rate'] = data['frame_rate']
            
        
        if 'exposure_time_us' in data:
            
            kwargs['exposure_time_us'] = data['exposure_time_us']
            
        
        if 'analog_gain' in data:
            
            kwargs['analog_gain'] = data['analog_gain']
            
        
        if 'fov_scale' in data:
            
            kwargs['fov_scale'] = data['fov_scale']
            
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        
        
        result['camera_id'] = self.camera_id
        
        
        
        result['resolution_width'] = self.resolution_width
        
        
        
        result['resolution_height'] = self.resolution_height
        
        
        
        result['frame_rate'] = self.frame_rate
        
        
        
        result['exposure_time_us'] = self.exposure_time_us
        
        
        
        result['analog_gain'] = self.analog_gain
        
        
        
        result['fov_scale'] = self.fov_scale
        
        
        return result
    
    # Field accessors (mirroring C++ style)
    
    def get_camera_id(self) -> int:
        """Get camera_id"""
        return self.camera_id
    
    def set_camera_id(self, value: int) -> None:
        """Set camera_id"""
        self.camera_id = value
    
    
    def get_resolution_width(self) -> int:
        """Get resolution_width"""
        return self.resolution_width
    
    def set_resolution_width(self, value: int) -> None:
        """Set resolution_width"""
        self.resolution_width = value
    
    
    def get_resolution_height(self) -> int:
        """Get resolution_height"""
        return self.resolution_height
    
    def set_resolution_height(self, value: int) -> None:
        """Set resolution_height"""
        self.resolution_height = value
    
    
    def get_frame_rate(self) -> float:
        """Get frame_rate"""
        return self.frame_rate
    
    def set_frame_rate(self, value: float) -> None:
        """Set frame_rate"""
        self.frame_rate = value
    
    
    def get_exposure_time_us(self) -> int:
        """Get exposure_time_us"""
        return self.exposure_time_us
    
    def set_exposure_time_us(self, value: int) -> None:
        """Set exposure_time_us"""
        self.exposure_time_us = value
    
    
    def get_analog_gain(self) -> float:
        """Get analog_gain"""
        return self.analog_gain
    
    def set_analog_gain(self, value: float) -> None:
        """Set analog_gain"""
        self.analog_gain = value
    
    
    def get_fov_scale(self) -> float:
        """Get fov_scale"""
        return self.fov_scale
    
    def set_fov_scale(self, value: float) -> None:
        """Set fov_scale"""
        self.fov_scale = value
    
    
    
    @classmethod
    def from_msgpack(cls, data: bytes) -> 'CameraConfigurationMsg':
        """Deserialize from msgpack"""
        instance = cls()
        instance.deserialize(data)
        return instance
    
    def to_msgpack(self) -> bytes:
        """Serialize to msgpack"""
        return self.serialize()
    
    def __str__(self) -> str:
        return f"CameraConfigurationMsg({', '.join(f'{k}={v}' for k, v in self.to_dict().items())})"