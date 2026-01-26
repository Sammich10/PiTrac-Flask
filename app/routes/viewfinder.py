from flask import (
    Blueprint, Flask, render_template, Response, request, jsonify, 
    redirect, url_for, session, current_app
)
import cv2
import numpy as np
import base64
import time

bp = Blueprint('viewfinder', __name__, url_prefix='/viewfinder')


def get_pitrac():
    """Helper to get PiTrac connection from current app"""
    return current_app.pitrac_connection


@bp.route("/")
def viewfinder():
    """Render viewfinder page"""
    return render_template("viewfinder/viewfinder.html")


@bp.route("/debug")
def debug_stream():
    """Render debug stream page"""
    return render_template("debug_stream.html")


@bp.route("/frame/latest", methods=["GET"])
def get_latest_frame():
    """Get latest camera frame as JSON (placeholder)"""
    # Note: The simple PiTracConnection doesn't have frame buffering
    # You would need to implement frame receiving separately
    # or use the full PiTracManager with FrameProcessor
    
    return jsonify({
        'success': False,
        'error': 'Frame receiving not implemented in simple connection',
        'hint': 'Use PiTracManager with FrameProcessor for frame handling'
    }), 501


@bp.route("/frame/data_url", methods=["GET"])
def get_frame_data_url():
    """Get latest frame as data URL (placeholder)"""
    return jsonify({
        'success': False,
        'error': 'Frame receiving not implemented in simple connection',
        'hint': 'Use PiTracManager with FrameProcessor for frame handling'
    }), 501


@bp.route("/stream/<camera_id>")
def stream(camera_id):
    """
    Stream camera frames (placeholder)
    
    Note: The simple PiTracConnection uses REQ/REP pattern which is synchronous.
    For streaming frames, you need:
    1. PiTrac to send frames via SUB/PUB or PUSH/PULL
    2. Use the full PiTracManager with FrameProcessor
    """
    return jsonify({
        'error': 'Streaming not implemented in simple connection',
        'hint': 'Use PiTracManager with FrameProcessor for frame streaming'
    }), 501


@bp.route("/stop_stream", methods=["POST"])
def stop_stream():
    """Stop streaming (placeholder for compatibility)"""
    # With the new architecture, streams are stateless
    # Each request gets the latest frame
    return '', 204

