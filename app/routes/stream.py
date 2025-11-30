from flask import (
    Blueprint, Flask, render_template, Response, request, jsonify, 
    redirect, url_for, session, current_app
)
import cv2
import numpy as np
import base64
import time

bp = Blueprint('stream', __name__, url_prefix='/stream')


def get_pitrac():
    """Helper to get PiTrac connection from current app"""
    return current_app.pitrac_connection

