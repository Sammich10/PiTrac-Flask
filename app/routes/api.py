from flask import(
    Blueprint, Flask, render_template, Response, request, jsonify, redirect, url_for, session
)
from app.routes.messages.ModeChange import make_mode_change_msg, STANDBY, VIEWFINDER, CALIBRATION, LAUNCH_MONITOR, DIAGNOSTICS
from app.routes.messages.Common import PI_IP, ZMQ_CONTEXT
import zmq

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/change_mode", methods=["POST"])
def change_mode():
    new_mode = request.json.get("mode")
    if new_mode == "standby":
        new_mode = STANDBY
    elif new_mode == "viewfinder":
        new_mode = VIEWFINDER
    elif new_mode == "calibration":
        new_mode = CALIBRATION
    elif new_mode == "launch_monitor":
        new_mode = LAUNCH_MONITOR
    elif new_mode == "diagnostics":
        new_mode = DIAGNOSTICS
    else:
        return jsonify({"error": "Invalid mode"}), 400
    # Create and send mode change message
    packed_msg = make_mode_change_msg(new_mode)
    if packed_msg is None:
        return jsonify({"error": "Invalid mode"}), 400
    socket = ZMQ_CONTEXT.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.RCVTIMEO, 2000)  # 2 seconds timeout for recv
    socket.connect(f"tcp://{PI_IP}:6000")
    socket.send(packed_msg)
    try:
        response = socket.recv()
        return jsonify({"message": "Mode changed successfully"})
    except zmq.Again:
        return jsonify({"error": "No response from server"}), 504
    finally:
        socket.close()