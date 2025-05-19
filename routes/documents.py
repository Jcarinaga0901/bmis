from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.document import Document
from models.resident import Resident
from models import db
from datetime import datetime
from utils import role_required

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

@documents_bp.route('/')
@login_required
def index():
    print("Certificate page loaded")
    query = Document.query
    
    # Filter by barangay if not system admin
    if current_user.barangay_id:
        query = query.filter_by(barangay_id=current_user.barangay_id)
    
    all_documents = query.order_by(Document.issue_date.desc()).all()
    return render_template('documents/index.html', documents=all_documents)

@documents_bp.route('/issue', methods=['GET', 'POST'])
@login_required
def issue_document():
    # Pre-select resident if resident_id is provided in the URL
    resident_id = request.args.get('resident_id', None)
    selected_resident = None
    
    if resident_id:
        selected_resident = Resident.query.get(resident_id)
    
    if request.method == 'POST':
        resident_id = request.form['resident_id']
        document_type = request.form['document_type']
        purpose = request.form['purpose']
        
        if not current_user.barangay_id:
            flash('Your account is not linked to a barangay. Please contact the administrator.', 'error')
            return redirect(url_for('documents.index'))
        
        new_document = Document(
            resident_id=resident_id,
            document_type=document_type,
            purpose=purpose,
            issue_date=datetime.now().date(),
            amount=100.0,
            payment_status='pending',
            barangay_id=current_user.barangay_id
        )
        
        db.session.add(new_document)
        db.session.commit()
        flash('Document issued successfully!', 'success')
        return redirect(url_for('documents.payment_form', document_id=new_document.id))
        
    residents = Resident.query.order_by(Resident.last_name, Resident.first_name).all()
    return render_template('documents/issue.html', residents=residents, selected_resident=selected_resident)

@documents_bp.route('/<int:document_id>')
@login_required
def view_document(document_id):
    document = Document.query.get_or_404(document_id)
    if document.payment_status != 'paid':
        return redirect(url_for('documents.payment_form', document_id=document_id))
    return render_template('documents/view.html', document=document)

@documents_bp.route('/<int:document_id>/print')
@login_required
def print_document(document_id):
    document = Document.query.get_or_404(document_id)
    if document.payment_status != 'paid':
        return redirect(url_for('documents.payment_form', document_id=document_id))
    return render_template('documents/print.html', document=document)

@documents_bp.route('/<int:document_id>/payment')
@login_required
def payment_form(document_id):
    document = Document.query.get_or_404(document_id)
    if document.payment_status == 'paid':
        return redirect(url_for('documents.view_document', document_id=document_id))
    return render_template('documents/payment.html', document=document)

@documents_bp.route('/<int:document_id>/process_payment', methods=['POST'])
@login_required
def process_payment(document_id):
    document = Document.query.get_or_404(document_id)
    payment_method = request.form.get('payment_method')
    
    document.payment_status = 'paid'
    document.payment_method = payment_method
    document.payment_date = datetime.utcnow()
    
    db.session.commit()
    flash(f'Payment of ₱{document.amount} processed successfully!', 'success')
    return redirect(url_for('documents.view_document', document_id=document_id))

@documents_bp.route('/<int:document_id>/delete', methods=['POST'])
@login_required
@role_required('staff')  # Only staff and admin can delete
def delete_document(document_id):
    document = Document.query.get_or_404(document_id)
    
    try:
        db.session.delete(document)
        db.session.commit()
        flash('Document deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting document.', 'error')
    
    return redirect(url_for('documents.index'))
