from models import db
from datetime import datetime
from models.user import User

class Barangay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    logo_filename = db.Column(db.String(255))
    primary_color = db.Column(db.String(7), default='#166534')  # Default green-800
    secondary_color = db.Column(db.String(7), default='#15803d')  # Default green-700
    accent_color = db.Column(db.String(7), default='#16a34a')  # Default green-600
    city = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='barangay', lazy=True)
    officials = db.relationship('Official', backref='barangay', lazy=True)
    documents = db.relationship('Document', backref='barangay', lazy=True)
    announcements = db.relationship('Announcement', backref='barangay', lazy=True)
    residents = db.relationship('Resident', backref='barangay', lazy=True)

    def __repr__(self):
        return f'<Barangay {self.name}>'
