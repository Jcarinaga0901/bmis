from models import db

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barangay_id = db.Column(db.Integer, db.ForeignKey('barangay.id'), nullable=False)
    primary_color = db.Column(db.String(7), default='#166534')  # Default green-800
    secondary_color = db.Column(db.String(7), default='#15803d')  # Default green-700
    accent_color = db.Column(db.String(7), default='#16a34a')  # Default green-600
    text_color = db.Column(db.String(7), default='#166534')  # Default green-800
    background_color = db.Column(db.String(7), default='#ffffff')  # Default white
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationship
    barangay = db.relationship('Barangay', backref=db.backref('settings', uselist=False))

    @classmethod
    def get_settings(cls, barangay_id):
        settings = cls.query.filter_by(barangay_id=barangay_id).first()
        if not settings:
            settings = cls(barangay_id=barangay_id)
            db.session.add(settings)
            db.session.commit()
        return settings 