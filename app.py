from flask import Flask, session, request, g
from models import db
from config import Config
from datetime import datetime
from flask_login import LoginManager, current_user
from models.user import User, ROLE_ADMIN
from models.settings import Settings
import os
from flask_migrate import Migrate

# Import routes
from routes.main import main
from routes.residents import residents_bp
from routes.officials import officials_bp
from routes.documents import documents_bp
from routes.projects import projects_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.announcements import announcements_bp
from routes.settings import settings_bp
from routes.certificates import certificates_bp
from routes.ai import ai_bp

# Import utility functions
from utils import format_currency, calculate_age

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    # Import models after db.init_app(app)
    from models.barangay import Barangay
    
    # Ensure upload directories exist
    upload_dirs = [
        os.path.join(app.static_folder, 'uploads'),
        os.path.join(app.static_folder, 'uploads', 'barangay_logos'),
        os.path.join(app.static_folder, 'uploads', 'announcements')
    ]
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Initialize extensions
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, int(id))
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(residents_bp)
    app.register_blueprint(officials_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(announcements_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(certificates_bp)
    app.register_blueprint(ai_bp)
    
    # Add template context processors for global access in templates
    @app.context_processor
    def utility_processor():
        return {
            'format_currency': format_currency,
            'calculate_age': calculate_age,
            'now': datetime.now()  # Add current datetime to all templates
        }
    
    @app.context_processor
    def inject_logo():
        logo_path = os.path.join(app.static_folder, 'uploads', 'logo.png')
        return {'logo_exists': os.path.exists(logo_path)}
    
    @app.context_processor
    def inject_barangay_data():
        from models.barangay import Barangay  # Import inside the function!
        if current_user.is_authenticated and current_user.barangay_id:
            barangay = Barangay.query.get(current_user.barangay_id)
            if barangay and barangay.logo_filename:
                logo_path = f"uploads/barangay_logos/{barangay.logo_filename}"
            else:
                logo_path = "uploads/logo.png"
            return {
                'current_barangay': barangay,
                'barangay_logo': logo_path
            }
        else:
            return {
                'current_barangay': None,
                'barangay_logo': "uploads/logo.png"
        }
    
    @app.before_request
    def load_settings():
        if current_user.is_authenticated and current_user.barangay_id:
            g.settings = Settings.get_settings(current_user.barangay_id)
        else:
            g.settings = Settings.get_settings(1)  # Default settings for non-authenticated users
    
    @app.context_processor
    def inject_settings():
        return {'settings': g.settings}
    
    @app.context_processor
    def inject_barangay():
        from models.barangay import Barangay
        if current_user.is_authenticated and current_user.barangay_id:
            barangay = Barangay.query.get(current_user.barangay_id)
        else:
            barangay = Barangay.query.first()
        return {'barangay': barangay}
    
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'barangay_logos')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.config['OFFICIALS_UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'officials')
    os.makedirs(app.config['OFFICIALS_UPLOAD_FOLDER'], exist_ok=True)
    
    return app

def create_admin_user(app):
    """Create an admin user if none exists"""
    with app.app_context():
        # Check if any admin users exist
        admin_exists = User.query.filter_by(role=ROLE_ADMIN).first() is not None
        
        if not admin_exists:
            # Create default admin account
            User.create_admin(
                username='admin',
                email='admin@example.com',
                password='admin123',  # This should be changed immediately after first login
                first_name='System',
                last_name='Administrator'
            )
            print("Default admin user created. Please change the password immediately.")

if __name__ == '__main__':
    app = create_app()
    
    # Create database tables
    with app.app_context():
        # Drop all tables first to ensure clean state
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
    
    # Create admin user if none exists
    create_admin_user(app)
    
    app.run(debug=True)
