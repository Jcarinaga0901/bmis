from datetime import datetime
from models import db

class Blotter(db.Model):
    __tablename__ = 'blotter'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complainant_name = db.Column(db.String(100))
    respondent_name = db.Column(db.String(100))
    incident_type = db.Column(db.String(100), nullable=False)
    incident_date = db.Column(db.Date)
    incident_time = db.Column(db.Time)
    incident_location = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Open')
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys for resident relationships
    complainant_resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'))
    respondent_resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'))
    
    # Add barangay relationship
    barangay_id = db.Column(db.Integer, db.ForeignKey('barangay.id'), nullable=False)
    barangay = db.relationship('Barangay', backref='blotters')
    
    # Relationships to Resident are defined in the Resident model
    
    def __repr__(self):
        return f"<Blotter {self.id}: {self.incident_type}>"
    
    def get_absolute_url(self):
        """Returns the URL to view this blotter."""
        return f"/blotters/{self.id}"
