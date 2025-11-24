from enum import IntEnum

class SystemMode(IntEnum):
    STARTING_UP = 0
    STANDBY = 2
    VIEWFINDER = 3
    CALIBRATION = 4
    LAUNCH_MONITOR = 5
    DIAGNOSTIC = 6
    MAX_MODE = 7