from flask import (
    Blueprint, Flask, json, render_template, Response, request, jsonify, 
    redirect, url_for, session, current_app
)
from app.messages.message_types import MessageType
from app.messages.external.SystemCommandMsg import *
from app.messages.common.AckMessage import AckMessage
from app.config.task_names import TaskNames

bp = Blueprint('api', __name__, url_prefix='/api')


def get_pitrac():
    """Helper to get PiTrac connection from current app"""
    return current_app.pitrac_connection

def build_system_command(params):
    """Helper to build a SystemCommandMsg"""
    if not isinstance(params, dict):
        raise ValueError("Parameters must be a dictionary")
    # Initialize the system command message object
    cmdMsg = SystemCommandMsg()
    # Validate and extract the command ID from the parameters
    cmdId = CommandID.get_value(params.get('commandID', -1))
    if cmdId == -1:
        raise ValueError(f"Unknown command_id: {params.get('commandID')}")
    else:
        params.pop('commandID')
    
    # Handle specific command types based on the command ID
    if cmdId == CommandID.SetMode:
        # Get set mode action parameter
        action = SetModeAction.get_value(params.get("action"))
        if action == -1:
            raise ValueError(f"Unknown set mode action: {params.get('action', -1)}")
        else:
            params.pop("action")
    elif cmdId == CommandID.Calibrate:
        # Get calibration action parameter
        action = CalibrationAction.get_value(params.get("action", -1))
        if action == -1:
            raise ValueError(f"Unknown calibration action: {params.get('action', -1)}")
        else:
            params.pop("action")
    elif cmdId == CommandID.Configure:
        # Get configuration action parameter
        action = ConfigurationAction.get_value(params.get("action", -1))
        if action == -1:
            raise ValueError(f"Unknown configuration action: {params.get('action', -1)}")
        else:
            params.pop("action")
    else:
        raise ValueError(f"Unsupported Command ID: {cmdId}")

    # Build the command message
    cmdMsg.CommandID = cmdId
    cmdMsg.Action = action
    cmdMsg.CommandParams = {k: str(v) for k, v in params.items()}
    return cmdMsg


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
    print("Getting PiTrac status...")
    try:
        # Simple check if socket is connected
        connected = pitrac.socket is not None
        return jsonify({
            'connected': connected,
            'ip': pitrac.ip,
            'port': pitrac.port
        })
    except Exception as e:
        print(f"Error getting status: {e}")
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
        cmdMsg = SystemCommandMsg()
        cmdMsg.command_id = CommandID.SetMode
        cmdMsg.command_params = {"mode": new_mode}
        
        # Send and receive response (synchronous request-reply)
        response = pitrac.send_and_receive(cmdMsg, timeout_ms=3000)
        
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