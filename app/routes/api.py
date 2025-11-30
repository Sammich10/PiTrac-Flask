from flask import (
    Blueprint, Flask, render_template, Response, request, jsonify, 
    redirect, url_for, session, current_app
)
from app.messages.message_types import MessageType
from app.messages.external.SystemCommandMsg import SystemCommandMsg, CommandID
from app.messages.common.AckMessage import AckMessage

bp = Blueprint('api', __name__, url_prefix='/api')


def get_pitrac():
    """Helper to get PiTrac connection from current app"""
    return current_app.pitrac_connection


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


@bp.route("/calibrate", methods=["POST"])
def calibrate():
    """Trigger calibration"""
    pitrac = get_pitrac()
    
    if not pitrac.is_connected():
        return jsonify({"error": "Not connected to PiTrac"}), 503
    
    try:
        # Create calibration command
        cmd = SystemCommandMsg()
        cmd.command_id = CommandID.Calibrate
        cmd.command_params = {}
        
        # Send and receive response
        response = pitrac.send_and_receive(cmd, timeout_ms=3000)
        
        if response:
            return jsonify({
                "success": True,
                "message": "Calibration command sent",
                "response_type": response.__class__.__name__
            })
        else:
            return jsonify({
                "success": False,
                "error": "No response from PiTrac (timeout)"
            }), 504
            
    except Exception as e:
        current_app.logger.error(f"Error sending calibration: {e}")
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
    command_id = data.get("command_id")
    params = data.get("params", {})
    
    if command_id is None:
        return jsonify({"error": "command_id is required"}), 400
    
    try:
        # Create command
        cmd = SystemCommandMsg()
        cmd.command_id = command_id
        cmd.command_params = params
        
        # Send and receive response
        response = pitrac.send_and_receive(cmd, timeout_ms=3000)
        
        if response:
            return jsonify({
                "success": True,
                "message": "Command sent",
                "response_type": response.__class__.__name__
            })
        else:
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