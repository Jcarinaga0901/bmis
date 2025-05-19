from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(role):
    """Decorator to restrict access based on user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if role == 'admin' and not current_user.is_admin():
                flash('This action requires administrator privileges.', 'error')
                return redirect(url_for('main.home'))
            if role == 'staff' and not current_user.is_staff():
                flash('This action requires staff privileges.', 'error')
                return redirect(url_for('main.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
