from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.user import User, ROLE_ADMIN, ROLE_STAFF, ROLE_USER
from models import db
from functools import wraps
from models.blotter import Blotter # Import Blotter model
from models.resident import Resident # Import Resident model for linking
from datetime import datetime
from forms.blotter_form import BlotterForm
from werkzeug.utils import secure_filename
import os
from models.barangay import Barangay # Import Barangay model
from models.document import Document # Import Document model
from models.announcement import Announcement # Import Announcement model
from models.official import Official

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

ALLOWED_LOGO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
LOGO_UPLOAD_FOLDER = 'static/uploads'

def allowed_logo(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_LOGO_EXTENSIONS

@admin_bp.route('/')
@login_required
@admin_required
def index():
    if current_user.barangay_id:
        return redirect(url_for('admin.barangay_dashboard', barangay_id=current_user.barangay_id))
    return render_template('admin/index.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role', ROLE_USER)
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('admin.new_user'))
            
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('admin.new_user'))
            
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/new_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role = request.form.get('role')
        user.is_active = 'is_active' in request.form
        user.address = request.form.get('address')
        user.barangay_id = request.form.get('barangay_id')
        birth_date_str = request.form.get('birth_date')
        if birth_date_str:
            try:
                user.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except Exception:
                flash('Invalid birth date format.', 'danger')
                return redirect(url_for('admin.edit_user', user_id=user.id))
        
        # Only update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting your own account
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.users'))

# Blotter Management Routes
@admin_bp.route('/blotters')
@login_required
@admin_required
def list_blotters():
    blotters = Blotter.query.order_by(Blotter.date_reported.desc()).all()
    return render_template('admin/blotters.html', blotters=blotters)

@admin_bp.route('/blotters/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_blotter():
    residents = Resident.query.order_by(Resident.last_name, Resident.first_name).all()
    if request.method == 'POST':
        try:
            if not current_user.barangay_id:
                flash('Error: Your account is not linked to a barangay. Cannot create blotter record.', 'error')
                return render_template('admin/new_blotter.html', residents=residents)
            incident_date_str = request.form.get('incident_date')
            incident_time_str = request.form.get('incident_time')
            incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d').date()
            incident_time = None
            if incident_time_str:
                incident_time = datetime.strptime(incident_time_str, '%H:%M').time()
            new_blotter_record = Blotter(
                complainant_name=request.form.get('complainant_name'),
                respondent_name=request.form.get('respondent_name'),
                incident_type=request.form.get('incident_type'),
                incident_date=incident_date,
                incident_time=incident_time,
                incident_location=request.form.get('incident_location'),
                details=request.form.get('details'),
                status=request.form.get('status', 'Pending'),
                complainant_resident_id=request.form.get('complainant_resident_id') if request.form.get('complainant_resident_id') else None,
                respondent_resident_id=request.form.get('respondent_resident_id') if request.form.get('respondent_resident_id') else None,
                barangay_id=current_user.barangay_id
            )
            db.session.add(new_blotter_record)
            db.session.commit()
            flash('Blotter record created successfully.', 'success')
            return redirect(url_for('admin.list_blotters'))
        except ValueError as e:
            flash(f'Error in form data: {e}. Please check date and time formats.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            
    return render_template('admin/new_blotter.html', residents=residents)

@admin_bp.route('/blotters/edit/<int:blotter_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_blotter(blotter_id):
    """Edit an existing blotter or create a new one if blotter_id is 0"""
    
    # Initialize blotter and form
    if blotter_id > 0:
        # Edit existing blotter
        blotter = Blotter.query.get_or_404(blotter_id)
        form = BlotterForm(obj=blotter)
    else:
        # Create new blotter
        form = BlotterForm()

    # Set barangay choices for the SelectField
    barangays = Barangay.query.order_by(Barangay.name).all()
    form.barangay_id.choices = [(b.id, b.name) for b in barangays]

    # Get all residents for the dropdown selectors
    residents = Resident.query.order_by(Resident.last_name).all()
    
    if form.validate_on_submit():
        try:
            if blotter_id > 0:
                # Update existing blotter - use the form to update properties
                form.populate_obj(blotter)
                
                # Ensure complainant_name is set if there's a resident ID
                if blotter.complainant_resident_id and not blotter.complainant_name:
                    resident = Resident.query.get(blotter.complainant_resident_id)
                    if resident:
                        blotter.complainant_name = f"{resident.first_name} {resident.last_name}"
                
                flash('Blotter record has been updated successfully!', 'success')
            else:
                # Create new blotter - DON'T set the ID field
                new_blotter = Blotter()
                
                # Copy data from form to new_blotter manually
                new_blotter.incident_type = form.incident_type.data
                new_blotter.incident_date = form.incident_date.data
                new_blotter.incident_time = form.incident_time.data
                new_blotter.incident_location = form.incident_location.data
                new_blotter.details = form.details.data
                new_blotter.status = form.status.data
                new_blotter.date_reported = datetime.utcnow()
                
                # Handle resident IDs and ensure names are set
                if form.complainant_resident_id.data:
                    new_blotter.complainant_resident_id = form.complainant_resident_id.data
                    # Get the resident name from the database
                    resident = Resident.query.get(form.complainant_resident_id.data)
                    if resident:
                        new_blotter.complainant_name = f"{resident.first_name} {resident.last_name}"
                    else:
                        # Fallback if resident not found
                        new_blotter.complainant_name = "Unknown Complainant"
                else:
                    # Use form data if available, otherwise set a default
                    new_blotter.complainant_name = form.complainant_name.data or "Anonymous"
                
                if form.respondent_resident_id.data:
                    new_blotter.respondent_resident_id = form.respondent_resident_id.data
                    # Get the resident name from the database
                    resident = Resident.query.get(form.respondent_resident_id.data)
                    if resident:
                        new_blotter.respondent_name = f"{resident.first_name} {resident.last_name}"
                else:
                    # Respondent name is optional, use form data if available
                    new_blotter.respondent_name = form.respondent_name.data
                
                # Add the new blotter to the session
                db.session.add(new_blotter)
                flash('New blotter record has been created successfully!', 'success')
            
            # Commit the changes
            db.session.commit()
            return redirect(url_for('admin.list_blotters'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            # Use logger if current_app is available
            import logging
            logging.error(f"Error saving blotter: {str(e)}")
    
    return render_template('admin/blotter_form.html', 
                          form=form, 
                          residents=residents,
                          blotter_id=blotter_id)

@admin_bp.route('/blotters/view/<int:blotter_id>')
@login_required
@admin_required
def view_blotter(blotter_id):
    """View a specific blotter record"""
    blotter = Blotter.query.get_or_404(blotter_id)
    return render_template('admin/blotter_view.html', blotter=blotter)

@admin_bp.route('/blotters/<int:blotter_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_blotter(blotter_id):
    blotter_record = Blotter.query.get_or_404(blotter_id)
    try:
        db.session.delete(blotter_record)
        db.session.commit()
        flash('Blotter record deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting blotter record: {str(e)}', 'error')
    return redirect(url_for('admin.list_blotters'))

@admin_bp.route('/upload-logo', methods=['GET', 'POST'])
@login_required
def upload_logo():
    if not current_user.is_admin():
        flash('Only admins can upload the logo.', 'error')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        file = request.files.get('logo')
        if file and allowed_logo(file.filename):
            filename = 'logo.png'  # Always overwrite to keep it simple
            os.makedirs(LOGO_UPLOAD_FOLDER, exist_ok=True)
            file.save(os.path.join(LOGO_UPLOAD_FOLDER, filename))
            flash('Logo uploaded successfully!', 'success')
            return redirect(url_for('admin.upload_logo'))
        else:
            flash('Invalid file type. Please upload a PNG, JPG, or GIF image.', 'error')
    return render_template('admin/upload_logo.html')

@admin_bp.route('/blotters/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_blotter():
    form = BlotterForm()
    barangays = Barangay.query.order_by(Barangay.name).all()
    form.barangay_id.choices = [(b.id, b.name) for b in barangays]
    residents = Resident.query.order_by(Resident.last_name).all()

    if form.validate_on_submit():
        print('DEBUG: barangay_id from form:', form.barangay_id.data, type(form.barangay_id.data))
        print('DEBUG: barangay_id choices:', form.barangay_id.choices)
        # Ensure barangay_id is set
        if not form.barangay_id.data:
            print('DEBUG: barangay_id is missing, setting to first available barangay')
            if barangays:
                form.barangay_id.data = barangays[0].id
            else:
                form.barangay_id.data = 1  # fallback
        try:
            new_blotter = Blotter(
                complainant_name=form.complainant_name.data,
                respondent_name=form.respondent_name.data,
                incident_type=form.incident_type.data,
                incident_date=form.incident_date.data,
                incident_time=form.incident_time.data,
                incident_location=form.incident_location.data,
                details=form.details.data,
                status=form.status.data,
                complainant_resident_id=form.complainant_resident_id.data,
                respondent_resident_id=form.respondent_resident_id.data,
                barangay_id=form.barangay_id.data
            )
            db.session.add(new_blotter)
            db.session.commit()
            flash('Blotter added successfully!', 'success')
            return redirect(url_for('admin.list_blotters'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding blotter: {str(e)}', 'error')
    else:
        if request.method == 'POST':
            print('Form did not validate:', form.errors)
            flash('Please correct the errors in the form.', 'error')

    return render_template('admin/blotter_form.html', form=form, residents=residents, blotter_id=0)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.home'))
    if current_user.barangay_id:
        return redirect(url_for('admin.barangay_dashboard', barangay_id=current_user.barangay_id))
    # Count all barangay admins, residents, and staff/officials
    total_admins = User.query.filter_by(role=ROLE_ADMIN).count()
    total_residents = Resident.query.count()
    total_staff = User.query.filter_by(role=ROLE_STAFF).count()
    return render_template('admin/dashboard.html', total_admins=total_admins, total_residents=total_residents, total_staff=total_staff)

@admin_bp.route('/barangay/<int:barangay_id>/dashboard')
@login_required
@admin_required
def barangay_dashboard(barangay_id):
    # Check if the current user is an admin of the specified barangay
    if current_user.barangay_id != barangay_id:
        flash('You do not have permission to access this dashboard.', 'error')
        return redirect(url_for('main.home'))
    
    # Fetch barangay-specific data
    barangay = Barangay.query.get_or_404(barangay_id)
    residents = Resident.query.filter_by(barangay_id=barangay_id).all()
    blotters = Blotter.query.filter_by(barangay_id=barangay_id).all()
    document_count = Document.query.filter_by(barangay_id=barangay_id).count()
    announcement_count = Announcement.query.filter_by(barangay_id=barangay_id).count()
    # Gender breakdown
    male_count = Resident.query.filter_by(barangay_id=barangay_id, gender='Male').count()
    female_count = Resident.query.filter_by(barangay_id=barangay_id, gender='Female').count()
    other_count = Resident.query.filter(Resident.barangay_id==barangay_id, Resident.gender.notin_(['Male', 'Female'])).count()
    return render_template('admin/barangay_dashboard.html', barangay=barangay, residents=residents, blotters=blotters, document_count=document_count, announcement_count=announcement_count, male_count=male_count, female_count=female_count, other_count=other_count)

@admin_bp.route('/user-stats')
@login_required
@admin_required
def user_stats():
    breakdown = request.args.get('breakdown', 'all')
    if breakdown == 'admin':
        admin_count = User.query.filter_by(role=ROLE_ADMIN).count()
        staff_count = User.query.filter_by(role=ROLE_STAFF).count()
        user_count = 0
        resident_count = 0
        active_users = User.query.filter(User.role.in_([ROLE_ADMIN, ROLE_STAFF]), User.is_active == True).count()
        inactive_users = User.query.filter(User.role.in_([ROLE_ADMIN, ROLE_STAFF]), User.is_active == False).count()
        total_users = admin_count + staff_count
    elif breakdown == 'resident':
        admin_count = 0
        staff_count = 0
        user_count = User.query.filter_by(role=ROLE_USER).count()
        resident_count = Resident.query.count()
        active_users = User.query.filter_by(role=ROLE_USER, is_active=True).count()
        inactive_users = User.query.filter_by(role=ROLE_USER, is_active=False).count()
        total_users = user_count
    else:  # all
        admin_count = User.query.filter_by(role=ROLE_ADMIN).count()
        staff_count = User.query.filter_by(role=ROLE_STAFF).count()
        user_count = User.query.filter_by(role=ROLE_USER).count()
        resident_count = Resident.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        inactive_users = User.query.filter_by(is_active=False).count()
        total_users = admin_count + staff_count + user_count

    stats = {
        'admin_count': admin_count,
        'staff_count': staff_count,
        'user_count': user_count,
        'resident_count': resident_count,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'admin_percentage': round((admin_count / total_users * 100) if total_users > 0 else 0, 1),
        'staff_percentage': round((staff_count / total_users * 100) if total_users > 0 else 0, 1),
        'user_percentage': round((user_count / total_users * 100) if total_users > 0 else 0, 1),
        'active_percentage': round((active_users / total_users * 100) if total_users > 0 else 0, 1)
    }
    return render_template('admin/user_stats.html', stats=stats, breakdown=breakdown)

@admin_bp.route('/residents')
@login_required
@admin_required
def all_residents():
    # Only allow super admin (no barangay_id)
    if current_user.barangay_id:
        flash('Access denied: Only super admin can view all residents.', 'error')
        return redirect(url_for('admin.index'))
    # Optional: filter by barangay
    barangay_id = request.args.get('barangay_id', type=int)
    search = request.args.get('search', '', type=str)
    query = Resident.query
    if barangay_id:
        query = query.filter_by(barangay_id=barangay_id)
    if search:
        query = query.filter(
            Resident.first_name.ilike(f'%{search}%') |
            Resident.last_name.ilike(f'%{search}%') |
            Resident.address.ilike(f'%{search}%')
        )
    residents = query.order_by(Resident.last_name, Resident.first_name).all()
    barangays = Barangay.query.order_by(Barangay.name).all()
    return render_template('admin/resident_list.html', residents=residents, barangays=barangays, selected_barangay=barangay_id, search=search)

@admin_bp.route('/officials')
@login_required
@admin_required
def all_officials():
    if current_user.barangay_id:
        flash('Access denied: Only super admin can view all officials.', 'error')
        return redirect(url_for('admin.index'))
    barangay_id = request.args.get('barangay_id', type=int)
    search = request.args.get('search', '', type=str)
    query = Official.query
    if barangay_id:
        query = query.filter_by(barangay_id=barangay_id)
    if search:
        query = query.filter(
            Official.first_name.ilike(f'%{search}%') |
            Official.last_name.ilike(f'%{search}%') |
            Official.position.ilike(f'%{search}%')
        )
    officials = query.order_by(Official.last_name, Official.first_name).all()
    barangays = Barangay.query.order_by(Barangay.name).all()
    return render_template('admin/official_list.html', officials=officials, barangays=barangays, selected_barangay=barangay_id, search=search)

@admin_bp.route('/documents')
@login_required
@admin_required
def all_documents():
    if current_user.barangay_id:
        flash('Access denied: Only super admin can view all documents.', 'error')
        return redirect(url_for('admin.index'))
    barangay_id = request.args.get('barangay_id', type=int)
    search = request.args.get('search', '', type=str)
    query = Document.query
    if barangay_id:
        query = query.filter_by(barangay_id=barangay_id)
    if search:
        query = query.join(Document.resident).filter(
            Resident.first_name.ilike(f'%{search}%') |
            Resident.last_name.ilike(f'%{search}%') |
            Document.document_type.ilike(f'%{search}%')
        )
    documents = query.order_by(Document.date_requested.desc()).all()
    barangays = Barangay.query.order_by(Barangay.name).all()
    return render_template('admin/document_list.html', documents=documents, barangays=barangays, selected_barangay=barangay_id, search=search)

@admin_bp.route('/announcements', methods=['GET', 'POST'])
@login_required
@admin_required
def all_announcements():
    if current_user.barangay_id:
        flash('Access denied: Only super admin can manage announcements.', 'error')
        return redirect(url_for('admin.index'))
    from forms.announcement_form import AnnouncementForm
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            content=form.content.data,
            priority=form.priority.data,
            image_filename=form.image.data.filename if form.image.data else None,
            author_id=current_user.id,
            barangay_id=None  # Super admin announcement is global
        )
        if form.image.data:
            image_path = os.path.join('static/uploads/announcements', form.image.data.filename)
            form.image.data.save(image_path)
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement created and posted to all barangays!', 'success')
        return redirect(url_for('admin.all_announcements'))
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcement_list.html', announcements=announcements, form=form)

@admin_bp.route('/blotters-all')
@login_required
@admin_required
def all_blotters():
    if current_user.barangay_id:
        flash('Access denied: Only super admin can view all blotters.', 'error')
        return redirect(url_for('admin.index'))
    barangay_id = request.args.get('barangay_id', type=int)
    search = request.args.get('search', '', type=str)
    query = Blotter.query
    if barangay_id:
        query = query.filter_by(barangay_id=barangay_id)
    if search:
        query = query.filter(
            Blotter.complainant_name.ilike(f'%{search}%') |
            Blotter.respondent_name.ilike(f'%{search}%') |
            Blotter.incident_type.ilike(f'%{search}%')
        )
    blotters = query.order_by(Blotter.date_reported.desc()).all()
    barangays = Barangay.query.order_by(Barangay.name).all()
    return render_template('admin/blotter_list.html', blotters=blotters, barangays=barangays, selected_barangay=barangay_id, search=search)
