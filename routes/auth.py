from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse
from models.user import User
from models.barangay import Barangay
import os
from models import db
from models.resident import Resident
from utils import parse_date

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
            
        # Check if user is active
        if not user.is_active:
            flash('This account has been deactivated. Please contact an administrator.', 'error')
            return redirect(url_for('auth.login'))
            
        # Log user in
        login_user(user, remember=remember)
        flash('You have been logged in successfully!', 'success')
        
        # Redirect to the page user was trying to access or homepage
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.home')
            
        return redirect(next_page)
    
    # Find the latest superadmin logo
    logo_dir = os.path.join('static', 'uploads', 'superadmin_logos')
    superadmin_logo = None
    if os.path.exists(logo_dir):
        logos = [f for f in os.listdir(logo_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if logos:
            logos.sort(key=lambda x: os.path.getmtime(os.path.join(logo_dir, x)), reverse=True)
            superadmin_logo = logos[0]
    
    # Always pass the correct barangay object
    barangay = None
    if current_user.is_authenticated and current_user.barangay_id:
        barangay = Barangay.query.get(current_user.barangay_id)
    else:
        barangay = Barangay.query.first()
    
    return render_template(
        'auth/login.html',
        superadmin_logo=superadmin_logo,
        barangay=barangay
    )

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            role = request.form.get('role')
            barangay_id = request.form.get('barangay_id')
            
            # Validate required fields
            if not all([first_name, last_name, email, password, confirm_password, role]):
                flash('All fields are required', 'error')
                return render_template('auth/register.html', barangays=Barangay.query.all())
            
            # Validate password match
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('auth/register.html', barangays=Barangay.query.all())
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('auth/register.html', barangays=Barangay.query.all())
            
            # Create new user
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                barangay_id=barangay_id if barangay_id else None
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('auth/register.html', barangays=Barangay.query.all())
    
    return render_template('auth/register.html', barangays=Barangay.query.all())

@auth_bp.route('/register_barangay_admin', methods=['GET', 'POST'])
def register_barangay_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        barangay_name = request.form.get('barangay_name')
        barangay_city = request.form.get('barangay_city')
        barangay_address = request.form.get('barangay_address')

        # Validation
        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register_barangay_admin.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/register_barangay_admin.html')
        if not all([barangay_name, barangay_city, barangay_address, username, email, password]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register_barangay_admin.html')

        # Create barangay
        barangay = Barangay(name=barangay_name, address=barangay_address, city=barangay_city)
        db.session.add(barangay)
        db.session.flush()  # Get the ID

        # Create admin user
        admin = User(
            username=username,
            email=email,
            role='admin',
            barangay_id=barangay.id
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        login_user(admin)
        flash('Barangay admin account created successfully! You are now logged in.', 'success')
        return redirect(url_for('main.home'))
    return render_template('auth/register_barangay_admin.html')

@auth_bp.route('/register_user', methods=['GET', 'POST'])
def register_user():
    barangays = Barangay.query.all()
    if request.method == 'POST':
        print("DEBUG: Form submitted with data:", request.form)  # Debug print
        
        try:
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm')
            barangay_id = request.form.get('barangay_id')
            address = request.form.get('address')
            gender = request.form.get('gender')
            birth_date = request.form.get('birth_date')
            civil_status = request.form.get('civil_status')

            print("DEBUG: Extracted form data:", {  # Debug print
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'barangay_id': barangay_id,
                'address': address,
                'gender': gender,
                'birth_date': birth_date,
                'civil_status': civil_status
            })

            # Validation checks
            if not all([first_name, last_name, username, email, password, password_confirm, barangay_id, address, gender, birth_date, civil_status]):
                missing_fields = [field for field, value in {
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Username': username,
                    'Email': email,
                    'Password': password,
                    'Confirm Password': password_confirm,
                    'Barangay': barangay_id,
                    'Address': address,
                    'Gender': gender,
                    'Birth Date': birth_date,
                    'Civil Status': civil_status
                }.items() if not value]
                flash(f'Missing required fields: {", ".join(missing_fields)}', 'error')
                return render_template('auth/register_user.html', barangays=barangays)
            
            if password != password_confirm:
                flash('Passwords do not match.', 'error')
                return render_template('auth/register_user.html', barangays=barangays)
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists.', 'error')
                return render_template('auth/register_user.html', barangays=barangays)
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', 'error')
                return render_template('auth/register_user.html', barangays=barangays)

            # Create new user
            user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                barangay_id=barangay_id,
                role='resident',
                address=address
            )
            user.set_password(password)
            
            print("DEBUG: Attempting to save user to database")  # Debug print
            db.session.add(user)
            db.session.commit()
            print("DEBUG: User saved successfully")  # Debug print

            # Create corresponding Resident record
            resident = Resident(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                birth_date=parse_date(birth_date),
                civil_status=civil_status,
                address=address,
                email=email,
                barangay_id=barangay_id
            )
            db.session.add(resident)
            db.session.commit()
            print("DEBUG: Resident record created")

            flash('Registration successful! Please login with your credentials.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Registration failed - {str(e)}")  # Debug print
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('auth/register_user.html', barangays=barangays)
            
    return render_template('auth/register_user.html', barangays=barangays)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.home'))