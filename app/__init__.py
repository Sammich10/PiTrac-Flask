import zmq
import threading
import cv2
import numpy as np
from flask import Flask, render_template, Blueprint, Response
import time
import os

BASE_DIR=os.path.dirname(os.path.abspath(__file__))

def create_app():
    from .routes import viewfinder
    app=Flask(__name__)
    app.register_blueprint(viewfinder.bp)
    return app