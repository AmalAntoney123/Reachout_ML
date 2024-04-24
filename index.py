from flask import Blueprint, render_template, send_from_directory
import os

index_bp = Blueprint('index', __name__, static_folder='static')

@index_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@index_bp.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)