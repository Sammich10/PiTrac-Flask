"""
PiTrac Message Types
Auto-generated message type enumeration from schemas
Mirrors the C++ Message_Type enum
"""

from enum import IntEnum

class MessageType(IntEnum):
    """Message type enumeration matching C++ Message_Type"""
    # Common Messages (0-99) - Shared between internal and external systems
    AckMessage = 0

    # Internal Messages (100-199) - Process-to-process communication only
    ChangeMode = 100
    Heartbeat = 101
    RegisterTask = 102

    # External Messages (200-299) - Communication with host/Flask app
    CameraFrame = 200
    SystemCommand = 201
    TaskStatus = 202

    @classmethod
    def get_category(cls, msg_type: 'MessageType') -> str:
        """Get the category (Common/Internal/External) for a message type"""
        if 0 <= msg_type.value <= 99:
            return "Common"
        elif 100 <= msg_type.value <= 199:
            return "Internal"
        elif 200 <= msg_type.value <= 299:
            return "External"
        else:
            return "Unknown"
    
    @classmethod
    def is_external(cls, msg_type: 'MessageType') -> bool:
        """Check if message type is external (for Flask communication)"""
        return 200 <= msg_type.value <= 299
    
    @classmethod
    def is_internal(cls, msg_type: 'MessageType') -> bool:
        """Check if message type is internal (process-to-process only)"""
        return 100 <= msg_type.value <= 199
    
    @classmethod
    def is_common(cls, msg_type: 'MessageType') -> bool:
        """Check if message type is common (shared)"""
        return 0 <= msg_type.value <= 99


# Message type lookup dictionary for convenience
MESSAGE_TYPE_INFO = {
    MessageType.AckMessage: {
        'category': 'Common',
        'description': 'Acknowledgment message that contains the original message data for confirmation',
        'file': 'AckMessage.json'
    },
    MessageType.ChangeMode: {
        'category': 'Internal',
        'description': 'Internal message to request system mode changes',
        'file': 'ChangeModeMsg.json'
    },
    MessageType.Heartbeat: {
        'category': 'Internal',
        'description': 'Internal heartbeat message for monitoring agent health and status',
        'file': 'HeartbeatMsg.json'
    },
    MessageType.RegisterTask: {
        'category': 'Internal',
        'description': 'Internal message for registering tasks with the system manager',
        'file': 'RegisterTaskMsg.json'
    },
    MessageType.CameraFrame: {
        'category': 'External',
        'description': 'Camera frame data with encoded image and metadata',
        'file': 'CameraFrameMsg.json'
    },
    MessageType.SystemCommand: {
        'category': 'External',
        'description': 'System command message for controlling application modes and operations',
        'file': 'SystemCommandMsg.json'
    },
    MessageType.TaskStatus: {
        'category': 'External',
        'description': 'Status update for a running task',
        'file': 'TaskStatusMsg.json'
    },
}
