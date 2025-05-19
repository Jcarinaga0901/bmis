from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.project import Project
from models import db
from utils import parse_date, role_required
from datetime import datetime

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/')
@login_required
def projects():
    all_projects = Project.query.order_by(Project.start_date.desc()).all()
    return render_template('projects.html', projects=all_projects)

@projects_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('staff')  # Only staff and admin can add projects
def add_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = parse_date(request.form['start_date'])
        end_date = parse_date(request.form['end_date']) if request.form['end_date'] else None
        budget = float(request.form['budget']) if request.form['budget'] else None
        status = request.form['status']
        
        new_project = Project(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            status=status
        )
        
        db.session.add(new_project)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('projects.projects'))
        
    return render_template('add_project.html')

@projects_bp.route('/<int:project_id>', methods=['GET'])
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('view_project.html', project=project)

@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.name = request.form['name']
        project.description = request.form['description']
        project.start_date = parse_date(request.form['start_date'])
        project.end_date = parse_date(request.form['end_date']) if request.form['end_date'] else None
        project.budget = float(request.form['budget']) if request.form['budget'] else None
        project.status = request.form['status']
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))
        
    return render_template('edit_project.html', project=project)

@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
@role_required('admin')  # Only admin can delete projects
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting project.', 'error')
    
    return redirect(url_for('projects.projects'))
