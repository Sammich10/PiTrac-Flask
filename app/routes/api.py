from flask import (
    Blueprint, Flask, render_template, Response, request, jsonify, 
    redirect, url_for, session, current_app
)
from app.messages.message_types import MessageType
from app.messages.external.SystemCommandMsg import SystemCommandMsg, CommandID
from app.messages.common.AckMessage import AckMessage
from app.config.task_names import TaskNames

bp = Blueprint('api', __name__, url_prefix='/api')


def get_pitrac():
    """Helper to get PiTrac connection from current app"""
    return current_app.pitrac_connection

def build_system_command(params):
    """Helper to build a SystemCommandMsg"""
    
    cmd = SystemCommandMsg()
    
    if not params or "command_id" not in params:
        raise ValueError("Missing 'command_id' in parameters")
    
    command_id = params.get("command_id")
    
    if command_id == "calibrate":
        command_id = CommandID.Calibrate
    elif command_id == "set_mode":
        command_id = CommandID.SetMode
    else:
        raise ValueError(f"Unknown command_id: {command_id}")
    
    if command_id == CommandID.SetMode:
        # Set the message ID
        cmd.command_id = CommandID.SetMode
        # Extract mode parameter, ensure it exists
        if "mode" not in params:
            raise ValueError("Missing 'mode' parameter for SetMode command")
        # Set command parameters
        cmd.command_params = {"mode": params.get("mode")}
        return cmd
    elif command_id == CommandID.Calibrate:
        cmd.command_id = CommandID.Calibrate
        # Extract the camera_id parameter
        msg_params = {}
        # Find the calibration sub-command, ensure it exists
        if "command" not in params:
                raise ValueError("Missing 'command' parameter for Calibrate command")
        else:
            command = params.get("command")
            if command == "capture":
                msg_params["action"] = "capture_image"
            elif command == "process":
                msg_params["action"] = "do_distortion_cal"
            else:
                raise ValueError(f"Unknown calibration command: {command}")
        # Find the camera ID parameter, optional
        if "camera_id" in params:
            camera_id = params.get("camera_id")
            if camera_id == "Tee":
                msg_params["task_name"] = TaskNames.TEE_AGENT.value
            elif camera_id == "Flight":
                msg_params["task_name"] = TaskNames.FLIGHT_AGENT.value
            else:
                # As of now, if no camera ID is given, assume command is for both cameras
                pass
        cmd.set_command_params(msg_params)
        return cmd

    raise ValueError(f"Unsupported command_id: {command_id}")


@bp.route("/connect", methods=["POST"])
def connect():
    """Connect to PiTrac"""
    pitrac = get_pitrac()
    if pitrac.is_connected():
        pitrac.disconnect()
    connected = pitrac.connect()
    stream_connected = pitrac.connectStream()
    if connected and stream_connected:
        return jsonify({"success": True, "message": "Connected to PiTrac"})
    else:
        return jsonify({"success": False, "message": "Failed to connect to PiTrac. Control: " + str(connected) + ", Stream: " + str(stream_connected)}), 500

@bp.route("/status", methods=["GET"])
def get_status():
    """Get PiTrac connection status"""
    pitrac = get_pitrac()
    
    try:
        # Simple check if socket is connected
        connected = pitrac.socket is not None
        return jsonify({
            'connected': connected,
            'ip': pitrac.ip,
            'port': pitrac.port
        })
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 500


@bp.route("/change_mode", methods=["POST"])
def change_mode():
    """Change PiTrac system mode"""
    pitrac = get_pitrac()
    
    if not pitrac.is_connected():
        return jsonify({"error": "Not connected to PiTrac"}), 503
    
    new_mode = request.json.get("mode")
    if not new_mode:
        return jsonify({"error": "Mode is required"}), 400
    
    # Validate mode (adjust these based on your actual modes)
    valid_modes = ["standby", "viewfinder", "calibration", "launch_monitor", "diagnostic", "tracking"]
    if new_mode not in valid_modes:
        return jsonify({"error": f"Invalid mode. Must be one of: {', '.join(valid_modes)}"}), 400
    
    try:
        # Create command
        cmd = SystemCommandMsg()
        cmd.command_id = CommandID.SetMode
        cmd.command_params = {"mode": new_mode}
        
        # Send and receive response (synchronous request-reply)
        response = pitrac.send_and_receive(cmd, timeout_ms=3000)
        
        if response:
            return jsonify({
                "success": True,
                "message": "Mode changed successfully",
                "mode": new_mode,
                "response_type": response.__class__.__name__
            })
        else:
            return jsonify({
                "success": False,
                "error": "No response from PiTrac (timeout)"
            }), 504
        
    except Exception as e:
        current_app.logger.error(f"Error changing mode: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/send_command", methods=["POST"])
def send_command():
    """
    Send a custom system command to PiTrac
    
    JSON body:
    {
        "command_id": 0,  # 0=SetMode, 1=Calibrate
        "params": {"key": "value"}
    }
    """
    pitrac = get_pitrac()
    
    if not pitrac.is_connected():
        return jsonify({"error": "Not connected to PiTrac"}), 503
    
    data = request.json
    command_msg = None
    try:
        command_msg = build_system_command(data)
    except ValueError as ve:
        current_app.logger.error(f"Error building command message: {ve}")
        return jsonify({"error": str(ve)}), 400
    if command_msg is None:
        return jsonify({"error": "Unknown error creating command message"}), 400
    
    current_app.logger.info("Received command data: %s", command_msg.__str__())    
    try:
        # Send and receive response
        response = pitrac.send_and_receive(command_msg, timeout_ms=3000)
        
        if response:
            return jsonify({
                "success": True,
                "message": "Command sent",
                "response_type": response.__class__.__name__
            })
        else:
            current_app.logger.error("No response received from PiTrac for command")
            return jsonify({
                "success": False,
                "error": "No response from PiTrac (timeout)"
            }), 504
            
    except Exception as e:
        current_app.logger.error(f"Error sending command: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500