from flask import Flask, render_template, Blueprint, Response
import time
import os
import logging
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_app():
    """Create and configure Flask application"""
    from .routes import viewfinder, api, stream
    from .services.pitrac_connection import PiTracConnection
    
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config_path = os.path.join(BASE_DIR, 'config', 'app.json')
    with open(config_path) as f:
        app.config['PITRAC_CONFIG'] = json.load(f)
    
    pitrac_config = app.config['PITRAC_CONFIG']['Network']['PiTrac']
    flask_config = app.config['PITRAC_CONFIG']['Network']['Flask']
    
    # Initialize PiTrac connection
    pitrac = PiTracConnection(
        pitrac_config
    )
    
    # Store in app context for routes to access
    app.pitrac_connection = pitrac
    
    # Connect to PiTrac immediately
    # try:
    #     pitrac.connect()
    #     app.logger.info("PiTrac connection established successfully")
    #     pitrac.connectStream()
    #     app.logger.info("PiTrac frame stream connection established successfully")
    # except Exception as e:
    #     app.logger.error(f"Failed to connect to PiTrac: {e}")
    
    # Register blueprints
    app.register_blueprint(viewfinder.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(stream.bp)
    
    @app.route("/")
    def index():
        return render_template("app/home.html")
    
    # Cleanup on shutdown
    # @app.teardown_appcontext
    # def shutdown_pitrac(exception=None):
    #     if hasattr(app, 'pitrac_connection') and app.pitrac_connection:
    #         try:
    #             app.pitrac_connection.socket.close()
    #             app.pitrac_connection.context.term()
    #             app.logger.info("PiTrac connection closed")
    #         except:
    #             pass
    
    return app