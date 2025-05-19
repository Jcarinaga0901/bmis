import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secure-default-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///barangay.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
