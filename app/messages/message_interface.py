"""
PiTrac Python Message Interface
Abstract base class for all PiTrac messages with ZMQ messaging capabilities
Mirrors the C++ MessageInterface and MessageBase implementation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, Type, List
from datetime import datetime
import msgpack
import json
import logging
import time
from enum import IntEnum
import zmq    
import msgpack
import json
import logging
import time
from enum import IntEnum

class SocketType(IntEnum):
    """ZMQ Socket types matching C++ SocketType"""
    Publisher = 0
    Subscriber = 1
    Router = 2
    Dealer = 3
    Request = 4
    Reply = 5

class MessageInterface(ABC):
    """
    Abstract interface for all PiTrac messages
    Mirrors the C++ MessageInterface class
    """
    
    def __init__(self):
        self._timestamp: Optional[datetime] = None
    
    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def get_message_type(self) -> MessageType:
        """Get the message type"""
        pass
    
    def get_timestamp(self) -> Optional[datetime]:
        """Get message timestamp"""
        return self._timestamp
    
    def set_timestamp(self, timestamp: Optional[datetime] = None):
        """Set message timestamp (defaults to current time)"""
        self._timestamp = timestamp or datetime.now()
    
    # Serialization interface - to be implemented by MessageBase
    @abstractmethod
    def serialize(self) -> bytes:
        """Serialize message to msgpack bytes"""
        pass
    
    @abstractmethod
    def deserialize(self, data: bytes) -> None:
        """Deserialize message from msgpack bytes"""
        pass
    
    # ZMQ message operations
    def to_zmq_message(self) -> bytes:
        """Convert to ZMQ message data"""
        return self.serialize()
    
    def from_zmq_message(self, data: bytes) -> None:
        """Populate from ZMQ message data"""
        self.deserialize(data)
    
    # Convenience methods
    @abstractmethod
    def to_string(self) -> str:
        """String representation of the message"""
        pass
    
    @abstractmethod
    def clone(self) -> 'MessageInterface':
        """Create a copy of this message"""
        pass


class MessageBase(MessageInterface):
    """
    Base implementation for all PiTrac messages
    Mirrors the C++ MessageBase class
    """
    
    def __init__(self):
        super().__init__()
        self._timestamp = datetime.now()
    
    def serialize(self) -> bytes:
        """Serialize message to msgpack bytes using array format like C++"""
        # Pack as array: [type, timestamp_ms, field1, field2, ...]
        fields_data = self._get_fields_data()
        
        # Convert timestamp to milliseconds since epoch
        timestamp_ms = int(self._timestamp.timestamp() * 1000) if self._timestamp else 0
        
        # Create array with common fields + message fields
        array_data = [
            int(self.get_message_type()),  # Message type
            timestamp_ms,                   # Timestamp in milliseconds
        ] + fields_data
        
        return msgpack.packb(array_data, use_bin_type=True)
    
    def deserialize(self, data: bytes) -> None:
        """Deserialize message from msgpack bytes"""
        try:
            unpacked = msgpack.unpackb(data, raw=False)
            
            if not isinstance(unpacked, list) or len(unpacked) < 2:
                raise ValueError("Invalid message format: expected array with at least 2 elements")
            
            # Extract and validate message type
            msg_type = unpacked[0]
            if msg_type != int(self.get_message_type()):
                raise ValueError(self._incorrect_message_type_string(msg_type))
            
            # Extract timestamp
            timestamp_ms = unpacked[1]
            self._timestamp = datetime.fromtimestamp(timestamp_ms / 1000.0)
            
            # Extract field data (skip type and timestamp)
            fields_data = unpacked[2:]
            self._set_fields_data(fields_data)
            
        except Exception as e:
            raise ValueError(f"Failed to deserialize {self.__class__.__name__}: {e}")
    
    def to_string(self) -> str:
        """String representation of the message"""
        timestamp_str = self._timestamp.isoformat() if self._timestamp else "None"
        return f"Message Type: {self.get_message_type().name}, Timestamp: {timestamp_str}"
    
    def clone(self) -> 'MessageBase':
        """Create a copy of this message"""
        data = self.serialize()
        new_instance = self.__class__()
        new_instance.deserialize(data)
        return new_instance
    
    # Abstract methods for field management
    @abstractmethod
    def _get_fields_data(self) -> List[Any]:
        """Get field values as list for serialization"""
        pass
    
    @abstractmethod
    def _set_fields_data(self, fields_data: List[Any]) -> None:
        """Set field values from list during deserialization"""
        pass
    
    # Helper methods
    def _incorrect_message_type_string(self, incorrect_type: int) -> str:
        """Generate error message for type mismatch"""
        return f"Message type mismatch: expected {int(self.get_message_type())}, got {incorrect_type}"
    
    # Convenience serialization methods
    def to_json(self) -> str:
        """Convert message to JSON string"""
        data = {
            '_message_type': int(self.get_message_type()),
            '_timestamp': self._timestamp.isoformat() if self._timestamp else None,
        }
        # Add field data as dictionary
        field_dict = self.to_dict()
        data.update(field_dict)
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MessageBase':
        """Create message from JSON string"""
        data = json.loads(json_str)
        
        # Extract timestamp if present
        timestamp = None
        if '_timestamp' in data:
            timestamp = datetime.fromisoformat(data['_timestamp'])
            del data['_timestamp']
        
        # Remove message type
        if '_message_type' in data:
            del data['_message_type']
        
        # Create instance and set timestamp
        instance = cls.from_dict(data)
        if timestamp:
            instance.set_timestamp(timestamp)
        return instance
    
    # Abstract methods for dict conversion
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        pass
    
    @classmethod
    @abstractmethod 
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageBase':
        """Create message from dictionary"""
        pass
    
    def __str__(self) -> str:
        """String representation of the message"""
        return f"{self.__class__.__name__}({self.get_message_type().name}): {self.to_dict()}"


class ZMQMessenger:
    """
    ZMQ messaging utility for sending and receiving PiTrac messages
    """
    
    def __init__(self, context: Optional[zmq.Context] = None):
        self._context = context or zmq.Context()
        self._sockets: Dict[str, zmq.Socket] = {}
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def create_socket(self, name: str, socket_type: SocketType, timeout_ms: int = 5000) -> zmq.Socket:
        """Create a new ZMQ socket"""
        zmq_socket_types = {
            SocketType.Publisher: zmq.PUB,
            SocketType.Subscriber: zmq.SUB,
            SocketType.Router: zmq.ROUTER,
            SocketType.Dealer: zmq.DEALER,
            SocketType.Request: zmq.REQ,
            SocketType.Reply: zmq.REP
        }
        
        if socket_type not in zmq_socket_types:
            raise ValueError(f"Invalid socket type: {socket_type}")
        
        socket = self._context.socket(zmq_socket_types[socket_type])
        socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
        socket.setsockopt(zmq.SNDTIMEO, timeout_ms)
        
        self._sockets[name] = socket
        self._logger.info(f"Created {socket_type.name} socket '{name}' with {timeout_ms}ms timeout")
        return socket
    
    def get_socket(self, name: str) -> Optional[zmq.Socket]:
        """Get existing socket by name"""
        return self._sockets.get(name)
    
    def bind(self, socket_name: str, endpoint: str):
        """Bind socket to endpoint"""
        socket = self._sockets.get(socket_name)
        if not socket:
            raise ValueError(f"Socket '{socket_name}' not found")
        
        socket.bind(endpoint)
        self._logger.info(f"Socket '{socket_name}' bound to {endpoint}")
    
    def connect(self, socket_name: str, endpoint: str):
        """Connect socket to endpoint"""
        socket = self._sockets.get(socket_name)
        if not socket:
            raise ValueError(f"Socket '{socket_name}' not found")
        
        socket.connect(endpoint)
        self._logger.info(f"Socket '{socket_name}' connected to {endpoint}")
    
    def subscribe(self, socket_name: str, topic: str = ""):
        """Subscribe to topic (for SUB sockets)"""
        socket = self._sockets.get(socket_name)
        if not socket:
            raise ValueError(f"Socket '{socket_name}' not found")
        
        socket.setsockopt(zmq.SUBSCRIBE, topic.encode('utf-8'))
        self._logger.info(f"Socket '{socket_name}' subscribed to topic '{topic}'")
    
    def send_message(self, socket_name: str, message: MessageInterface, topic: str = "") -> bool:
        """Send a message through the specified socket"""
        socket = self._sockets.get(socket_name)
        if not socket:
            raise ValueError(f"Socket '{socket_name}' not found")
        
        try:
            # Set timestamp if not already set
            if message.get_timestamp() is None:
                message.set_timestamp()
            
            # Serialize message
            data = message.serialize()
            
            # Send with topic if specified (for PUB sockets)
            if topic:
                socket.send_multipart([topic.encode('utf-8'), data], zmq.NOBLOCK)
            else:
                socket.send(data, zmq.NOBLOCK)
            
            self._logger.debug(f"Sent {message.__class__.__name__} via '{socket_name}'")
            return True
            
        except zmq.Again:
            self._logger.warning(f"Send timeout on socket '{socket_name}'")
            return False
        except Exception as e:
            self._logger.error(f"Failed to send message via '{socket_name}': {e}")
            return False
    
    def receive_message(self, socket_name: str, message_class: Type[MessageInterface]) -> Optional[MessageInterface]:
        """Receive a message of the specified type"""
        socket = self._sockets.get(socket_name)
        if not socket:
            raise ValueError(f"Socket '{socket_name}' not found")
        
        try:
            # Check if this is a multipart message (with topic)
            if socket.getsockopt(zmq.RCVMORE):
                parts = socket.recv_multipart(zmq.NOBLOCK)
                if len(parts) >= 2:
                    data = parts[1]  # Second part is the message data
                else:
                    data = parts[0]
            else:
                data = socket.recv(zmq.NOBLOCK)
            
            # Create and deserialize message
            message = message_class()
            message.deserialize(data)
            
            self._logger.debug(f"Received {message_class.__name__} via '{socket_name}'")
            return message
            
        except zmq.Again:
            # No message available (timeout)
            return None
        except Exception as e:
            self._logger.error(f"Failed to receive message via '{socket_name}': {e}")
            return None
    
    def close_socket(self, name: str):
        """Close and remove socket"""
        if name in self._sockets:
            self._sockets[name].close()
            del self._sockets[name]
            self._logger.info(f"Closed socket '{name}'")
    
    def close_all(self):
        """Close all sockets and context"""
        for name in list(self._sockets.keys()):
            self.close_socket(name)
        self._context.term()
        self._logger.info("Closed all sockets and ZMQ context")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.close_all()
        except:
            pass


# Convenience function to create a messenger instance
def create_messenger(context: Optional[zmq.Context] = None) -> ZMQMessenger:
    """Create a new ZMQ messenger instance"""
    return ZMQMessenger(context)
