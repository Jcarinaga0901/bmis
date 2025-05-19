from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User, ROLE_ADMIN, ROLE_USER
from models import db
from urllib.parse import urlparse as url_parse
from models.barangay import Barangay
import os
from werkzeug.security import generate_password_hash
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        remember = 'remember' in request.form
        
        # Validate role selection
        if not role or role not in [ROLE_USER, ROLE_ADMIN]:
            flash('Please select a valid account type', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
            
        # Check if user is active
        if not user.is_active:
            flash('This account has been deactivated. Please contact an administrator.', 'error')
            return redirect(url_for('auth.login'))
            
        # Check if user's role matches selected role
        if user.role != role:
            role_name = "Barangay Admin" if role == ROLE_ADMIN else "Resident"
            flash(f'This account is not registered as a {role_name}. Please select the correct account type.', 'error')
            return redirect(url_for('auth.login'))
            
        # Log user in
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.first_name}!', 'success')
        
        # Redirect based on role
        if role == ROLE_ADMIN:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.home'))
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        role = request.form.get('role', ROLE_USER)  # Default to user role
        
        # Validate required fields
        if not all([first_name, last_name, username, email, password, password_confirm]):
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')
            
        # Check password match
        if password != password_confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
            
        # Check for duplicate username/email
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('auth/register.html')
            
        # Create user
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')

        # Handle profile photo upload
        photo = request.files.get('photo')
        remove_photo = request.form.get('remove_photo')
        upload_dir = os.path.join('static', 'uploads', 'users')
        os.makedirs(upload_dir, exist_ok=True)
        if remove_photo == '1' and current_user.photo_filename:
            photo_path = os.path.join(upload_dir, current_user.photo_filename)
            if os.path.exists(photo_path):
                os.remove(photo_path)
            current_user.photo_filename = None
        elif photo and photo.filename:
            # Remove old photo if exists
            if current_user.photo_filename:
                old_photo_path = os.path.join(upload_dir, current_user.photo_filename)
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)
            filename = f"{current_user.username}_{photo.filename}"
            filename = filename.replace(' ', '_')
            photo.save(os.path.join(upload_dir, filename))
            current_user.photo_filename = filename

        # Update password if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('auth.edit_profile'))
                
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('auth.edit_profile'))
                
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/edit_profile.html') 