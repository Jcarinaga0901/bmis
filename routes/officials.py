from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.official import Official
from models import db
from utils import parse_date, role_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename

officials_bp = Blueprint('officials', __name__, url_prefix='/officials')

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/officials'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@officials_bp.route('/')
@login_required
def officials():
    query = Official.query
    
    # Filter by barangay if not system admin
    if current_user.barangay_id:
        query = query.filter_by(barangay_id=current_user.barangay_id)
    
    all_officials = query.order_by(Official.start_term.desc()).all()
    today = datetime.now().date()
    return render_template('officials.html', officials=all_officials, today=today)

@officials_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_official():
    if request.method == 'POST':
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Handle photo upload
        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename and allowed_file(photo.filename):
                photo_filename = secure_filename(f"{request.form.get('first_name')}_{request.form.get('last_name')}_{photo.filename}")
                photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))
        
        official = Official(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            position=request.form.get('position'),
            contact_number=request.form.get('contact_number'),
            start_term=parse_date(request.form.get('start_term')),
            end_term=parse_date(request.form.get('end_term')),
            photo_filename=photo_filename,
            barangay_id=current_user.barangay_id
        )
        
        db.session.add(official)
        db.session.commit()
        
        flash('Official added successfully!', 'success')
        return redirect(url_for('officials.officials'))
    
    return render_template('add_official.html')

@officials_bp.route('/<int:official_id>', methods=['GET'])
@login_required
def view_official(official_id):
    official = Official.query.get_or_404(official_id)
    today = datetime.now().date()
    is_current = official.end_term >= today
    return render_template('view_official.html', official=official, is_current=is_current)

@officials_bp.route('/edit/<int:official_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_official(official_id):
    official = Official.query.get_or_404(official_id)
    
    if request.method == 'POST':
        # Handle photo upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename and allowed_file(photo.filename):
                # Delete old photo if exists
                if official.photo_filename:
                    old_photo_path = os.path.join(UPLOAD_FOLDER, official.photo_filename)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                
                # Save new photo
                photo_filename = secure_filename(f"{request.form.get('first_name')}_{request.form.get('last_name')}_{photo.filename}")
                photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))
                official.photo_filename = photo_filename
        
        official.first_name = request.form.get('first_name')
        official.last_name = request.form.get('last_name')
        official.position = request.form.get('position')
        official.contact_number = request.form.get('contact_number')
        official.start_term = parse_date(request.form.get('start_term'))
        official.end_term = parse_date(request.form.get('end_term'))
        
        db.session.commit()
        flash('Official updated successfully!', 'success')
        return redirect(url_for('officials.officials'))
    
    return render_template('edit_official.html', official=official)

@officials_bp.route('/delete/<int:official_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_official(official_id):
    official = Official.query.get_or_404(official_id)
    
    # Delete photo if exists
    if official.photo_filename:
        photo_path = os.path.join(UPLOAD_FOLDER, official.photo_filename)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    db.session.delete(official)
    db.session.commit()
    
    flash('Official deleted successfully!', 'success')
    return redirect(url_for('officials.officials'))
