from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Optional
from datetime import datetime, date, time

class BlotterForm(FlaskForm):
    """Form for creating and editing blotter records"""
    id = HiddenField('ID')
    complainant_name = StringField('Complainant Name', validators=[DataRequired()])  # Changed to required
    respondent_name = StringField('Respondent Name', validators=[Optional()])
    incident_type = StringField('Incident Type', validators=[DataRequired()])
    incident_date = DateField('Incident Date', format='%Y-%m-%d', validators=[DataRequired()])
    incident_time = TimeField('Incident Time', format='%H:%M', validators=[Optional()])
    incident_location = StringField('Incident Location', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Open', 'Open'),
        ('Under Investigation', 'Under Investigation'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed')
    ], default='Open', validators=[DataRequired()])
    complainant_resident_id = IntegerField('Complainant Resident ID', validators=[Optional()])
    respondent_resident_id = IntegerField('Respondent Resident ID', validators=[Optional()])
    barangay_id = SelectField('Barangay', coerce=int, validators=[DataRequired()])
