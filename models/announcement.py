from datetime import datetime
from models import db

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('announcements', lazy=True))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    image_filename = db.Column(db.String(255))
    image_url = db.Column(db.String, nullable=True)
    barangay_id = db.Column(db.Integer, db.ForeignKey('barangay.id'), nullable=False)
    
    def __repr__(self):
        return f'<Announcement {self.title}>'
