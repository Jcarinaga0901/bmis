from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db is defined
from models.announcement import Announcement
