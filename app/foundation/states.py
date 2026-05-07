from enum import IntEnum

class SystemMode(IntEnum):
    STARTING_UP = 0
    STANDBY = 2
    CALIBRATION = 3
    LAUNCH_MONITOR = 4
    DIAGNOSTIC = 5
    MAX_MODE = 6
    