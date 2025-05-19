from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.resident import Resident
from models import db
from utils import parse_date, role_required
from sqlalchemy import or_
import os
from werkzeug.utils import secure_filename
from models.barangay import Barangay
from models.document import Document
from datetime import datetime

residents_bp = Blueprint('residents', __name__, url_prefix='/residents')

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/residents'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@residents_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Resident.query
    
    # Filter by barangay if not system admin
    if current_user.barangay_id:
        query = query.filter_by(barangay_id=current_user.barangay_id)
    
    if search:
        query = query.filter(
            (Resident.first_name.contains(search)) |
            (Resident.last_name.contains(search))
        )
    
    residents = query.paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('residents/index.html', residents=residents, search=search)

@residents_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_resident():
    if request.method == 'POST':
        # Debug: print all form data
        print("Form data:", request.form)
        print("Form gender value:", request.form.get('gender'))
        print("Form civil_status value:", request.form.get('civil_status'))
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'birth_date', 'gender', 'civil_status', 'address']
        missing = [field for field in required_fields if not request.form.get(field)]
        if missing:
            flash(f'Missing required fields: {", ".join(missing)}', 'error')
            return render_template('add_resident.html', barangays=Barangay.query.all())
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Handle photo upload
        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename and allowed_file(photo.filename):
                photo_filename = secure_filename(f"{request.form.get('first_name')}_{request.form.get('last_name')}_{photo.filename}")
                photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))
        
        try:
            # Determine barangay_id
            barangay_id = current_user.barangay_id
            if not barangay_id:
                barangay_id = request.form.get('barangay_id')
                if not barangay_id:
                    flash('Please select a barangay for the resident.', 'error')
                    return render_template('add_resident.html', barangays=Barangay.query.all())

            resident = Resident(
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                middle_name=request.form.get('middle_name'),
                birth_date=parse_date(request.form.get('birth_date')),
                gender=request.form.get('gender'),
                civil_status=request.form.get('civil_status'),
                address=request.form.get('address'),
                contact_number=request.form.get('contact_number'),
                email=request.form.get('email'),
                occupation=request.form.get('occupation'),
                photo_filename=photo_filename,
                barangay_id=barangay_id
            )
            
            db.session.add(resident)
            db.session.commit()
            
            flash('Resident added successfully!', 'success')
            return redirect(url_for('residents.index'))
        except Exception as e:
            db.session.rollback()
            print(f"Error adding resident: {str(e)}")
            flash(f'Error adding resident: {str(e)}', 'error')
            return render_template('add_resident.html', barangays=Barangay.query.all())
    
    return render_template('add_resident.html', barangays=Barangay.query.all())

@residents_bp.route('/<int:resident_id>', methods=['GET'])
@login_required
def view_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    return render_template('residents/view.html', resident=resident)

@residents_bp.route('/edit/<int:resident_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    
    if request.method == 'POST':
        # Handle photo upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename and allowed_file(photo.filename):
                # Delete old photo if exists
                if resident.photo_filename:
                    old_photo_path = os.path.join(UPLOAD_FOLDER, resident.photo_filename)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                
                # Save new photo
                photo_filename = secure_filename(f"{request.form.get('first_name')}_{request.form.get('last_name')}_{photo.filename}")
                photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))
                resident.photo_filename = photo_filename
        
        # Handle photo removal
        if request.form.get('remove_photo'):
            if resident.photo_filename:
                photo_path = os.path.join(UPLOAD_FOLDER, resident.photo_filename)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                resident.photo_filename = None
        
        resident.first_name = request.form.get('first_name')
        resident.last_name = request.form.get('last_name')
        resident.middle_name = request.form.get('middle_name')
        resident.birth_date = parse_date(request.form.get('birth_date'))
        resident.gender = request.form.get('gender')
        resident.civil_status = request.form.get('civil_status')
        resident.address = request.form.get('address')
        resident.contact_number = request.form.get('contact_number')
        resident.email = request.form.get('email')
        resident.occupation = request.form.get('occupation')
        
        db.session.commit()
        flash('Resident updated successfully!', 'success')
        return redirect(url_for('residents.view_resident', resident_id=resident.id))
    
    return render_template('residents/edit.html', resident=resident)

@residents_bp.route('/delete/<int:resident_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    
    # Delete photo if exists
    if resident.photo_filename:
        photo_path = os.path.join(UPLOAD_FOLDER, resident.photo_filename)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    db.session.delete(resident)
    db.session.commit()
    
    flash('Resident deleted successfully!', 'success')
    return redirect(url_for('residents.index'))

@residents_bp.route('/')
def list_residents():
    residents = Resident.query.all()
    return render_template('residents/list.html', residents=residents)

@residents_bp.route('/issue_document', methods=['POST'])
@login_required
def issue_document():
    resident_id = request.form.get('resident_id')
    document_type = request.form.get('document_type')
    purpose = request.form.get('purpose')
    
    if not resident_id or not document_type or not purpose:
        flash('All fields are required.', 'danger')
        return redirect(url_for('residents.index'))
    
    try:
        resident = Resident.query.get_or_404(resident_id)
        if not resident.barangay_id:
            flash('Resident is not linked to a barangay.', 'danger')
            return redirect(url_for('residents.index'))
        
        new_document = Document(
            resident_id=resident_id,
            document_type=document_type,
            purpose=purpose,
            issue_date=datetime.now().date(),
            amount=100.0,
            payment_status='pending',
            barangay_id=current_user.barangay_id
        )
        
        db.session.add(new_document)
        db.session.commit()
        flash('Document issued successfully!', 'success')
        return redirect(url_for('residents.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error issuing document: {str(e)}', 'error')
        return redirect(url_for('residents.index'))
