from flask import(
    Blueprint, Flask, render_template, Response, request, jsonify, redirect, url_for, session
)
from app.routes.messages.SystemCommand import (
    SystemCommandMsg, CommandID, SystemMode, StartPayload, StopPayload, ModeChangePayload
)
from app.routes.messages.Ack import AckMessage, Status
from app.routes.messages.Common import PI_IP, ZMQ_CONTEXT
import zmq

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/change_mode", methods=["POST"])
def change_mode():
    new_mode = request.json.get("mode")
    if new_mode == "standby":
        new_mode = SystemMode.STANDBY
    elif new_mode == "viewfinder":
        new_mode = SystemMode.VIEWFINDER
    elif new_mode == "calibration":
        new_mode = SystemMode.CALIBRATION
    elif new_mode == "launch_monitor":
        new_mode = SystemMode.LAUNCH_MONITOR
    elif new_mode == "diagnostics":
        new_mode = SystemMode.DIAGNOSTICS
    else:
        return jsonify({"error": "Invalid mode"}), 400
    # Create and send mode change message
    cmd = SystemCommandMsg(CommandID.CHANGE_MODE, ModeChangePayload(new_mode))
    msg = cmd.serialize()
    if msg is None:
        return jsonify({"error": "Invalid mode"}), 400
    socket = ZMQ_CONTEXT.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.RCVTIMEO, 2000)  # 2 seconds timeout for recv
    socket.connect(f"tcp://{PI_IP}:6000")
    socket.send(msg)
    try:
        response = socket.recv()
        ack = AckMessage.deserialize(response)
        if ack.get_status() == Status.Success:
            return jsonify({"message": "Mode changed successfully"})
        else:
            return jsonify({"error": "Failed to change mode", "status": ack.get_status()}), 400
    except zmq.Again:
        return jsonify({"error": "No response from server"}), 504
    finally:
        socket.close()