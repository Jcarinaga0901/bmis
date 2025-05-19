from datetime import datetime
from models import db

class Official(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20))
    start_term = db.Column(db.Date, nullable=False)
    end_term = db.Column(db.Date, nullable=False)
    photo_filename = db.Column(db.String(255))
    barangay_id = db.Column(db.Integer, db.ForeignKey('barangay.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_current(self):
        today = datetime.now().date()
        return self.start_term <= today <= self.end_term
