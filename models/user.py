from models import db
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

# Define roles as constants
ROLE_ADMIN = 'admin'
ROLE_STAFF = 'staff'
ROLE_USER = 'user'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    address = db.Column(db.String(255))
    birth_date = db.Column(db.Date)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    barangay_id = db.Column(db.Integer, db.ForeignKey('barangay.id'), nullable=True)
    photo_filename = db.Column(db.String(255), nullable=True)
    logo_filename = db.Column(db.String(255), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == ROLE_ADMIN
    
    def is_staff(self):
        return self.role == ROLE_STAFF or self.role == ROLE_ADMIN
    
    def is_staff_or_admin(self):
        return self.role in [ROLE_ADMIN, ROLE_STAFF]
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @staticmethod
    def create_admin(username, email, password, first_name=None, last_name=None):
        """Helper method to create an admin user"""
        admin = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=ROLE_ADMIN
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        return admin
