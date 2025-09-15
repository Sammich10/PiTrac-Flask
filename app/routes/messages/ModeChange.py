import msgpack
from app.routes.messages.Common import CHANGE_MODE
import time

STANDBY         = 0
VIEWFINDER      = 1
CALIBRATION     = 2
LAUNCH_MONITOR  = 3
DIAGNOSTICS     = 4
MAX_MODE        = 5

def make_mode_change_msg(new_mode):
    if new_mode < 0 or new_mode >= MAX_MODE:
        return None
    # Get current timestamp in milliseconds
    timestamp_ms = int(time.time() * 1000)
    # Create a mode change message
    message = (
        CHANGE_MODE,
        timestamp_ms,
        new_mode
    )
    # Serialize the message using msgpack
    packed_msg = msgpack.packb(message, use_bin_type=True)
    return packed_msg