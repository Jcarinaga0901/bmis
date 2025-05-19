from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.announcement import Announcement
from models import db
from datetime import datetime
from utils import role_required
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/uploads/announcements'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

announcements_bp = Blueprint('announcements', __name__, url_prefix='/announcements')

@announcements_bp.route('/')
def announcements():
    # Show active announcements to everyone
    active_announcements = Announcement.query.filter_by(is_active=True)\
        .order_by(Announcement.date_posted.desc()).all()
    return render_template('announcements/index.html', announcements=active_announcements)

@announcements_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('staff')  # Only staff and admin can create
def create_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        priority = request.form['priority']
        image = request.files.get('image')
        image_filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_filename = filename

        new_announcement = Announcement(
            title=title,
            content=content,
            priority=priority,
            author_id=current_user.id,
            image_filename=image_filename,
            barangay_id=current_user.barangay_id
        )
        
        db.session.add(new_announcement)
        db.session.commit()
        flash('Announcement created successfully!', 'success')
        return redirect(url_for('announcements.announcements'))
    
    return render_template('announcements/create.html')

@announcements_bp.route('/<int:announcement_id>')
def view_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    return render_template('announcements/view.html', announcement=announcement)

@announcements_bp.route('/<int:announcement_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def edit_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    
    if request.method == 'POST':
        announcement.title = request.form['title']
        announcement.content = request.form['content']
        announcement.priority = request.form['priority']
        announcement.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Announcement updated successfully!', 'success')
        return redirect(url_for('announcements.view_announcement', announcement_id=announcement.id))
    
    return render_template('announcements/edit.html', announcement=announcement)

@announcements_bp.route('/<int:announcement_id>/delete', methods=['POST'])
@login_required
@role_required('staff')
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    
    try:
        db.session.delete(announcement)
        db.session.commit()
        flash('Announcement deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting announcement.', 'error')
    
    return redirect(url_for('announcements.announcements'))

@announcements_bp.route('/manage')
@login_required
@role_required('staff')
def manage_announcements():
    # Show all announcements for management
    all_announcements = Announcement.query.order_by(Announcement.date_posted.desc()).all()
    return render_template('announcements/manage.html', announcements=all_announcements)
