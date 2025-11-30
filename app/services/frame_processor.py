"""
Frame Processor Service
Handles camera frame processing, buffering, and distribution
"""

import logging
import threading
import base64
from typing import Optional, Dict, Any, List, Callable
from collections import deque
from datetime import datetime
import io

from ..messages.external.CameraFrameMsg import CameraFrameMsg


class FrameBuffer:
    """Thread-safe circular buffer for camera frames"""
    
    def __init__(self, max_size: int = 30):
        """
        Initialize frame buffer
        
        Args:
            max_size: Maximum number of frames to keep in buffer
        """
        self._buffer = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._max_size = max_size
    
    def add_frame(self, frame: CameraFrameMsg) -> None:
        """Add a frame to the buffer"""
        with self._lock:
            self._buffer.append(frame)
    
    def get_latest_frame(self) -> Optional[CameraFrameMsg]:
        """Get the most recent frame"""
        with self._lock:
            if self._buffer:
                return self._buffer[-1]
            return None
    
    def get_frame_by_number(self, frame_number: int) -> Optional[CameraFrameMsg]:
        """Get a specific frame by frame number"""
        with self._lock:
            for frame in reversed(self._buffer):
                if frame.frame_number == frame_number:
                    return frame
            return None
    
    def get_all_frames(self) -> List[CameraFrameMsg]:
        """Get all frames in buffer (oldest to newest)"""
        with self._lock:
            return list(self._buffer)
    
    def clear(self) -> None:
        """Clear all frames from buffer"""
        with self._lock:
            self._buffer.clear()
    
    def size(self) -> int:
        """Get current number of frames in buffer"""
        with self._lock:
            return len(self._buffer)


class FrameProcessor:
    """
    Service for processing camera frames from PiTrac
    Manages frame buffering, conversion, and distribution to clients
    """
    
    def __init__(self, buffer_size: int = 30):
        """
        Initialize frame processor
        
        Args:
            buffer_size: Maximum number of frames to keep in buffer
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        
        # Frame storage
        self._buffers: Dict[str, FrameBuffer] = {}  # camera_id -> buffer
        self._buffer_size = buffer_size
        self._lock = threading.Lock()
        
        # Frame subscribers (for real-time streaming)
        self._subscribers: Dict[str, List[Callable[[CameraFrameMsg], None]]] = {}
        
        # Statistics
        self._stats = {
            'total_frames': 0,
            'by_camera': {},
            'dropped_frames': 0,
            'last_frame_time': None
        }
        
        self._logger.info("FrameProcessor initialized")
    
    def process_frame(self, frame: CameraFrameMsg) -> None:
        """
        Process an incoming camera frame
        
        Args:
            frame: Camera frame message to process
        """
        camera_id = frame.camera_id
        
        # Update statistics
        self._stats['total_frames'] += 1
        self._stats['last_frame_time'] = datetime.now()
        if camera_id not in self._stats['by_camera']:
            self._stats['by_camera'][camera_id] = {
                'frames': 0,
                'last_frame_number': -1
            }
        
        camera_stats = self._stats['by_camera'][camera_id]
        camera_stats['frames'] += 1
        
        # Check for dropped frames
        if camera_stats['last_frame_number'] >= 0:
            expected = camera_stats['last_frame_number'] + 1
            if frame.frame_number > expected:
                dropped = frame.frame_number - expected
                self._stats['dropped_frames'] += dropped
                self._logger.warning(
                    f"Dropped {dropped} frames from camera {camera_id} "
                    f"(expected {expected}, got {frame.frame_number})"
                )
        
        camera_stats['last_frame_number'] = frame.frame_number
        
        # Get or create buffer for this camera
        buffer = self._get_or_create_buffer(camera_id)
        buffer.add_frame(frame)
        
        # Notify subscribers
        self._notify_subscribers(camera_id, frame)
        
        self._logger.debug(
            f"Processed frame {frame.frame_number} from {camera_id} "
            f"({len(frame.image_data)} bytes, {frame.fps:.1f} fps)"
        )
    
    def _get_or_create_buffer(self, camera_id: str) -> FrameBuffer:
        """Get or create frame buffer for a camera"""
        with self._lock:
            if camera_id not in self._buffers:
                self._buffers[camera_id] = FrameBuffer(self._buffer_size)
                self._logger.info(f"Created frame buffer for camera {camera_id}")
            return self._buffers[camera_id]
    
    def get_latest_frame(self, camera_id: str) -> Optional[CameraFrameMsg]:
        """
        Get the most recent frame for a camera
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Latest frame or None if no frames available
        """
        with self._lock:
            if camera_id in self._buffers:
                return self._buffers[camera_id].get_latest_frame()
            return None
    
    def get_frame_as_base64(self, camera_id: str) -> Optional[str]:
        """
        Get the latest frame as base64 encoded string
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Base64 encoded image data or None
        """
        frame = self.get_latest_frame(camera_id)
        if frame and frame.image_data:
            return base64.b64encode(frame.image_data).decode('utf-8')
        return None
    
    def get_frame_as_data_url(self, camera_id: str, mime_type: str = "image/jpeg") -> Optional[str]:
        """
        Get the latest frame as a data URL for HTML embedding
        
        Args:
            camera_id: Camera identifier
            mime_type: MIME type of the image
            
        Returns:
            Data URL string or None
        """
        frame = self.get_latest_frame(camera_id)
        if frame and frame.image_data:
            b64_data = base64.b64encode(frame.image_data).decode('utf-8')
            return f"data:{mime_type};base64,{b64_data}"
        return None
    
    def subscribe(self, camera_id: str, callback: Callable[[CameraFrameMsg], None]) -> None:
        """
        Subscribe to real-time frame updates for a camera
        
        Args:
            camera_id: Camera identifier
            callback: Function to call when new frame arrives
        """
        with self._lock:
            if camera_id not in self._subscribers:
                self._subscribers[camera_id] = []
            self._subscribers[camera_id].append(callback)
        
        self._logger.info(f"Added subscriber for camera {camera_id}")
    
    def unsubscribe(self, camera_id: str, callback: Callable[[CameraFrameMsg], None]) -> None:
        """
        Unsubscribe from frame updates
        
        Args:
            camera_id: Camera identifier
            callback: Previously registered callback
        """
        with self._lock:
            if camera_id in self._subscribers:
                if callback in self._subscribers[camera_id]:
                    self._subscribers[camera_id].remove(callback)
                if not self._subscribers[camera_id]:
                    del self._subscribers[camera_id]
        
        self._logger.info(f"Removed subscriber for camera {camera_id}")
    
    def _notify_subscribers(self, camera_id: str, frame: CameraFrameMsg) -> None:
        """Notify all subscribers of a new frame"""
        with self._lock:
            subscribers = self._subscribers.get(camera_id, []).copy()
        
        for callback in subscribers:
            try:
                callback(frame)
            except Exception as e:
                self._logger.error(f"Error in frame subscriber callback: {e}")
    
    def get_camera_ids(self) -> List[str]:
        """Get list of all camera IDs with buffered frames"""
        with self._lock:
            return list(self._buffers.keys())
    
    def get_buffer_size(self, camera_id: str) -> int:
        """Get number of frames buffered for a camera"""
        with self._lock:
            if camera_id in self._buffers:
                return self._buffers[camera_id].size()
            return 0
    
    def clear_buffer(self, camera_id: str) -> None:
        """Clear frame buffer for a camera"""
        with self._lock:
            if camera_id in self._buffers:
                self._buffers[camera_id].clear()
        self._logger.info(f"Cleared buffer for camera {camera_id}")
    
    def clear_all_buffers(self) -> None:
        """Clear all frame buffers"""
        with self._lock:
            for buffer in self._buffers.values():
                buffer.clear()
        self._logger.info("Cleared all frame buffers")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get frame processing statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset frame statistics"""
        self._stats = {
            'total_frames': 0,
            'by_camera': {},
            'dropped_frames': 0,
            'last_frame_time': None
        }
        self._logger.info("Statistics reset")
