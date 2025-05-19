from datetime import datetime
from models import db

class Resident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    civil_status = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    occupation = db.Column(db.String(100))
    photo_filename = db.Column(db.String(255))
    barangay_id = db.Column(db.Integer, db.ForeignKey('barangay.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to Blotter records
    # Blotters where this resident is the complainant
    blotters_as_complainant = db.relationship(
        'Blotter', 
        foreign_keys='Blotter.complainant_resident_id', 
        backref='complainant_resident_info', 
        lazy=True
    )
    # Blotters where this resident is the respondent
    blotters_as_respondent = db.relationship(
        'Blotter', 
        foreign_keys='Blotter.respondent_resident_id', 
        backref='respondent_resident_info', 
        lazy=True
    )

    def get_full_name(self):
        return f"{self.first_name} {self.middle_name + ' ' if self.middle_name else ''}{self.last_name}"

    def get_age(self):
        today = datetime.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def get_absolute_url(self):
        """
        Returns the absolute URL for this resident instance.
        This can be used in templates to link to a resident's detail page.
        Assumes a route like '/residents/<resident_id>' exists.
        """
        return f"/residents/{self.id}"
