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
    
    Configure = 2
    
    GetData = 3
    
    
    @classmethod
    def get_name(cls, value: int) -> str:
        """Get enum name from value"""
        mapping = {
            
            0: "SetMode",
            
            1: "Calibrate",
            
            2: "Configure",
            
            3: "GetData",
            
        }
        return mapping.get(value, f"Unknown({value})")
        
    @classmethod
    def get_value(cls, name: str) -> int:
        """Get enum value from name"""
        mapping = {
            
            "SetMode": 0,
            
            "Calibrate": 1,
            
            "Configure": 2,
            
            "GetData": 3,
            
        }
        return mapping.get(name, -1)


class SetModeAction:
    """Available set mode actions"""
    
    EnterStandby = 0
    
    EnterCalibration = 1
    
    EnterLaunchMonitorMode = 2
    
    EnterDiagnosticMode = 3
    
    
    @classmethod
    def get_name(cls, value: int) -> str:
        """Get enum name from value"""
        mapping = {
            
            0: "EnterStandby",
            
            1: "EnterCalibration",
            
            2: "EnterLaunchMonitorMode",
            
            3: "EnterDiagnosticMode",
            
        }
        return mapping.get(value, f"Unknown({value})")
        
    @classmethod
    def get_value(cls, name: str) -> int:
        """Get enum value from name"""
        mapping = {
            
            "EnterStandby": 0,
            
            "EnterCalibration": 1,
            
            "EnterLaunchMonitorMode": 2,
            
            "EnterDiagnosticMode": 3,
            
        }
        return mapping.get(name, -1)


class CalibrationAction:
    """Available calibration actions"""
    
    SelectModel = 0
    
    SetBoardDimensions = 1
    
    CaptureFrame = 2
    
    AcceptFrame = 3
    
    RejectFrame = 4
    
    PerformDistortionCalibration = 5
    
    PerformStereoCalibration = 6
    
    
    @classmethod
    def get_name(cls, value: int) -> str:
        """Get enum name from value"""
        mapping = {
            
            0: "SelectModel",
            
            1: "SetBoardDimensions",
            
            2: "CaptureFrame",
            
            3: "AcceptFrame",
            
            4: "RejectFrame",
            
            5: "PerformDistortionCalibration",
            
            6: "PerformStereoCalibration",
            
        }
        return mapping.get(value, f"Unknown({value})")
        
    @classmethod
    def get_value(cls, name: str) -> int:
        """Get enum value from name"""
        mapping = {
            
            "SelectModel": 0,
            
            "SetBoardDimensions": 1,
            
            "CaptureFrame": 2,
            
            "AcceptFrame": 3,
            
            "RejectFrame": 4,
            
            "PerformDistortionCalibration": 5,
            
            "PerformStereoCalibration": 6,
            
        }
        return mapping.get(name, -1)


class ConfigurationAction:
    """Available configuration actions"""
    
    SetExposure = 0
    
    SetGain = 1
    
    SetFOV = 2
    
    SetCameraParams = 3
    
    ToggleViewfinder = 4
    
    
    @classmethod
    def get_name(cls, value: int) -> str:
        """Get enum name from value"""
        mapping = {
            
            0: "SetExposure",
            
            1: "SetGain",
            
            2: "SetFOV",
            
            3: "SetCameraParams",
            
            4: "ToggleViewfinder",
            
        }
        return mapping.get(value, f"Unknown({value})")
        
    @classmethod
    def get_value(cls, name: str) -> int:
        """Get enum value from name"""
        mapping = {
            
            "SetExposure": 0,
            
            "SetGain": 1,
            
            "SetFOV": 2,
            
            "SetCameraParams": 3,
            
            "ToggleViewfinder": 4,
            
        }
        return mapping.get(name, -1)



@dataclass
class SystemCommandMsg(MessageBase):
    """System command message for controlling application modes and operations"""
    
    # Fields
    
    CommandID: int = 0  # Command identifier (0=SetMode, 1=Calibrate, 2=Configure)
    
    Action: int = 0  # Action identifier corresponding to the command (e.g., CalibrationAction or ConfigurationAction)
    
    CommandParams: Dict[str, str] = field(default_factory=dict)  # Additional command parameters for future extensibility
    
    
    def __post_init__(self):
        """Initialize parent class after dataclass initialization"""
        super().__init__()
    
    def get_message_type(self) -> MessageType:
        """Get the message type for this message"""
        return MessageType.SystemCommand
    
    def _get_fields_data(self) -> List[Any]:
        """Get field values as list for serialization (matching C++ field order)"""
        return [
            
            self.CommandID,
            
            self.Action,
            
            self.CommandParams,
            
        ]
    
    def _set_fields_data(self, fields_data: List[Any]) -> None:
        """Set field values from list during deserialization"""
        if len(fields_data) != 3:
            raise ValueError(f"Expected 3 fields, got {len(fields_data)}")
        
        
        self.CommandID = fields_data[0]
        
        self.Action = fields_data[1]
        
        self.CommandParams = fields_data[2]
        
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemCommandMsg':
        """Create instance from dictionary"""
        kwargs = {}
        
        if 'CommandID' in data:
            
            kwargs['CommandID'] = data['CommandID']
            
        
        if 'Action' in data:
            
            kwargs['Action'] = data['Action']
            
        
        if 'CommandParams' in data:
            
            kwargs['CommandParams'] = data['CommandParams']
            
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        
        
        result['CommandID'] = self.CommandID
        
        
        
        result['Action'] = self.Action
        
        
        
        result['CommandParams'] = self.CommandParams
        
        
        return result
    
    # Field accessors (mirroring C++ style)
    
    def get_CommandID(self) -> int:
        """Get CommandID"""
        return self.CommandID
    
    def set_CommandID(self, value: int) -> None:
        """Set CommandID"""
        self.CommandID = value
    
    
    def get_Action(self) -> int:
        """Get Action"""
        return self.Action
    
    def set_Action(self, value: int) -> None:
        """Set Action"""
        self.Action = value
    
    
    def get_CommandParams(self) -> Dict[str, str]:
        """Get CommandParams"""
        return self.CommandParams
    
    def set_CommandParams(self, value: Dict[str, str]) -> None:
        """Set CommandParams"""
        self.CommandParams = value
    
    
    
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