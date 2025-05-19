from models import db

class Barangay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    captain = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(100), nullable=True)
    primary_color = db.Column(db.String(7), default='#3B82F6')
    secondary_color = db.Column(db.String(7), default='#1E40AF')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    users = db.relationship('User', backref='barangay', lazy=True)
    documents = db.relationship('Document', backref='barangay', lazy=True)
    announcements = db.relationship('Announcement', backref='barangay', lazy=True) 