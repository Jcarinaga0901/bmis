from datetime import datetime
from functools import wraps
from flask import flash, redirect, url_for, request, session, abort
from flask_login import current_user

def parse_date(date_str):
    """Parse date string to datetime object"""
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d')

def format_currency(value):
    """Format a value as Philippine Peso"""
    if value is None:
        return "₱0.00"
    return f"₱{value:,.2f}"

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
        
    today = datetime.now()
    age = today.year - birth_date.year
    
    # Adjust age if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
        
    return age

def role_required(role):
    """Decorator for views that checks if the user has the required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page', 'error')
                return redirect(url_for('auth.login', next=request.path))
            
            if role == 'admin' and not current_user.is_admin():
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('main.home'))
            
            if role == 'staff' and not current_user.is_staff():
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('main.home'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def barangay_required(f):
    """Decorator to ensure user can only access their barangay's data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        # System admin can access everything
        if current_user.role == 'admin' and not current_user.barangay_id:
            return f(*args, **kwargs)
        
        # Check if accessing own barangay data
        barangay_id = kwargs.get('barangay_id')
        if barangay_id and current_user.barangay_id != int(barangay_id):
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function
