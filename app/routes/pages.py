from flask import (
    Blueprint, Flask, render_template, Response, request, jsonify, 
    redirect, url_for, session, current_app
)

bp = Blueprint('pages', __name__, url_prefix='/page')

@bp.route('/home')
def home():
    return render_template('app/pages/home.html')

@bp.route('/calibration')
def calibration():
    return render_template('app/pages/calibration.html')

@bp.route('/settings')
def settings():
    return render_template('app/pages/settings.html')

@bp.route('/about')
def about():
    return render_template('app/pages/about.html')
