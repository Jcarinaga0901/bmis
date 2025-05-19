from flask import url_for
from models.resident import Resident
from models.document import Document
from models.project import Project
from models.official import Official
from sqlalchemy import func
from datetime import datetime

class ChatbotAI:
    def __init__(self):
        self.context = {}
        self.last_query = None

    def _handle_dashboard_query(self, message, stats, db):
        """Handle queries about dashboard and system overview"""
        return {
            'message': f"""Here's your system overview:
• {stats['residents']} registered residents
• {stats['documents']} documents issued
• {stats['ongoing_projects']} ongoing projects
• {stats['officials']} active officials

What would you like to know more about?""",
            'links': [
                {'url': url_for('main.home'), 'text': 'View Dashboard'},
                {'url': url_for('main.user_guide'), 'text': 'View User Guide'}
            ]
        }

    def get_response(self, message, db):
        """Generate intelligent responses based on user input and system context"""
        try:
            message = message.lower()
            stats = self._get_system_stats(db)
            
            # Store context for follow-up questions
            self.last_query = message
            
            # Navigation and action patterns
            nav_patterns = {
                'dashboard': self._handle_dashboard_query,
                'home': self._handle_dashboard_query,
                'resident': self._handle_resident_query,
                'document': self._handle_document_query,
                'project': self._handle_project_query,
                'official': self._handle_official_query,
                'help': self._handle_help_query,
                'support': self._handle_help_query,
                'guide': self._handle_help_query,
            }

            # Check for matches in navigation patterns
            for key, handler in nav_patterns.items():
                if key in message:
                    return handler(message, stats, db)

            # Additional specific checks
            if 'blotter' in message and ('what' in message or 'why' in message):
                return {
                    'message': 'A blotter record is an official record of an incident or complaint filed at the barangay. It is important for legal documentation and community safety. Would you like to file a blotter or view existing records?',
                    'links': [
                        {'text': 'File a Blotter', 'url': '/report-blotter'},
                        {'text': 'View Blotter Records', 'url': '/blotters'}
                    ]
                }
            if 'file' in message and 'blotter' in message:
                return {
                    'message': 'To file a blotter, click the button below and fill out the incident details. Our barangay staff will review your report.',
                    'links': [
                        {'text': 'File a Blotter', 'url': '/report-blotter'}
                    ]
                }
            if 'document' in message and ('request' in message or 'how' in message):
                return {
                    'message': 'You can request documents such as Barangay Clearance, Certificate of Indigency, and Business Permit. Click below to start your request.',
                    'links': [
                        {'text': 'Request Document', 'url': '/documents'}
                    ]
                }
            if 'track' in message and 'document' in message:
                return {
                    'message': 'To track the status of your requested document, click below.',
                    'links': [
                        {'text': 'Track Document Status', 'url': '/documents/status'}
                    ]
                }
            if 'resident' in message and ('how' in message or 'info' in message):
                return {
                    'message': 'Residents can update their information, request documents, and file blotters through the system. How can I assist you today?',
                    'links': [
                        {'text': 'Residents', 'url': '/residents'}
                    ]
                }

            # Default response with system overview
            return self._handle_dashboard_query(message, stats, db)

        except Exception as e:
            print(f"Chatbot error: {str(e)}")
            return {
                'message': "I apologize, but I encountered an error. Please try asking in a different way or contact support if the issue persists.",
                'links': [{'url': url_for('main.contact_support'), 'text': 'Contact Support'}]
            }

    def _handle_resident_query(self, message, stats, db):
        recent_residents = db.session.query(Resident).order_by(Resident.created_at.desc()).limit(3).all()
        resident_list = "\n".join([f"• {r.first_name} {r.last_name}" for r in recent_residents])
        
        return {
            'message': f"""There are {stats['residents']} residents in the system.
Recently added residents:
{resident_list}

What would you like to do with resident management?""",
            'links': [
                {'url': url_for('residents.residents'), 'text': 'View All Residents'},
                {'url': url_for('residents.add_resident'), 'text': 'Add New Resident'}
            ]
        }

    def _handle_document_query(self, message, stats, db):
        return {
            'message': f"The system has processed {stats['documents']} documents. Would you like to issue a new document or view existing ones?",
            'links': [
                {'url': url_for('documents.documents'), 'text': 'View All Documents'},
                {'url': url_for('documents.issue_document'), 'text': 'Issue New Document'}
            ]
        }

    def _handle_project_query(self, message, stats, db):
        return {
            'message': f"There are {stats['ongoing_projects']} ongoing projects. Would you like to view projects or add a new one?",
            'links': [
                {'url': url_for('projects.projects'), 'text': 'View All Projects'},
                {'url': url_for('projects.add_project'), 'text': 'Add New Project'}
            ]
        }

    def _handle_official_query(self, message, stats, db):
        return {
            'message': f"Currently there are {stats['officials']} registered officials in the system.",
            'links': [
                {'url': url_for('officials.officials'), 'text': 'View Officials'},
                {'url': url_for('officials.add_official'), 'text': 'Add Official'}
            ]
        }

    def _handle_help_query(self, message, stats, db):
        return {
            'message': "How can I help you? You can ask about:\n• Residents\n• Documents\n• Projects\n• Officials\n\nOr visit our user guide for detailed instructions.",
            'links': [
                {'url': url_for('main.user_guide'), 'text': 'User Guide'},
                {'url': url_for('main.contact_support'), 'text': 'Contact Support'}
            ]
        }

    def _get_system_stats(self, db):
        """Get current system statistics"""
        return {
            'residents': db.session.query(func.count(Resident.id)).scalar() or 0,
            'documents': db.session.query(func.count(Document.id)).scalar() or 0,
            'projects': db.session.query(func.count(Project.id)).scalar() or 0,
            'ongoing_projects': db.session.query(func.count(Project.id)).filter(Project.status == 'Ongoing').scalar() or 0,
            'officials': db.session.query(func.count(Official.id)).scalar() or 0
        }
