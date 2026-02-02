"""
Task Names Configuration - Synchronized with C++ TaskNames.h
This file provides the same task names used in the C++ application
to ensure consistent targeting of commands between Flask and C++.
"""

from enum import Enum
from typing import List, Optional

class TaskNames(Enum):
    """Task names that match the C++ TaskNames enum"""
    SYSTEM_MANAGER = "SystemManager"
    FLIGHT_AGENT = "FlightAgent"  
    TEE_AGENT = "TeeAgent"

class TaskNameUtils:
    """Utility functions for task name validation and conversion"""
    
    @staticmethod
    def get_all_task_names() -> List[str]:
        """Get all valid task names as strings"""
        return [task.value for task in TaskNames]
    
    @staticmethod
    def is_valid_task_name(task_name: str) -> bool:
        """Check if a task name is valid"""
        return task_name in TaskNameUtils.get_all_task_names()
    
    @staticmethod
    def from_string(task_name: str) -> Optional[TaskNames]:
        """Convert string to TaskNames enum, return None if invalid"""
        for task in TaskNames:
            if task.value == task_name:
                return task
        return None

# For easier imports
SYSTEM_MANAGER = TaskNames.SYSTEM_MANAGER.value
FLIGHT_AGENT = TaskNames.FLIGHT_AGENT.value
TEE_AGENT = TaskNames.TEE_AGENT.value