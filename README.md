# ACCR - Civic Complaint Management System

ACCR is a comprehensive civic complaint management system that empowers citizens to report, track, and resolve urban issues. Built with Flask and Python, this platform bridges the gap between citizens and municipal authorities by providing an efficient channel for reporting city-related problems.

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

### User Management
- User registration with email verification
- Secure login/logout functionality
- Profile management
- Notification preferences

### Complaint Management
- Submit complaints with detailed descriptions
- Attach photos to complaints
- Optional map location and phone number fields
- Track complaint status in real-time
- View all complaints in the system
- Filter and sort complaints by various criteria
- Threaded conversations for similar complaints

### Admin Portal
- Dedicated admin login for department officials
- Admin dashboard for managing complaints
- Status update functionality
- Department-specific complaint filtering
- Phone number visibility for admins only

### Voting System
- Upvote/downvote complaints to show community support
- Automatic escalation of highly supported complaints
- Community-driven prioritization of issues

### Department Integration
- Comprehensive database of municipal departments
- Direct contact information for each department
- Automated notifications to relevant authorities

### Notification System
- Real-time notifications for complaint updates
- Email notifications for complaint registration
- In-app notification center
- Configurable notification preferences

## Technology Stack

- **Backend**: Python 3.13, Flask 2.3.3
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
- **ORM**: SQLAlchemy 1.4.49
- **Email**: Flask-Mail for notification system
- **Geolocation**: GeoPy for location services
- **Deployment**: Flask development server (development), WSGI server (production)

## Project Structure

```
ACCR/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── init_db.py             # Database initialization script
├── check_db.py            # Database verification script
├── populate_cities.py     # City data population script
├── populate_departments.py # Department data population script
├── populate_admins.py     # Admin user population script
├── indian_cities.json     # JSON data for Indian cities
├── requirements.txt       # Python dependencies
├── test_app.py            # Application test suite
├── test_email.py          # Email functionality test
├── test_admin.py          # Admin functionality test
├── README.md             # Project documentation
├── .gitignore            # Git ignore file
├── static/               # Static assets
│   ├── css/              # Stylesheets
│   │   └── style.css     # Main stylesheet
│   ├── script.js         # Client-side JavaScript
│   └── uploads/          # User uploaded images
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── dashboard.html    # User dashboard
    ├── submit_complaint.html # Complaint submission form
    ├── view_complaint.html   # Individual complaint view
    ├── all_complaints.html   # All complaints listing
    ├── notifications.html    # Notification center
    ├── admin_login.html      # Admin login page
    ├── admin_dashboard.html  # Admin dashboard
    ├── privacy.html          # Privacy policy
    └── terms.html            # Terms of service
```

## Installation

### Prerequisites
- Python 3.13 or higher
- pip package manager
- Git (optional, for version control)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ACCR.git
   cd ACCR
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

The application uses SQLite for development. To set up the database:

1. **Initialize the database**:
   ```bash
   python init_db.py
   ```

2. **Populate with city data**:
   ```bash
   python populate_cities.py
   ```

3. **Populate with department data**:
   ```bash
   python populate_departments.py
   ```

4. **Populate with admin users**:
   ```bash
   python populate_admins.py
   ```

5. **Verify the database**:
   ```bash
   python check_db.py
   ```

## Running the Application

1. **Start the Flask development server**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   Open your web browser and navigate to `http://127.0.0.1:5000`

3. **Default credentials** (if you've added test data):
   - Email: test@example.com
   - Password: testpassword

## Usage

### For Citizens
1. **Register** for a new account
2. **Verify** your email address
3. **Log in** to your account
4. **Submit complaints** with detailed information, photos, and optional location data
5. **Track** the status of your complaints
6. **Vote** on other complaints to show support
7. **Receive notifications** about complaint updates via email and in-app notifications

### For Administrators
1. **Log in** using admin credentials (iamqwertyui11@gmail.com / admin123 for road complaints)
2. **Access** the admin dashboard to view complaints specific to your department
3. **Update** complaint statuses (Pending, In Progress, Resolved, Closed)
4. **View** phone numbers and contact information for follow-up
5. **Monitor** complaint threads and community engagement
6. **Receive** email notifications for all new complaints in the system

### Email Notifications
- **Complaint Registration**: Users receive email confirmations when complaints are submitted
- **Admin Notifications**: Admin (iamqwertyui11@gmail.com) receives email alerts for all new complaints
- **Follow-up Complaint Emails**: When similar complaints are grouped as follow-ups, users get notified
- **Welcome Emails**: New users receive welcome messages upon registration

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Complaints
- `GET /dashboard` - User dashboard
- `GET /submit_complaint` - Complaint submission form
- `POST /submit_complaint` - Submit a new complaint
- `GET /complaint/<int:complaint_id>` - View a specific complaint
- `GET /all_complaints` - View all complaints
- `POST /vote/<int:complaint_id>/<vote_type>` - Vote on a complaint

### Notifications
- `GET /notifications` - View notifications
- `GET /mark_notification_read/<int:notification_id>` - Mark notification as read
- `GET /mark_all_notifications_read` - Mark all notifications as read

### Utilities
- `GET /get_cities/<state>` - Get cities for a specific state
- `GET /get_department_contact` - Get department contact information

## Configuration

The application can be configured through environment variables or by modifying the `app.py` file:

```python
app.config.update(
    SECRET_KEY='your-secret-key',
    SQLALCHEMY_DATABASE_URI='sqlite:///database.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER='static/uploads',
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='your-email@gmail.com',
    MAIL_PASSWORD='your-app-password'
)
```
# ACCR - Complaint Management System for Citizen

ACCR is a web-based Complaint Management System for Citizen built to bridge the gap between citizens and civic authorities. Empowering citizens to resolve civic issues efficiently and transparently.
It enables users to report, track, and discuss civic issues in their cities while providing departments with tools to address complaints effectively. 

# Key Features ✨_

__User Management 👤__

-> User registration & login with OTP verification 🔐

-> Profiles with city, state & notification prefs 🏙

__Complaint Management 📢__

-> Submit complaints: title, desc, pics, GPS & dept 📸

-> Track status in real-time ⏳

-> Thread discussions for collab 🗣

__Department Integration 🏢__

-> Contact deets: toll-free, emails, locations 📞

-> Dept-wise complaint workflows ⚙


__Interactive Features 🎉__

-> Upvote/downvote complaints 👍👎

-> Report bad content 🚨

-> Detect similar issues 🔍

__Notification System 🔔__

-> Real-time alerts: status, replies, updates ⚡

-> Email + in-app notifications 📧

__Geographic Features 🌍__

-> City & state organization 🗺

-> Location tracking + nearby complaint detection 📍

__Security 🔒__

-> Secure login & session mgmt 🛡

-> Safe file uploads 📤


__Tech Stack </>__

-> Backend: Flask (Python)

-> Database: SQLite with SQLAlchemy ORM

-> Frontend: HTML, CSS, JavaScript

-> Email: Flask-Mail

-> Geolocation: Geopy

-> File Handling: Werkzeug
