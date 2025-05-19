from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from models import db
from werkzeug.utils import secure_filename
from models.settings import Settings
from utils import role_required
from models.barangay import Barangay

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_admin:
        flash('You do not have permission to access settings.', 'error')
        return redirect(url_for('main.home'))

    barangay = current_user.barangay

    # Default admin logic
    if current_user.role == 'default_admin':
        if request.method == 'POST':
            logo = request.files.get('logo')
            remove_logo = request.form.get('remove_logo')
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'default_admin_logos')
            os.makedirs(upload_dir, exist_ok=True)
            
            if remove_logo == '1' and current_user.logo_filename:
                logo_path = os.path.join(upload_dir, current_user.logo_filename)
                if os.path.exists(logo_path):
                    os.remove(logo_path)
                current_user.logo_filename = None
                db.session.commit()
                flash('Logo removed successfully!', 'success')
                return redirect(url_for('settings.settings'))
            elif logo and logo.filename:
                # Remove old logo if exists
                if current_user.logo_filename:
                    old_logo_path = os.path.join(upload_dir, current_user.logo_filename)
                    if os.path.exists(old_logo_path):
                        os.remove(old_logo_path)
                
                # Save new logo
                filename = secure_filename(f"defaultadmin_{current_user.username}_{logo.filename}")
                logo.save(os.path.join(upload_dir, filename))
                current_user.logo_filename = filename
                db.session.commit()
                
                # Debug logging
                print('DEBUG: Uploaded logo filename:', current_user.logo_filename)
                print('DEBUG: Logo file exists:', os.path.exists(os.path.join(upload_dir, filename)))
                
                flash('Logo uploaded successfully!', 'success')
                return redirect(url_for('settings.settings'))
        return render_template('settings.html', barangay=None)

    if barangay is None:
        # Handle super admin logo upload/removal
        if request.method == 'POST':
            logo = request.files.get('superadmin_logo')
            remove_logo = request.form.get('remove_logo')
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'superadmin_logos')
            os.makedirs(upload_dir, exist_ok=True)
            if remove_logo == '1' and current_user.logo_filename:
                logo_path = os.path.join(upload_dir, current_user.logo_filename)
                if os.path.exists(logo_path):
                    os.remove(logo_path)
                current_user.logo_filename = None
                db.session.commit()
                flash('Logo removed successfully!', 'success')
                return redirect(url_for('settings.settings'))
            elif logo and logo.filename:
                # Remove old logo if exists
                if current_user.logo_filename:
                    old_logo_path = os.path.join(upload_dir, current_user.logo_filename)
                    if os.path.exists(old_logo_path):
                        os.remove(old_logo_path)
                filename = f"superadmin_{current_user.username}_{logo.filename}"
                filename = filename.replace(' ', '_')
                logo.save(os.path.join(upload_dir, filename))
                current_user.logo_filename = filename
                print('DEBUG: Uploaded logo filename:', current_user.logo_filename)
                print('DEBUG: Logo file exists:', os.path.exists(os.path.join(upload_dir, filename)))
                flash('Logo uploaded successfully!', 'success')
                return redirect(url_for('settings.settings'))
        return render_template('settings.html', barangay=None)

    if request.method == 'POST':
        # Handle logo removal
        if request.form.get('remove_logo') == '1':
            if barangay and barangay.logo_filename:
                logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'barangay_logos', barangay.logo_filename)
                if os.path.exists(logo_path):
                    os.remove(logo_path)
                barangay.logo_filename = None
        else:
            # Handle logo upload
            logo = request.files.get('logo')
            if logo and logo.filename:
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                filename = secure_filename(logo.filename)
                logo.save(os.path.join(upload_dir, filename))
                if barangay:
                    barangay.logo_filename = filename
                    db.session.commit()
                    flash('Logo uploaded successfully!', 'success')
                else:
                    flash('No barangay found for this user. Cannot upload logo.', 'error')
                return redirect(url_for('settings.settings'))

        # Handle color theme changes
        if barangay:
            barangay.primary_color = request.form.get('primary_color', '#166534')
            barangay.secondary_color = request.form.get('secondary_color', '#15803d')
            barangay.accent_color = request.form.get('accent_color', '#16a34a')
            db.session.commit()

        try:
            db.session.commit()
            flash('Settings updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating settings.', 'error')
            current_app.logger.error(f'Error updating settings: {str(e)}')

        return redirect(url_for('settings.settings'))

    return render_template('settings.html', barangay=barangay)

@settings_bp.route('/theme', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def theme_settings():
    settings = Settings.get_settings(current_user.barangay_id)
    
    if request.method == 'POST':
        settings.primary_color = request.form.get('primary_color', '#166534')
        settings.secondary_color = request.form.get('secondary_color', '#15803d')
        settings.accent_color = request.form.get('accent_color', '#16a34a')
        settings.text_color = request.form.get('text_color', '#166534')
        settings.background_color = request.form.get('background_color', '#ffffff')
        
        db.session.commit()
        flash('Theme settings updated successfully!', 'success')
        return redirect(url_for('settings.theme_settings'))
    
    return render_template('settings/theme.html', settings=settings)