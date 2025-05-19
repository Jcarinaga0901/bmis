# Barangay Management System

A comprehensive web application for managing barangay or small community administrative tasks, built with Flask.

## 📋 Features

- **Resident Management**: Track community residents with personal details
- **Document Generation**: Issue various types of official documents to residents
- **Official Records**: Maintain information about current and past barangay officials
- **Project Tracking**: Monitor community projects, budgets and status
- **User Management**: Role-based access control for staff and administrators
- **Dashboard**: Quick overview of key metrics and recent activities

## 🏗️ System Architecture

The application is built with Flask and follows a modular blueprint structure:

- **Authentication System**: User registration, login, and profile management
- **Role-Based Access Control**: Different permissions for regular users, staff, and administrators
- **SQLAlchemy ORM**: Database interaction through models
- **Blueprint Structure**: Modular code organization

## 🧰 Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy ORM (compatible with SQLite, PostgreSQL, etc.)
- **Frontend**: HTML, CSS (likely with Tailwind CSS based on class references), JavaScript
- **Authentication**: Flask-Login

## 📁 Project Structure

```
├── models/                  # Database models
│   ├── __init__.py          # Database initialization
│   ├── document.py          # Document model
│   ├── official.py          # Official model
│   ├── project.py           # Project model
│   ├── resident.py          # Resident model
│   └── user.py              # User model with authentication
│
├── routes/                  # Route blueprints
│   ├── __init__.py          # Blueprint registration
│   ├── admin.py             # Admin panel routes
│   ├── auth.py              # Authentication routes
│   ├── documents.py         # Document management routes
│   ├── main.py              # Main routes and API endpoints
│   └── officials.py         # Official management routes
│
├── static/                  # Static files (CSS, JS, images)
│
├── templates/               # Jinja2 templates
│   ├── admin/               # Admin panel templates
│   ├── auth/                # Authentication templates
│   ├── documents/           # Document templates
│   └── ...                  # Other template directories
│
├── utils.py                 # Utility functions
├── app.py                   # Application factory
└── config.py                # Configuration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/barangay-management-system.git
   cd barangay-management-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # On Windows
   set FLASK_APP=app.py
   set FLASK_ENV=development
   
   # On macOS/Linux
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

7. Access the application at [http://localhost:5000](http://localhost:5000)

### Setting up an Admin User

You need at least one admin user to access the admin panel:

```python
from models import db
from models.user import User, ROLE_ADMIN

# Create an admin user
admin = User(
    username="admin",
    email="admin@example.com",
    first_name="Admin",
    last_name="User",
    role=ROLE_ADMIN,
    is_active=True
)
admin.set_password("secure_password")
#

# Add to database
db.session.add(admin)
db.session.commit()
```

## Default Admin Account

The system comes with a default administrator account with the following credentials:

```
Username: admin
Email: admin@example.com
Password: admin123
First Name: System
Last Name: Administrator
```

⚠️ **IMPORTANT**: For security reasons, please change the default password immediately after your first login.

## 👥 User Roles

The system has three levels of access:

1. **Regular Users** - Limited access to view resident information and documents
2. **Staff Members** - Can manage residents, issue documents, and update officials
3. **Administrators** - Full system access including user management

## 📄 Document Types

The system can issue various types of documents including:

- Barangay Clearance
- Certificate of Residency
- Certificate of Indigency
- Business Permit
- And other custom document types

## 🔒 Security Features

- Password hashing
- Role-based access control
- Session management
- CSRF protection