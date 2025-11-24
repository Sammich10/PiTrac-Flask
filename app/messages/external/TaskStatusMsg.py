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
class TaskStatusMsg(MessageBase):
    """Status update for a running task"""
    
    # Fields
    
    task_id: str = ""  # Unique task identifier
    
    status: str = ""  # Current task status (running, completed, failed, etc)
    
    progress: float = 0.0  # Task completion percentage (0.0 to 1.0)
    
    details: Dict[str, str] = field(default_factory=dict)  # Additional status details and parameters
    
    error_log: List[str] = field(default_factory=list)  # List of error messages if task failed
    
    
    def __post_init__(self):
        """Initialize parent class after dataclass initialization"""
        super().__init__()
    
    def get_message_type(self) -> MessageType:
        """Get the message type for this message"""
        return MessageType.TaskStatus
    
    def _get_fields_data(self) -> List[Any]:
        """Get field values as list for serialization (matching C++ field order)"""
        return [
            
            self.task_id,
            
            self.status,
            
            self.progress,
            
            self.details,
            
            self.error_log,
            
        ]
    
    def _set_fields_data(self, fields_data: List[Any]) -> None:
        """Set field values from list during deserialization"""
        if len(fields_data) != 5:
            raise ValueError(f"Expected 5 fields, got {len(fields_data)}")
        
        
        self.task_id = fields_data[0]
        
        self.status = fields_data[1]
        
        self.progress = fields_data[2]
        
        self.details = fields_data[3]
        
        self.error_log = fields_data[4]
        
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskStatusMsg':
        """Create instance from dictionary"""
        kwargs = {}
        
        if 'task_id' in data:
            
            kwargs['task_id'] = data['task_id']
            
        
        if 'status' in data:
            
            kwargs['status'] = data['status']
            
        
        if 'progress' in data:
            
            kwargs['progress'] = data['progress']
            
        
        if 'details' in data:
            
            kwargs['details'] = data['details']
            
        
        if 'error_log' in data:
            
            kwargs['error_log'] = data['error_log']
            
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        
        
        result['task_id'] = self.task_id
        
        
        
        result['status'] = self.status
        
        
        
        result['progress'] = self.progress
        
        
        
        result['details'] = self.details
        
        
        
        result['error_log'] = self.error_log
        
        
        return result
    
    # Field accessors (mirroring C++ style)
    
    def get_task_id(self) -> str:
        """Get task_id"""
        return self.task_id
    
    def set_task_id(self, value: str) -> None:
        """Set task_id"""
        self.task_id = value
    
    
    def get_status(self) -> str:
        """Get status"""
        return self.status
    
    def set_status(self, value: str) -> None:
        """Set status"""
        self.status = value
    
    
    def get_progress(self) -> float:
        """Get progress"""
        return self.progress
    
    def set_progress(self, value: float) -> None:
        """Set progress"""
        self.progress = value
    
    
    def get_details(self) -> Dict[str, str]:
        """Get details"""
        return self.details
    
    def set_details(self, value: Dict[str, str]) -> None:
        """Set details"""
        self.details = value
    
    
    def get_error_log(self) -> List[str]:
        """Get error_log"""
        return self.error_log
    
    def set_error_log(self, value: List[str]) -> None:
        """Set error_log"""
        self.error_log = value
    
    
    
    @classmethod
    def from_msgpack(cls, data: bytes) -> 'TaskStatusMsg':
        """Deserialize from msgpack"""
        instance = cls()
        instance.deserialize(data)
        return instance
    
    def to_msgpack(self) -> bytes:
        """Serialize to msgpack"""
        return self.serialize()
    
    def __str__(self) -> str:
        return f"TaskStatusMsg({', '.join(f'{k}={v}' for k, v in self.to_dict().items())})"