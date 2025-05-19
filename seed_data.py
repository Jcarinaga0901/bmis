import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from models import db
from models.resident import Resident
from models.document import Document
from models.official import Official
from models.project import Project
from models.user import User, ROLE_ADMIN, ROLE_STAFF, ROLE_USER

def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def create_users():
    """Create dummy users with different roles"""
    print("Creating users...")
    users = [
        # Admin users
        {
            'username': 'admin',
            'email': 'admin@example.com', 
            'password': 'admin123',
            'first_name': 'System', 
            'last_name': 'Administrator',
            'role': ROLE_ADMIN
        },
        {
            'username': 'maria.santos',
            'email': 'maria.santos@barangay.gov.ph', 
            'password': 'password123',
            'first_name': 'Maria', 
            'last_name': 'Santos',
            'role': ROLE_ADMIN
        },
        
        # Staff users
        {
            'username': 'juan.cruz',
            'email': 'juan.cruz@barangay.gov.ph', 
            'password': 'password123',
            'first_name': 'Juan', 
            'last_name': 'Cruz',
            'role': ROLE_STAFF
        },
        {
            'username': 'ana.reyes',
            'email': 'ana.reyes@barangay.gov.ph', 
            'password': 'password123',
            'first_name': 'Ana', 
            'last_name': 'Reyes',
            'role': ROLE_STAFF
        },
        
        # Regular users
        {
            'username': 'pedro.lim',
            'email': 'pedro.lim@example.com', 
            'password': 'password123',
            'first_name': 'Pedro', 
            'last_name': 'Lim',
            'role': ROLE_USER
        },
        {
            'username': 'sofia.garcia',
            'email': 'sofia.garcia@example.com', 
            'password': 'password123',
            'first_name': 'Sofia', 
            'last_name': 'Garcia',
            'role': ROLE_USER
        }
    ]
    
    for user_data in users:
        if User.query.filter_by(username=user_data['username']).first():
            print(f"User {user_data['username']} already exists, skipping...")
            continue
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(users)} users")

def create_residents():
    """Create dummy resident data"""
    print("Creating residents...")
    
    streets = [
        "Rizal Street", "Mabini Avenue", "Bonifacio Road", "Aguinaldo Boulevard", 
        "Luna Street", "Quezon Avenue", "Osmena Road", "Roxas Boulevard",
        "Sampaguita Street", "Ylang-Ylang Road", "Orchid Avenue", "Jasmine Street"
    ]
    
    barangays = ["San Isidro", "Santa Maria", "Santo Tomas", "San Pedro", "Santa Ana"]
    cities = ["Quezon City", "Manila", "Makati", "Pasig", "Taguig"]
    
    residents_data = []
    
    # Filipino first and last names
    first_names = [
        "Jose", "Maria", "Juan", "Rosa", "Pedro", "Ana", "Carlos", "Sofia", "Miguel", "Luisa",
        "Antonio", "Josefina", "Ricardo", "Elena", "Eduardo", "Teresa", "Luis", "Carolina", 
        "Ramon", "Gloria", "Roberto", "Angelica", "David", "Carmen", "Francisco", "Monica",
        "Emilio", "Patricia", "Gabriel", "Linda", "Daniel", "Cristina", "Alejandro", "Victoria"
    ]
    
    last_names = [
        "Santos", "Reyes", "Cruz", "Bautista", "Gonzales", "Ramos", "Diaz", "Lopez", "Garcia",
        "Torres", "Martinez", "Rodriguez", "Flores", "Fernandez", "Rivera", "Gomez", "Perez",
        "Mendoza", "Castillo", "Castro", "Delos Santos", "Del Rosario", "Villanueva", "Tolentino",
        "Tan", "Lim", "Morales", "Aquino", "Pascual", "Romualdez", "Navarro", "Mercado"
    ]
    
    # Generate 50 random residents
    for _ in range(50):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        street_number = random.randint(1, 999)
        street = random.choice(streets)
        barangay = random.choice(barangays)
        city = random.choice(cities)
        address = f"{street_number} {street}, Brgy. {barangay}, {city}"
        
        # Generate random phone number in PH format
        phone_prefix = random.choice(["0917", "0918", "0919", "0920", "0921", "0922", "0923"])
        phone_suffix = "".join([str(random.randint(0, 9)) for _ in range(7)])
        contact_number = f"{phone_prefix}{phone_suffix}"
        
        # Random email (not all residents have email)
        has_email = random.random() > 0.3  # 70% have email
        email = f"{first_name.lower()}.{last_name.lower()}@example.com" if has_email else None
        
        # Random birth date (age between 18 and 80)
        today = datetime.now().date()
        birth_date = random_date(
            today - timedelta(days=80*365), 
            today - timedelta(days=18*365)
        )
        
        # Add to residents data
        residents_data.append({
            'first_name': first_name,
            'last_name': last_name,
            'address': address,
            'contact_number': contact_number,
            'email': email,
            'birth_date': birth_date
        })
    
    # Create residents in the database
    for data in residents_data:
        # Check if resident already exists (by name and birth date)
        existing = Resident.query.filter_by(
            first_name=data['first_name'], 
            last_name=data['last_name'],
            birth_date=data['birth_date']
        ).first()
        
        if existing:
            print(f"Resident {data['first_name']} {data['last_name']} already exists, skipping...")
            continue
        
        resident = Resident(
            first_name=data['first_name'],
            last_name=data['last_name'],
            address=data['address'],
            contact_number=data['contact_number'],
            email=data['email'],
            birth_date=data['birth_date']
        )
        db.session.add(resident)
    
    db.session.commit()
    print(f"Created {len(residents_data)} residents")
    return Resident.query.all()

def create_officials():
    """Create dummy officials data"""
    print("Creating officials...")
    
    positions = [
        "Barangay Captain",
        "Barangay Kagawad - Peace and Order",
        "Barangay Kagawad - Health and Sanitation",
        "Barangay Kagawad - Education",
        "Barangay Kagawad - Infrastructure",
        "Barangay Kagawad - Youth and Sports",
        "Barangay Kagawad - Budget and Finance",
        "Barangay Kagawad - Senior Citizens",
        "SK Chairman",
        "Barangay Secretary",
        "Barangay Treasurer"
    ]
    
    officials_data = []
    
    # Filipino first and last names
    first_names = [
        "Roberto", "Carmen", "Eduardo", "Gloria", "Ricardo", "Teresa", "Antonio", 
        "Lucia", "Fernando", "Beatriz", "Reynaldo", "Margarita", "Ernesto", "Dolores"
    ]
    
    last_names = [
        "Bautista", "Villanueva", "Tolentino", "Romualdez", "Macapagal", "Laurel",
        "Osmena", "Roxas", "Aquino", "Marcos", "Duterte", "Estrada", "Arroyo", "Ramos"
    ]
    
    # Set term periods (past, current, and future)
    today = datetime.now().date()
    past_term_start = today - timedelta(days=1095)  # ~3 years ago
    past_term_end = today - timedelta(days=365)  # 1 year ago
    
    current_term_start = today - timedelta(days=365)  # 1 year ago
    current_term_end = today + timedelta(days=1095)  # ~3 years from now
    
    future_term_start = today + timedelta(days=1095)  # ~3 years from now
    future_term_end = today + timedelta(days=2190)  # ~6 years from now
    
    # Create past officials (completed terms)
    for i in range(5):
        officials_data.append({
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'position': random.choice(positions),
            'start_term': past_term_start,
            'end_term': past_term_end,
            'contact_number': f"09{random.randint(100000000, 999999999)}"
        })
    
    # Create current officials (one for each position)
    for position in positions:
        officials_data.append({
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'position': position,
            'start_term': current_term_start,
            'end_term': current_term_end,
            'contact_number': f"09{random.randint(100000000, 999999999)}"
        })
    
    # Create incoming officials (future terms)
    for i in range(3):
        officials_data.append({
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'position': random.choice(positions),
            'start_term': future_term_start,
            'end_term': future_term_end,
            'contact_number': f"09{random.randint(100000000, 999999999)}"
        })
    
    # Create officials in the database
    for data in officials_data:
        # Check if official already exists
        existing = Official.query.filter_by(
            first_name=data['first_name'],
            last_name=data['last_name'],
            position=data['position'],
            start_term=data['start_term']
        ).first()
        
        if existing:
            print(f"Official {data['first_name']} {data['last_name']} already exists, skipping...")
            continue
        
        official = Official(
            first_name=data['first_name'],
            last_name=data['last_name'],
            position=data['position'],
            start_term=data['start_term'],
            end_term=data['end_term'],
            contact_number=data['contact_number']
        )
        db.session.add(official)
    
    db.session.commit()
    print(f"Created {len(officials_data)} officials")

def create_documents(residents):
    """Create dummy documents for existing residents"""
    print("Creating documents...")
    
    document_types = [
        "Barangay Clearance",
        "Certificate of Residency",
        "Certificate of Indigency",
        "Business Permit",
        "Certificate of Good Moral Character",
        "Barangay ID",
        "First-Time Jobseeker Certificate"
    ]
    
    purposes = [
        "employment requirements",
        "school requirements",
        "bank loan application",
        "police clearance application",
        "scholarship application",
        "government ID application",
        "business permit application",
        "travel requirements",
        "legal proceedings",
        "medical assistance",
        "senior citizen registration",
        "voter's ID application"
    ]
    
    # Create ~100 documents with varying issue dates
    documents_data = []
    today = datetime.now().date()
    
    # Create documents for the past 2 years
    for _ in range(100):
        resident = random.choice(residents)
        document_type = random.choice(document_types)
        purpose = random.choice(purposes)
        
        # Random issue date within the past 2 years
        issue_date = random_date(today - timedelta(days=730), today)
        
        documents_data.append({
            'resident_id': resident.id,
            'document_type': document_type,
            'purpose': f"For {purpose}",
            'issue_date': issue_date
        })
    
    # Create documents in the database
    for data in documents_data:
        # Check if document already exists
        existing = Document.query.filter_by(
            resident_id=data['resident_id'],
            document_type=data['document_type'],
            issue_date=data['issue_date']
        ).first()
        
        if existing:
            print(f"Document already exists for resident ID {data['resident_id']}, skipping...")
            continue
        
        document = Document(
            resident_id=data['resident_id'],
            document_type=data['document_type'],
            purpose=data['purpose'],
            issue_date=data['issue_date']
        )
        db.session.add(document)
    
    db.session.commit()
    print(f"Created {len(documents_data)} documents")

def create_projects():
    """Create dummy projects data"""
    print("Creating projects...")
    
    project_names = [
        "Road Repair and Maintenance",
        "Community Health Center Renovation",
        "Public Park Improvement",
        "Street Lighting Installation",
        "Drainage System Upgrade",
        "Basketball Court Renovation",
        "Senior Citizen Center Construction",
        "Day Care Center Improvement",
        "Waste Management Program",
        "Clean Water Supply Project",
        "Livelihood Training Program",
        "Youth Development Program",
        "Scholarship Program",
        "Disaster Preparedness Training",
        "Tree Planting Initiative"
    ]
    
    project_descriptions = [
        "Repair and maintenance of damaged roads within the barangay to improve accessibility and safety for residents.",
        "Renovation of the community health center to provide better healthcare services to residents.",
        "Improvement of the public park with new playground equipment, benches, and landscaping.",
        "Installation of LED street lights in key areas to improve visibility and safety at night.",
        "Upgrade of the drainage system to prevent flooding during heavy rains.",
        "Renovation of the basketball court with new flooring, backboards, and seating.",
        "Construction of a dedicated center for senior citizens' activities and programs.",
        "Improvement of the day care center facilities to provide better early childhood education.",
        "Implementation of a comprehensive waste management program to promote proper waste disposal.",
        "Installation of water filters and improvement of water supply infrastructure.",
        "Training program to develop entrepreneurial skills for unemployed residents.",
        "Development program focused on sports, arts, and leadership for the youth.",
        "Educational financial assistance for deserving students from low-income families.",
        "Training program to prepare residents for natural disasters and emergencies.",
        "Environmental conservation initiative involving tree planting in various areas."
    ]
    
    status_options = ["Planned", "Ongoing", "Completed", "Cancelled"]
    
    # Create projects with different statuses
    projects_data = []
    today = datetime.now().date()
    
    # Make sure all project names are used
    for i in range(len(project_names)):
        name = project_names[i]
        description = project_descriptions[i]
        
        # Determine status and dates based on pattern
        if i % 4 == 0:  # Planned projects
            status = "Planned"
            start_date = random_date(today + timedelta(days=30), today + timedelta(days=180))
            end_date = start_date + timedelta(days=random.randint(90, 365))
            
        elif i % 4 == 1:  # Ongoing projects
            status = "Ongoing"
            start_date = random_date(today - timedelta(days=180), today - timedelta(days=10))
            end_date = random_date(today + timedelta(days=30), today + timedelta(days=180))
            
        elif i % 4 == 2:  # Completed projects
            status = "Completed"
            start_date = random_date(today - timedelta(days=730), today - timedelta(days=180))
            end_date = random_date(today - timedelta(days=179), today - timedelta(days=10))
            
        else:  # Cancelled projects
            status = "Cancelled"
            start_date = random_date(today - timedelta(days=365), today - timedelta(days=30))
            end_date = None
        
        # Generate random budget between 50,000 and 1,000,000
        budget = random.randint(5, 100) * 10000
        
        projects_data.append({
            'name': name,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'budget': budget,
            'status': status
        })
    
    # Create projects in the database
    for data in projects_data:
        # Check if project already exists
        existing = Project.query.filter_by(name=data['name']).first()
        
        if existing:
            print(f"Project '{data['name']}' already exists, skipping...")
            continue
        
        project = Project(
            name=data['name'],
            description=data['description'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            budget=data['budget'],
            status=data['status']
        )
        db.session.add(project)
    
    db.session.commit()
    print(f"Created {len(projects_data)} projects")

def main():
    """Main function to create all dummy data"""
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create dummy data
        create_users()
        residents = create_residents()
        create_officials()
        create_documents(residents)
        create_projects()
        
        print("All dummy data has been created successfully!")

if __name__ == "__main__":
    main()
