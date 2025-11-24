from flask import(
    Blueprint, Flask, render_template, Response, request, jsonify, redirect, url_for, session
)
from app.messages.message_types import MessageType
from app.messages.external import (
    SystemCommandMsg
)
from app.messages.common import AckMessage
from app import SystemMode
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
    elif new_mode == "diagnostic":
        new_mode = SystemMode.DIAGNOSTIC
    else:
        return jsonify({"error": "Invalid mode"}), 400
    # Create and send mode change message
    cmd = SystemCommandMsg(MessageType.ChangeMode, {"mode": new_mode})
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