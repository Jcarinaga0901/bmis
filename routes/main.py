from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models.resident import Resident
from models.official import Official
from models.document import Document
from models.project import Project
from models.blotter import Blotter # Import Blotter model
from models import db
from sqlalchemy import func, or_
from utils import ChatbotAI  # Updated import statement
from forms.blotter_form import BlotterForm
from models.announcement import Announcement
from models.user import User
from models.barangay import Barangay

chatbot_ai = ChatbotAI()

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    if current_user.is_admin():
        if current_user.barangay_id:
            return redirect(url_for('admin.barangay_dashboard', barangay_id=current_user.barangay_id))
        else:
            return redirect(url_for('admin.dashboard'))
    else:
        # Example: Count residents per barangay
        barangays = Barangay.query.all()
        resident_counts = [
            {'barangay': b.name, 'count': User.query.filter_by(barangay_id=b.id, role='resident').count()}
            for b in barangays
        ]
        return render_template('main/home.html', resident_counts=resident_counts)

@main.route('/api/dashboard-stats')
def dashboard_stats():
    resident_count = Resident.query.count()
    official_count = 5  # Replace with actual official count if you have an officials model
    document_count = Document.query.filter(
        func.extract('month', Document.date_created) == datetime.now().month,
        func.extract('year', Document.date_created) == datetime.now().year
    ).count()
    
    return jsonify({
        'residents': resident_count,
        'officials': official_count,
        'documents': document_count
    })

@main.route('/api/recent-documents')
def recent_documents():
    # Get 5 most recent documents with resident info
    recent_docs = Document.query.order_by(Document.issue_date.desc()).limit(5).all()
    
    documents = []
    for doc in recent_docs:
        # Assign color based on document type
        type_color = "bg-blue-100 text-blue-800"
        if "clearance" in doc.document_type.lower():
            type_color = "bg-green-100 text-green-800"
        elif "indigency" in doc.document_type.lower():
            type_color = "bg-yellow-100 text-yellow-800"
        elif "business" in doc.document_type.lower():
            type_color = "bg-purple-100 text-purple-800"
            
        documents.append({
            'id': doc.id,
            'document_type': doc.document_type,
            'type_color': type_color,
            'resident_name': f"{doc.resident.first_name} {doc.resident.last_name}",
            'resident_id': doc.resident_id,
            'issue_date': doc.issue_date.strftime('%b %d, %Y')
        })
    
    return jsonify({'documents': documents})

@main.route('/api/recent-blotters')
def recent_blotters():
    # Get 5 most recent blotter records
    recent_blotter_records = Blotter.query.order_by(Blotter.date_reported.desc()).limit(5).all()
    
    blotters_data = []
    for record in recent_blotter_records:
        status_color = "bg-gray-100 text-gray-800" # Default
        if record.status.lower() == 'pending':
            status_color = "bg-yellow-100 text-yellow-800"
        elif record.status.lower() in ['under investigation', 'open', 'investigating']:
            status_color = "bg-blue-100 text-blue-800"
        elif record.status.lower() == 'resolved' or record.status.lower() == 'amicably settled':
            status_color = "bg-green-100 text-green-800"
        elif record.status.lower() == 'closed' or record.status.lower() == 'referred to higher hq':
            status_color = "bg-red-100 text-red-800"

        blotters_data.append({
            'id': record.id,
            'incident_type': record.incident_type,
            'status': record.status,
            'status_color': status_color,
            'complainant_name': record.complainant_name,
            'respondent_name': record.respondent_name,
            'date_reported': record.date_reported.strftime('%b %d, %Y %I:%M %p'),
            'incident_date': record.incident_date.strftime('%b %d, %Y')
        })
    
    return jsonify({'blotters': blotters_data})

@main.route('/blotters')
def view_blotters():
    # For public view, you might want to filter or limit details for privacy
    # For now, let's show all, ordered by most recent
    # Consider pagination for large datasets
    page = request.args.get('page', 1, type=int)
    per_page = 10 # Number of blotters per page
    blotter_pagination = Blotter.query.order_by(Blotter.date_reported.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('blotters.html', blotter_pagination=blotter_pagination)

@main.route('/user-guide')
def user_guide():
    return render_template('user_guide.html')

@main.route('/contact-support', methods=['GET', 'POST'])
def contact_support():
    if request.method == 'POST':
        # In a real application, you would process the form data here
        # This could include sending an email or storing the request in the database
        flash('Your support request has been submitted. We will get back to you as soon as possible.', 'success')
        return redirect(url_for('main.contact_support'))
    
    return render_template('contact_support.html')

@main.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        message = request.json.get('message', '').lower()
        response = chatbot_ai.get_response(message, db)
        return jsonify(response)
    except Exception as e:
        print(f"Chatbot API error: {str(e)}")
        return jsonify({
            'message': 'Sorry, I encountered an error. Please try again.',
            'links': [{'url': url_for('main.contact_support'), 'text': 'Contact Support'}]
        }), 500

@main.route('/report-blotter', methods=['GET', 'POST'])
def report_blotter():
    """Allow users to report a new blotter incident."""
    form = BlotterForm()
    barangays = Barangay.query.order_by(Barangay.name).all()
    form.barangay_id.choices = [(b.id, b.name) for b in barangays]
    # Pre-fill form with today's date if it's a new GET request
    if request.method == 'GET':
        form.incident_date.data = datetime.now().date()
    # Generate a case number for new blotters
    current_year = datetime.now().year
    last_blotter = Blotter.query.order_by(Blotter.id.desc()).first()
    if last_blotter and hasattr(last_blotter, 'id') and last_blotter.id:
        new_number = last_blotter.id + 1
    else:
        new_number = 1
    case_number = f"BLT-{current_year}-{new_number:04d}"
    if form.validate_on_submit():
        print('DEBUG: barangay_id from form:', form.barangay_id.data, type(form.barangay_id.data))
        print('DEBUG: barangay_id choices:', form.barangay_id.choices)
        # Ensure barangay_id is set
        if not form.barangay_id.data:
            print('DEBUG: barangay_id is missing, setting to first available barangay')
            if barangays:
                form.barangay_id.data = barangays[0].id
            else:
                form.barangay_id.data = 1  # fallback
        try:
            new_blotter = Blotter()
            new_blotter.complainant_name = form.complainant_name.data 
            new_blotter.respondent_name = form.respondent_name.data
            new_blotter.incident_type = form.incident_type.data
            new_blotter.incident_date = form.incident_date.data or datetime.now().date()
            new_blotter.incident_time = form.incident_time.data
            new_blotter.incident_location = form.incident_location.data
            new_blotter.details = form.details.data
            new_blotter.status = form.status.data
            new_blotter.date_reported = datetime.utcnow()
            if form.complainant_resident_id.data:
                new_blotter.complainant_resident_id = form.complainant_resident_id.data
            if form.respondent_resident_id.data:
                new_blotter.respondent_resident_id = form.respondent_resident_id.data
            new_blotter.barangay_id = form.barangay_id.data
            # If user is logged in, try to associate them as the complainant
            if current_user.is_authenticated:
                user_email = None
                if hasattr(current_user, 'email'):
                    user_email = current_user.email
                if user_email:
                    resident = Resident.query.filter_by(email=user_email).first()
                    if resident:
                        new_blotter.complainant_resident_id = resident.id
                        if not new_blotter.complainant_name:
                            new_blotter.complainant_name = f"{resident.first_name} {resident.last_name}"
            if current_user.is_authenticated:
                if hasattr(current_user, 'full_name') and current_user.full_name:
                    new_blotter.complainant_name = current_user.full_name
                elif hasattr(current_user, 'username'):
                    new_blotter.complainant_name = current_user.username
                if hasattr(current_user, 'email'):
                    resident = Resident.query.filter_by(email=current_user.email).first()
                    if resident:
                        new_blotter.complainant_resident_id = resident.id
                current_app.logger.info(f"Created blotter for user: {current_user.username}, " +
                                      f"with complainant: {new_blotter.complainant_name}, " +
                                      f"resident_id: {new_blotter.complainant_resident_id}")
            db.session.add(new_blotter)
            db.session.commit()
            flash(f'Your incident has been reported successfully. Case number: {case_number}', 'success')
            if current_user.is_authenticated:
                return redirect(url_for('main.user_blotters'))
            else:
                return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating blotter: {str(e)}', 'error')
    residents = []
    if current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin():
        residents = Resident.query.order_by(Resident.last_name).all()
    return render_template('user/blotter_report_form.html', form=form, residents=residents)

@main.route('/my-blotters')
@login_required
def user_blotters():
    """Show all blotter reports related to the current user."""
    # Use multiple methods to find blotters associated with the current user
    
    # Method 1: Find by resident ID (if user has a linked resident profile)
    resident = None
    if hasattr(current_user, 'email'):
        resident = Resident.query.filter_by(email=current_user.email).first()
    
    # Initialize query
    query_conditions = []
    
    # Add conditions to find blotters by resident ID
    if resident:
        query_conditions.append(Blotter.complainant_resident_id == resident.id)
        query_conditions.append(Blotter.respondent_resident_id == resident.id)
    
    # Method 2: Find by user's name (if blotter was submitted with their name)
    if hasattr(current_user, 'full_name') and current_user.full_name:
        query_conditions.append(Blotter.complainant_name == current_user.full_name)
    
    # Method 3: Find by username (if blotter was submitted with their username)
    if hasattr(current_user, 'username') and current_user.username:
        query_conditions.append(Blotter.complainant_name == current_user.username)
    
    # If we have any conditions, run the query
    if query_conditions:
        # Use OR to match any of the conditions
        blotters = Blotter.query.filter(
            or_(*query_conditions)
        ).order_by(Blotter.date_reported.desc()).all()
    else:
        blotters = []
    
    # For debugging
    if len(blotters) == 0:
        current_app.logger.info(f"No blotters found for user: {current_user.username}")
        # Check if there are any blotters at all in the system
        all_blotters = Blotter.query.all()
        current_app.logger.info(f"Total blotters in system: {len(all_blotters)}")
        if all_blotters:
            for blotter in all_blotters[:5]:  # Show first 5 for debugging
                current_app.logger.info(f"Blotter #{blotter.id}: complainant={blotter.complainant_name}, " +
                                       f"complainant_id={blotter.complainant_resident_id}")
    
    return render_template('user/blotter_status.html', reported_blotters=blotters)

@main.route('/blotter-details/<int:blotter_id>')
@login_required
def blotter_details(blotter_id):
    """Show details of a specific blotter."""
    blotter = Blotter.query.get_or_404(blotter_id)
    
    # Security check: ensure user is allowed to view this blotter
    is_admin = current_user.is_admin() if hasattr(current_user, 'is_admin') else False
    
    if not is_admin:
        # Try to find resident by email instead of user_id
        user_email = current_user.email if hasattr(current_user, 'email') else None
        if user_email:
            resident = Resident.query.filter_by(email=user_email).first()
            if resident and (blotter.complainant_resident_id == resident.id or blotter.respondent_resident_id == resident.id):
                # User is involved in this blotter, allow access
                pass
            else:
                flash('You do not have permission to view this blotter.', 'error')
                return redirect(url_for('main.user_blotters'))
        else:
            flash('You do not have permission to view this blotter.', 'error')
            return redirect(url_for('main.home'))
        
    return render_template('user/blotter_details.html', blotter=blotter)

@main.route('/public-blotters')
def public_blotters():
    """Show recent public blotters for community awareness."""
    # Only show blotters that are marked as public
    # Assuming you have a 'is_public' field in your Blotter model
    blotters = Blotter.query.filter_by(is_public=True).order_by(Blotter.created_at.desc()).limit(10).all()
    return render_template('public/recent_blotters.html', blotters=blotters)
