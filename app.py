from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
import random
import string
from datetime import datetime, timezone
import pytz
import json
import requests
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__, template_folder='templates')
app.config.update(
    SECRET_KEY='citysamadhan2025',
    SQLALCHEMY_DATABASE_URI='sqlite:///database.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER='static/uploads',
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='hakyakrudost@gmail.com',
    MAIL_PASSWORD='obnmcrphxilkmjph'
)

db = SQLAlchemy(app)
mail = Mail(app)

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper to format timestamps in IST (+05:30)
def format_datetime_ist(dt):
    if not dt:
        return ''
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ist = pytz.timezone('Asia/Kolkata')
    dt_ist = dt.astimezone(ist)
    return dt_ist.strftime('%Y-%m-%d %H:%M:%S IST')

# Register Jinja filter
app.jinja_env.filters['format_datetime_ist'] = format_datetime_ist

# Load Indian cities data
def load_indian_cities():
    try:
        with open('indian_cities.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fetch cities data from an API or create a basic list
        return {"states": {
            "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
            "Delhi": ["New Delhi"],
            "Karnataka": ["Bangalore", "Mysore"],
            # Add more states and cities
        }}

INDIAN_CITIES = load_indian_cities()

# Department Information
DEPARTMENT_INFO = {
    'Electricity Board': {
        'description': 'Handles issues related to street lighting and electrical infrastructure',
        'common_issues': ['broken streetlights', 'power outages', 'electrical hazards']
    },
    'Public Works Department': {
        'description': 'Manages road infrastructure and maintenance',
        'common_issues': ['potholes', 'road damage', 'partial roads']
    },
    'Municipal Waste Management': {
        'description': 'Handles garbage collection and waste management',
        'common_issues': ['garbage accumulation', 'waste collection', 'dumping']
    },
    'Drainage Department': {
        'description': 'Manages drainage systems and related issues',
        'common_issues': ['clogged drains', 'flooding', 'sewage issues']
    },
    'Urban Development Authority': {
        'description': 'Oversees urban infrastructure development',
        'common_issues': ['damaged sidewalks', 'unauthorized construction']
    },
    'Traffic Management Department': {
        'description': 'Manages traffic signals and road safety',
        'common_issues': ['broken traffic signals', 'traffic congestion']
    },
    'Water Supply Authority': {
        'description': 'Handles water supply and related infrastructure',
        'common_issues': ['water pipe leakage', 'water quality', 'supply disruption']
    },
    'Transport Department': {
        'description': 'Manages transport infrastructure and signage',
        'common_issues': ['poor road signs', 'bus stop issues']
    },
    'Municipal Corporation': {
        'description': 'General civic issues and coordination',
        'common_issues': ['abandoned debris', 'public space maintenance']
    }
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    notifications_enabled = db.Column(db.Boolean, default=True)
    complaints = db.relationship('Complaint', backref='author', lazy=True)
    votes = db.relationship('Vote', backref='voter', lazy=True)
    reports = db.relationship('Report', backref='reporter', lazy=True)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    departments = db.relationship('DepartmentContact', backref='city', lazy=True)

class DepartmentContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    department_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    toll_free_number = db.Column(db.String(20), nullable=False)
    office_address = db.Column(db.String(200))

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Reported')  # Reported, Accepted, Work in Progress, Completed, Rejected
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status_updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status tracking timestamps
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    work_in_progress_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    
    feedback = db.Column(db.Text)
    feedback_timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=True)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    photo = db.Column(db.String(200))
    map_location = db.Column(db.String(500))  # Optional detailed map location
    phone_number = db.Column(db.String(15))  # Optional phone number, admin-only visibility
    is_thread = db.Column(db.Boolean, default=False)
    thread_count = db.Column(db.Integer, default=0)
    
    # Relationship for thread replies
    replies = db.relationship('Complaint', 
                            backref=db.backref('parent_complaint', remote_side=[id]),
                            lazy='dynamic')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuthorityResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    status_update = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    department_name = db.Column(db.String(100), nullable=False)
    officer_name = db.Column(db.String(100))
    estimated_completion_date = db.Column(db.DateTime)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Reviewed, Resolved

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # status_update, response, thread_update, etc.
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)

# Create database if it doesn't exist
with app.app_context():
    # Create all tables only if they don't exist
    db.create_all()
    print("Database initialized successfully!")

# Context processor to provide notifications data to all templates
@app.context_processor
def inject_notifications():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        unread_count = Notification.query.filter_by(user_id=user_id, read=False).count()
        recent_notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.timestamp.desc()).limit(5).all()
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }

# Helper Functions
def send_notification(user_id, title, message, notification_type, complaint_id=None):
    """Send notification to user"""
    user = User.query.get(user_id)
    if user and user.notifications_enabled:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            complaint_id=complaint_id
        )
        db.session.add(notification)
        
        # Send email notification
        try:
            msg = Message(
                title,
                sender=app.config['MAIL_USERNAME'],
                recipients=[user.email]
            )
            msg.body = message
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
        
        db.session.commit()

def send_admin_notification(title, message, complaint_id=None):
    """Send notification to admin"""
    admin_email = 'iamqwertyui11@gmail.com'
    try:
        msg = Message(
            title,
            sender=app.config['MAIL_USERNAME'],
            recipients=[admin_email]
        )
        msg.body = message
        mail.send(msg)
        print(f"Admin notification sent to {admin_email} for complaint #{complaint_id}")
    except Exception as e:
        print(f"Failed to send admin notification: {e}")

def get_department_contact(city_name, department_name):
    """Get department contact information for a specific city"""
    city = City.query.filter_by(name=city_name).first()
    if city:
        contact = DepartmentContact.query.filter_by(
            city_id=city.id,
            department_name=department_name
        ).first()
        return contact
    return None

def find_similar_complaints(latitude, longitude, title, description, city):
    """Find similar complaints based on location and content."""
    if not (latitude and longitude):
        return None
    
    # Find complaints within 100 meters in the same city
    nearby_complaints = Complaint.query.filter(
        Complaint.latitude.isnot(None),
        Complaint.longitude.isnot(None),
        Complaint.parent_complaint_id.is_(None),  # Only check parent complaints
        Complaint.city == city
    ).all()
    
    similar_complaints = []
    for complaint in nearby_complaints:
        distance = geodesic(
            (latitude, longitude),
            (complaint.latitude, complaint.longitude)
        ).meters
        
        if distance <= 100:  # Within 100 meters
            similar_complaints.append(complaint)
    
    if similar_complaints:
        # Find the most upvoted similar complaint to use as thread parent
        return max(similar_complaints, key=lambda x: x.upvotes)
    return None

geolocator = Nominatim(user_agent="city_samadhan")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as admin to access this page.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') and not session.get('admin_logged_in'):
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['logged_in'] = True  # Set the logged_in flag
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        if otp == session.get('otp'):
            session['logged_in'] = True  # Set the logged_in flag after OTP verification
            flash('OTP verified successfully!')
            return redirect(url_for('dashboard'))
        flash('Invalid OTP!')
    return render_template('verify_otp.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        
        if not User.query.filter_by(email=email).first():
            user = User(
                name=name,
                email=email,
                phone=phone,
                password=password,
                city=city,
                state=state,
                notifications_enabled=True
            )
            db.session.add(user)
            db.session.commit()
            
            # Welcome notification
            send_notification(
                user.id,
                "Welcome to City Samadhan",
                f"Welcome {name}! Thank you for joining City Samadhan. Start by submitting your first complaint or browsing existing issues in your area.",
                "welcome"
            )
            
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
        flash("Email already registered!")
    
    # Format cities data for the template
    formatted_cities = []
    for state, cities in INDIAN_CITIES['states'].items():
        for city in cities:
            formatted_cities.append({
                'id': f"{state}_{city}",
                'name': city,
                'state': state
            })
    
    return render_template(
        'register.html',
        states=INDIAN_CITIES['states'].keys(),
        cities=formatted_cities
    )

@app.route('/get_department_contact')
def get_department_contact_route():
    city = request.args.get('city')
    department = request.args.get('department')
    contact = get_department_contact(city, department)
    if contact:
        return jsonify({
            'email': contact.email,
            'toll_free_number': contact.toll_free_number,
            'office_address': contact.office_address
        })
    return jsonify(None)

@app.route('/report_complaint/<int:complaint_id>', methods=['POST'])
def report_complaint(complaint_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Login required'}), 401
    
    data = request.get_json()
    reason = data.get('reason')
    
    if not reason:
        return jsonify({'error': 'Reason is required'}), 400
    
    report = Report(
        user_id=session['user_id'],
        complaint_id=complaint_id,
        reason=reason
    )
    db.session.add(report)
    db.session.commit()
    
    # Notify moderators (you can implement this later)
    return jsonify({'message': 'Report submitted successfully'})

@app.route('/submit_complaint', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    if request.method == 'POST':
        # Verify user still exists in database
        user = User.query.get(session.get('user_id'))
        if not user:
            session.clear()  # Clear invalid session
            flash('Your session has expired. Please log in again.')
            return redirect(url_for('login'))
            
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        state = request.form.get('state')
        city = request.form.get('city')
        department = request.form.get('department')
        map_location = request.form.get('map_location')
        phone_number = request.form.get('phone_number')
        photo = request.files.get('photo')
        
        # Check for similar complaints in the same location
        similar_complaints = Complaint.query.filter(
            Complaint.location == location,
            Complaint.city == city,
            Complaint.state == state,
            Complaint.department == department,
            Complaint.parent_complaint_id.is_(None)  # Only check parent complaints
        ).all()
        
        # Create new complaint
        complaint = Complaint(
            title=title,
            description=description,
            location=location,
            state=state,
            city=city,
            department=department,
            map_location=map_location,
            phone_number=phone_number,
            user_id=session['user_id']
        )
        
        # Handle photo upload
        if photo:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            complaint.photo = filename
            
        # If similar complaints exist, add this as a reply to the most recent one
        if similar_complaints:
            parent_complaint = similar_complaints[0]  # Use the most recent similar complaint
            complaint.parent_complaint_id = parent_complaint.id
            parent_complaint.thread_count += 1
            db.session.add(complaint)
            db.session.commit()
            
            # Send notification to user
            send_notification(
                user.id,
                "Complaint Registered",
                f"Your complaint '{complaint.title}' has been registered and added as a follow-up to an existing complaint (#{parent_complaint.id}).",
                "complaint_registered",
                complaint.id
            )
            
            # Send email confirmation to user
            try:
                msg = Message(
                    f'Complaint Registered - {complaint.title}',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[user.email]
                )
                msg.body = f"""
Dear {user.name},

Your complaint has been successfully registered with City Samadhan.

Complaint Details:
- ID: #{complaint.id}
- Title: {complaint.title}
- Location: {complaint.location}, {complaint.city}, {complaint.state}
- Department: {complaint.department}
- Status: {complaint.status}

This complaint has been added as a follow-up to an existing similar complaint (#{parent_complaint.id}).

You can track the progress of your complaint by logging into your dashboard at:
http://localhost:5001/dashboard

Thank you for helping make our city better!

Best regards,
City Samadhan Team
                """
                mail.send(msg)
                print(f"Email sent to {user.email} for complaint #{complaint.id}")
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            # Send admin notification for follow-up complaint
            send_admin_notification(
                f'New Follow-up Complaint - {complaint.title}',
                f"""
A new follow-up complaint has been registered.

Complaint Details:
- ID: #{complaint.id}
- Title: {complaint.title}
- Location: {complaint.location}, {complaint.city}, {complaint.state}
- Department: {complaint.department}
- Description: {complaint.description}
- User: {user.name} ({user.email})
- Phone: {complaint.phone_number or 'Not provided'}
- Map Location: {complaint.map_location or 'Not provided'}

This complaint has been added as a follow-up to complaint #{parent_complaint.id}.

Please review and update the status as needed.
                """,
                complaint.id
            )
            
            return redirect(url_for('view_complaint', complaint_id=parent_complaint.id))
        
        # If no similar complaints, create a new thread
        db.session.add(complaint)
        db.session.commit()
        
        # Send notification to user
        send_notification(
            user.id,
            "Complaint Registered",
            f"Your complaint '{complaint.title}' has been successfully registered with ID #{complaint.id}.",
            "complaint_registered",
            complaint.id
        )
        
        # Send email confirmation to user
        try:
            msg = Message(
                f'Complaint Registered - {complaint.title}',
                sender=app.config['MAIL_USERNAME'],
                recipients=[user.email]
            )
            msg.body = f"""
Dear {user.name},

Your complaint has been successfully registered with City Samadhan.

Complaint Details:
- ID: #{complaint.id}
- Title: {complaint.title}
- Location: {complaint.location}, {complaint.city}, {complaint.state}
- Department: {complaint.department}
- Status: {complaint.status}

You can track the progress of your complaint by logging into your dashboard at:
http://localhost:5001/dashboard

Thank you for helping make our city better!

Best regards,
City Samadhan Team
            """
            mail.send(msg)
            print(f"Email sent to {user.email} for complaint #{complaint.id}")
        except Exception as e:
            print(f"Failed to send email: {e}")
        
        # Send admin notification for new complaint
        send_admin_notification(
            f'New Complaint Registered - {complaint.title}',
            f"""
A new complaint has been registered in the system.

Complaint Details:
- ID: #{complaint.id}
- Title: {complaint.title}
- Location: {complaint.location}, {complaint.city}, {complaint.state}
- Department: {complaint.department}
- Description: {complaint.description}
- User: {user.name} ({user.email})
- Phone: {complaint.phone_number or 'Not provided'}
- Map Location: {complaint.map_location or 'Not provided'}
- Status: {complaint.status}

Please review and assign to the appropriate department if needed.
            """,
            complaint.id
        )
        
        return redirect(url_for('view_complaint', complaint_id=complaint.id))
        
    return render_template('submit_complaint.html', states=INDIAN_CITIES['states'].keys())

@app.route('/notifications')
def notifications():
    """Display user notifications"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    notifications = Notification.query.filter_by(
        user_id=session['user_id']
    ).order_by(Notification.timestamp.desc()).all()
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/mark_notification_read/<int:notification_id>')
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    notification.read = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/mark_all_notifications_read')
def mark_all_notifications_read():
    """Mark all notifications as read"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    Notification.query.filter_by(
        user_id=session['user_id'],
        read=False
    ).update({'read': True})
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Verify user still exists in database
    user = User.query.get(session.get('user_id'))
    if not user:
        session.clear()  # Clear invalid session
        flash('Your session has expired. Please log in again.')
        return redirect(url_for('login'))
        
    # Get only the user's complaints
    complaints = Complaint.query.filter_by(user_id=session['user_id']).order_by(Complaint.timestamp.desc()).all()
    return render_template('dashboard.html', complaints=complaints, user=user)

@app.route('/vote/<int:complaint_id>/<vote_type>', methods=['POST'])
def vote(complaint_id, vote_type):
    if not session.get('logged_in') or session.get('admin_logged_in'):
        return jsonify({'error': 'User login required'}), 401
    
    # Verify user still exists in database
    user = User.query.get(session.get('user_id'))
    if not user:
        return jsonify({'error': 'Session expired'}), 401
        
    complaint = Complaint.query.get_or_404(complaint_id)
    user_id = session['user_id']
    
    existing_vote = Vote.query.filter_by(
        user_id=user_id,
        complaint_id=complaint_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            if vote_type == 'upvote':
                complaint.upvotes -= 1
            else:
                complaint.downvotes -= 1
            db.session.delete(existing_vote)
            
            # Notify about vote removal
            send_notification(
                complaint.user_id,
                f"Vote Removed on Your Complaint",
                f"A user has removed their {vote_type} on your complaint: {complaint.title}",
                "vote_update",
                complaint.id
            )
        else:
            if vote_type == 'upvote':
                complaint.upvotes += 1
                complaint.downvotes -= 1
            else:
                complaint.upvotes -= 1
                complaint.downvotes += 1
            existing_vote.vote_type = vote_type
            
            # Notify about vote change
            send_notification(
                complaint.user_id,
                f"Vote Changed on Your Complaint",
                f"A user has changed their vote to {vote_type} on your complaint: {complaint.title}",
                "vote_update",
                complaint.id
            )
    else:
        vote = Vote(
            user_id=user_id,
            complaint_id=complaint_id,
            vote_type=vote_type
        )
        if vote_type == 'upvote':
            complaint.upvotes += 1
        else:
            complaint.downvotes += 1
        db.session.add(vote)
        
        # Notify about new vote
        send_notification(
            complaint.user_id,
            f"New {vote_type.capitalize()} on Your Complaint",
            f"Your complaint '{complaint.title}' received a new {vote_type}",
            "vote_update",
            complaint.id
        )
    
    # Auto-escalate if enough upvotes
    if complaint.upvotes >= 5 and complaint.status == 'Reported':
        complaint.status = 'In Process'
        
        # Notify complaint author about status change
        send_notification(
            complaint.user_id,
            "Complaint Status Updated",
            f"Your complaint '{complaint.title}' has been escalated to 'In Process' due to community support.",
            "status_update",
            complaint.id
        )
        
        # Notify department about escalation
        dept_contact = get_department_contact(complaint.city, complaint.department)
        if dept_contact:
            msg = Message(
                f"Complaint Escalated: {complaint.title}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[dept_contact.email]
            )
            msg.body = f"""
            A complaint has been escalated due to community support:
            Title: {complaint.title}
            Location: {complaint.location}, {complaint.city}
            Status: In Process
            Upvotes: {complaint.upvotes}
            
            Please login to the system to address this complaint.
            """
            mail.send(msg)
    
    db.session.commit()
    return jsonify({
        'upvotes': complaint.upvotes,
        'downvotes': complaint.downvotes,
        'status': complaint.status
    })

@app.route('/complaint/<int:complaint_id>')
@user_or_admin_required
def view_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    user = User.query.get(complaint.user_id)
    
    # Get all replies to this complaint
    replies = Complaint.query.filter_by(parent_complaint_id=complaint_id).order_by(Complaint.timestamp.asc()).all()
    
    # Get the parent complaint if this is a reply
    parent_complaint = None
    if complaint.parent_complaint_id:
        parent_complaint = Complaint.query.get(complaint.parent_complaint_id)
    
    return render_template(
        'view_complaint.html',
        complaint=complaint,
        user=user,
        replies=replies,
        parent_complaint=parent_complaint
    )

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out successfully!')
    return redirect(url_for('login'))

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/all_complaints')
def all_complaints():
    if not session.get('logged_in') and not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of complaints per page
    state = request.args.get('state', '')
    city = request.args.get('city', '')
    department = request.args.get('department', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'newest')
    
    # Build query
    query = Complaint.query
    
    # Apply filters
    if state:
        query = query.filter_by(state=state)
    if city:
        query = query.filter_by(city=city)
    if department:
        query = query.filter_by(department=department)
    if status:
        query = query.filter_by(status=status)
    
    # Apply sorting
    if sort == 'newest':
        query = query.order_by(Complaint.timestamp.desc())
    elif sort == 'oldest':
        query = query.order_by(Complaint.timestamp.asc())
    elif sort == 'most_upvoted':
        query = query.order_by(Complaint.upvotes.desc())
    
    # Get total count and paginate
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    complaints = query.paginate(page=page, per_page=per_page, error_out=False).items
    
    return render_template(
        'all_complaints.html',
        complaints=complaints,
        page=page,
        total_pages=total_pages,
        states=INDIAN_CITIES['states'].keys(),
        cities=INDIAN_CITIES['states'],
        departments=DEPARTMENT_INFO.keys(),
        selected_state=state,
        selected_city=city,
        selected_department=department,
        selected_status=status,
        selected_sort=sort
    )

@app.route('/get_cities/<state>')
def get_cities(state):
    if state in INDIAN_CITIES['states']:
        return jsonify(list(INDIAN_CITIES['states'][state]))
    return jsonify([])

# Admin Routes
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admin.query.filter_by(email=email, password=password).first()
        if admin:
            session['admin_id'] = admin.id
            session['admin_logged_in'] = True
            session['admin_department'] = admin.department
            session['admin_city'] = admin.city
            session['admin_state'] = admin.state
            flash('Admin logged in successfully!')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials!')
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    flash('Admin logged out successfully!')
    return redirect(url_for('admin_login'))

@app.route('/admin_dashboard')
@admin_login_required
def admin_dashboard():
    admin_department = session['admin_department']
    admin_city = session['admin_city']
    admin_state = session['admin_state']
    
    # Get complaints for this admin's department and city
    complaints = Complaint.query.filter_by(
        department=admin_department,
        city=admin_city,
        state=admin_state
    ).order_by(Complaint.timestamp.desc()).all()
    
    return render_template('admin_dashboard.html', complaints=complaints)

@app.route('/update_complaint_status/<int:complaint_id>', methods=['POST'])
@admin_login_required
def update_complaint_status(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check if this admin can update this complaint
    if (complaint.department != session['admin_department'] or 
        complaint.city != session['admin_city'] or 
        complaint.state != session['admin_state']):
        flash('Unauthorized to update this complaint!')
        return redirect(url_for('admin_dashboard'))
    
    new_status = request.form.get('status')
    response_text = request.form.get('response_text', '')
    
    old_status = complaint.status
    complaint.status = new_status
    complaint.status_updated_at = datetime.utcnow()
    
    # Set status-specific timestamps
    if new_status == 'Accepted':
        complaint.accepted_at = datetime.utcnow()
    elif new_status == 'Work in Progress':
        complaint.work_in_progress_at = datetime.utcnow()
    elif new_status == 'Completed':
        complaint.completed_at = datetime.utcnow()
    elif new_status == 'Rejected':
        complaint.rejected_at = datetime.utcnow()
    
    # Create authority response if there's response text
    if response_text:
        response = AuthorityResponse(
            complaint_id=complaint_id,
            response_text=response_text,
            status_update=new_status,
            department_name=session['admin_department'],
            officer_name=Admin.query.get(session['admin_id']).name
        )
        db.session.add(response)
    
    db.session.commit()
    
    # Send notification to user
    status_messages = {
        'Accepted': f'Your complaint "{complaint.title}" has been accepted by {session["admin_department"]}.',
        'Work in Progress': f'Work has started on your complaint "{complaint.title}".',
        'Completed': f'Your complaint "{complaint.title}" has been completed.',
        'Rejected': f'Your complaint "{complaint.title}" has been rejected by {session["admin_department"]}.'
    }
    
    if new_status in status_messages:
        send_notification(
            complaint.user_id,
            f'Complaint Status Update: {new_status}',
            status_messages[new_status],
            'status_update',
            complaint.id
        )
    
    flash(f'Complaint status updated to {new_status}!')
    return redirect(url_for('admin_dashboard'))

@app.route('/submit_feedback/<int:complaint_id>', methods=['POST'])
@login_required
def submit_feedback(complaint_id):
    # Verify user still exists in database
    user = User.query.get(session.get('user_id'))
    if not user:
        session.clear()  # Clear invalid session
        flash('Your session has expired. Please log in again.')
        return redirect(url_for('login'))
        
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.user_id != session.get('user_id'):
        flash('Unauthorized to submit feedback for this complaint.')
        return redirect(url_for('view_complaint', complaint_id=complaint_id))

    if complaint.status not in ['Completed', 'Rejected']:
        flash('Feedback can only be submitted after work is Completed or Rejected.')
        return redirect(url_for('view_complaint', complaint_id=complaint_id))

    feedback_text = request.form.get('feedback_text', '').strip()
    if not feedback_text:
        flash('Please enter feedback text before submitting.')
        return redirect(url_for('view_complaint', complaint_id=complaint_id))

    complaint.feedback = feedback_text
    complaint.feedback_timestamp = datetime.utcnow()
    db.session.commit()

    send_notification(
        complaint.user_id,
        'Feedback Submitted',
        f'Thanks for your feedback on complaint "{complaint.title}".',
        'feedback',
        complaint.id
    )

    send_admin_notification(
        'User Feedback Received',
        f"User feedback received for complaint #{complaint.id} (status: {complaint.status}):\n\n{feedback_text}",
        complaint.id
    )

    flash('Feedback submitted successfully.')
    return redirect(url_for('view_complaint', complaint_id=complaint_id))

if __name__ == '__main__':
    app.run(debug=True, port=5001)