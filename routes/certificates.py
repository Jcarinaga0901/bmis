from flask import Blueprint, render_template

certificates_bp = Blueprint('certificates', __name__, url_prefix='/certificates')

@certificates_bp.route('/')
def index():
    return render_template('certificates/index.html')

@certificates_bp.route('/documents')
def documents():
    return render_template('certificates/documents.html')
