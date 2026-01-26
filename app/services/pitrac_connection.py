"""
PiTrac Connection Service
Simple synchronous request-reply connection to PiTrac system
"""

import logging
from typing import Optional, Dict, Any
import zmq

from ..messages.message_interface import MessageInterface
from ..messages.message_types import MessageType


class PiTracConnection:
    """
    Simple synchronous connection to PiTrac system using REQ/REP pattern. This connection is used
    primarily for sending system commands and receiving acknowledgments or response messages.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize connection manager"""
        self._logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration
        self._config = config or {}
        self.hostname = self._config.get('hostname') or self._config.get('IP', 'localhost')
        self.port = self._config.get('port', 8080)
        self.stream_port = self._config.get('stream_port', 8081)
        
        # ZMQ context and socket
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self.framesocket : Optional[zmq.Socket] = None
        
        # Connection state
        self._connected = False
        self._stream_connected = False
        
        # Timeout settings (milliseconds)
        self.send_timeout = 5000  # 5 seconds
        self.recv_timeout = 5000  # 5 seconds
    
    def connect(self) -> bool:
        """Establish connection to PiTrac"""
        if self._connected:
            self._logger.warning("Already connected")
            return True
        
        self._logger.info(f"Connecting to PiTrac at {self.hostname}:{self.port}")
        
        try:
            # Create ZMQ context and REQ socket
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            
            # Set timeouts
            self.socket.setsockopt(zmq.SNDTIMEO, self.send_timeout)
            self.socket.setsockopt(zmq.RCVTIMEO, self.recv_timeout)
            self.socket.setsockopt(zmq.LINGER, 0)
            
            # Connect to PiTrac
            endpoint = f"tcp://{self.hostname}:{self.port}"
            self.socket.connect(endpoint)
            
            self._connected = True
            self._logger.info(f"Successfully connected to PiTrac at {endpoint}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to connect to PiTrac: {e}")
            self._cleanup()
            return False
        
    def connectStream(self) -> bool:
        """Establish frame stream connection to PiTrac"""
        if not self._connected:
            if not self.connect():
                return False
        
        if self.framesocket:
            self._logger.warning("Already connected to frame stream")
            return True
        
        self._logger.info("Connecting to PiTrac frame stream")
        
        try:
            self.framesocket = self.context.socket(zmq.SUB)
            endpoint = f"tcp://*:{self.port+1}"
            self.framesocket.bind(endpoint)
            self.framesocket.setsockopt_string(zmq.SUBSCRIBE, "")
            
        except Exception as e:
            self._logger.error(f"Failed to connect to PiTrac frame stream: {e}")
            self._cleanup()
            return False
        
        self._logger.info(f"Connecting to PiTrac frame stream at {self.hostname}:{self.stream_port}")
        
        try:
            # Create ZMQ context and REQ socket
            self.context = zmq.Context()
            self.framesocket = self.context.socket(zmq.SUB)
            
            # Set timeouts
            self.framesocket.setsockopt(zmq.SNDTIMEO, self.send_timeout)
            self.framesocket.setsockopt(zmq.RCVTIMEO, self.recv_timeout)
            self.framesocket.setsockopt(zmq.LINGER, 0)
            self.framesocket.setsockopt_string(zmq.SUBSCRIBE, "")
            
            # Connect to PiTrac
            endpoint = f"tcp://{self.hostname}:{self.stream_port}"
            self.framesocket.connect(endpoint)
            
            self._stream_connected = True
            self._logger.info(f"Successfully connected to PiTrac frame stream at {endpoint}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to connect to PiTrac frame stream: {e}")
            self._cleanup()
            return False
    
    def disconnect(self) -> None:
        """Disconnect from PiTrac"""
        if not self._connected:
            return
        
        self._logger.info("Disconnecting from PiTrac")
        self._cleanup()
        self._connected = False
        self._stream_connected = False
        self._logger.info("Disconnected from PiTrac")
    
    def _cleanup(self) -> None:
        """Cleanup resources"""
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                self._logger.error(f"Error closing socket: {e}")
            self.socket = None
            self._connected = False
            
        if self.framesocket:
            try:
                self.framesocket.close()
            except Exception as e:
                self._logger.error(f"Error closing frame socket: {e}")
            self.framesocket = None
            self._stream_connected = False
        
        if self.context:
            try:
                self.context.term()
            except Exception as e:
                self._logger.error(f"Error terminating context: {e}")
            self.context = None
    
    def send_message(self, message: MessageInterface) -> bool:
        """
        Send a message to PiTrac (synchronous)
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self._connected or not self.socket:
            self._logger.warning("Cannot send message - not connected")
            return False
        
        try:
            # Set timestamp if not already set
            if message.get_timestamp() is None:
                message.set_timestamp()
            
            # Serialize and send
            data = message.serialize()
            self.socket.send(data)
            
            self._logger.debug(f"Sent {message.__class__.__name__}")
            return True
            
        except zmq.Again:
            self._logger.error("Send timeout")
            return False
        except Exception as e:
            self._logger.error(f"Failed to send message: {e}")
            return False
    
    def receive_message(self, timeout_ms: Optional[int] = None) -> Optional[MessageInterface]:
        """
        Receive a message from PiTrac (synchronous)
        
        Args:
            timeout_ms: Timeout in milliseconds (uses default recv_timeout if None)
            
        Returns:
            Received message or None if timeout/error
        """
        if not self._connected or not self.socket:
            self._logger.warning("Cannot receive message - not connected")
            return None
        
        # Import message classes for deserialization
        from ..messages.external.CameraFrameMsg import CameraFrameMsg
        from ..messages.external.SystemCommandMsg import SystemCommandMsg
        from ..messages.external.TaskStatusMsg import TaskStatusMsg
        from ..messages.common.AckMessage import AckMessage
        
        # Message type to class mapping
        message_classes = {
            MessageType.CameraFrame: CameraFrameMsg,
            MessageType.SystemCommand: SystemCommandMsg,
            MessageType.TaskStatus: TaskStatusMsg,
            MessageType.AckMessage: AckMessage,
        }
        
        try:
            # Set temporary timeout if specified
            if timeout_ms is not None:
                old_timeout = self.socket.getsockopt(zmq.RCVTIMEO)
                self.socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
            
            # Receive data
            data = self.socket.recv()
            
            # Restore timeout if it was changed
            if timeout_ms is not None:
                self.socket.setsockopt(zmq.RCVTIMEO, old_timeout)
            
            # Deserialize to determine message type
            import msgpack
            unpacked = msgpack.unpackb(data, raw=False)
            
            if not isinstance(unpacked, list) or len(unpacked) < 2:
                self._logger.error("Invalid message format")
                return None
            
            msg_type_value = unpacked[0]
            
            # Find appropriate message class and deserialize
            for msg_type, msg_class in message_classes.items():
                if int(msg_type) == msg_type_value:
                    message = msg_class()
                    message.deserialize(data)
                    self._logger.debug(f"Received {message.__class__.__name__}")
                    return message
            
            self._logger.warning(f"Unknown message type: {msg_type_value}")
            return None
            
        except zmq.Again:
            self._logger.debug("Receive timeout")
            return None
        except Exception as e:
            self._logger.error(f"Error receiving message: {e}")
            return None
    
    def send_and_receive(self, message: MessageInterface, timeout_ms: Optional[int] = None) -> Optional[MessageInterface]:
        """
        Send a message and wait for response (request-reply pattern)
        
        Args:
            message: Message to send
            timeout_ms: Timeout for receive in milliseconds
            
        Returns:
            Response message or None if timeout/error
        """
        if self.send_message(message):
            return self.receive_message(timeout_ms)
        return None
    
    def is_connected(self) -> bool:
        """Check if connected to PiTrac"""
        return self._connected and self.socket is not None
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.disconnect()
        except:
            pass
