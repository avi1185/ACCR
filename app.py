from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
import random
import string
from datetime import datetime
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
    status = db.Column(db.String(50), default='Reported')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=True)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    photo = db.Column(db.String(200))
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
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        state = request.form.get('state')
        city = request.form.get('city')
        department = request.form.get('department')
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
            return redirect(url_for('view_complaint', complaint_id=parent_complaint.id))
        
        # If no similar complaints, create a new thread
        db.session.add(complaint)
        db.session.commit()
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
    # Get user object
    user = User.query.get(session['user_id'])
    # Get only the user's complaints
    complaints = Complaint.query.filter_by(user_id=session['user_id']).order_by(Complaint.timestamp.desc()).all()
    return render_template('dashboard.html', complaints=complaints, user=user)

@app.route('/vote/<int:complaint_id>/<vote_type>', methods=['POST'])
def vote(complaint_id, vote_type):
    if not session.get('logged_in'):
        return jsonify({'error': 'Login required'}), 401
    
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
@login_required
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
    if not session.get('logged_in'):
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)