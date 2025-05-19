from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(50))
    amount = db.Column(db.Float)
    payment_status = db.Column(db.String(20))
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.DateTime)

@app.route('/document/<int:id>/payment')
def payment_form(id):
    document = Document.query.get_or_404(id)
    if document.payment_status == 'paid':
        return redirect(url_for('view_document', id=id))
    return render_template('payment.html', document=document)

@app.route('/process_payment/<int:id>', methods=['POST'])
def process_payment(id):
    document = Document.query.get_or_404(id)
    payment_method = request.form.get('payment_method')
    
    # Update payment status
    document.payment_status = 'paid'
    document.payment_method = payment_method
    document.payment_date = datetime.utcnow()
    
    db.session.commit()
    flash(f'Payment of ${document.amount} processed successfully!', 'success')
    return redirect(url_for('view_document', id=id))

@app.route('/document/<int:id>/view')
def view_document(id):
    document = Document.query.get_or_404(id)
    if document.payment_status != 'paid':
        return redirect(url_for('payment_form', id=id))
    return render_template('view_document.html', document=document)

@app.route('/document/<int:id>/print')
def print_document(id):
    document = Document.query.get_or_404(id)
    if document.payment_status != 'paid':
        return redirect(url_for('payment_form', id=id))
    return render_template('print_document.html', document=document)

@app.route('/issue', methods=['POST'])
def issue_document():
    # ... existing code to create document ...
    
    # After saving the document:
    db.session.add(document)
    db.session.commit()
    
    # Instead of redirecting to view, redirect to payment:
    return redirect(url_for('documents.payment_form', document_id=document.id)) 