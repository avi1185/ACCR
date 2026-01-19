<<<<<<< HEAD
# CitySamadhan - Civic Complaint Management System

CitySamadhan is a comprehensive civic complaint management system that empowers citizens to report, track, and resolve urban issues. Built with Flask and Python, this platform bridges the gap between citizens and municipal authorities by providing an efficient channel for reporting city-related problems.

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
- Track complaint status in real-time
- View all complaints in the system
- Filter and sort complaints by various criteria

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
- Email notifications for important events
- In-app notification center

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
CitySamadhan/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── init_db.py             # Database initialization script
├── check_db.py            # Database verification script
├── populate_cities.py     # City data population script
├── populate_departments.py # Department data population script
├── indian_cities.json     # JSON data for Indian cities
├── requirements.txt       # Python dependencies
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
   git clone https://github.com/your-username/CitySamadhan.git
   cd CitySamadhan
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

4. **Verify the database**:
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
4. **Submit complaints** with detailed information and photos
5. **Track** the status of your complaints
6. **Vote** on other complaints to show support
7. **Receive notifications** about complaint updates

### For Administrators
1. **Monitor** all complaints in the system
2. **Assign** complaints to relevant departments
3. **Update** complaint statuses
4. **Respond** to citizens through the notification system

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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email hakyakrudost@gmail.com or open an issue in the GitHub repository.

## Acknowledgments

- Thanks to all contributors who have helped develop this project
- Inspired by the need for better civic engagement platforms
- Built with the Flask microframework and SQLAlchemy ORM
=======
# CitySamadhan - Complaint Management System for Citizen

CitySamadhan is a web-based Complaint Management System for Citizen built to bridge the gap between citizens and civic authorities. Empowering citizens to resolve civic issues efficiently and transparently.
It enables users to report, track, and discuss civic issues in their cities while providing departments with tools to address complaints effectively. Developed during "Code - ए - Manipal", this project leverages modern web technologies to create a scalable, user-friendly solution for urban governance.



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
>>>>>>> 9798a06cdcd79ddf59f3988906a1cad67b514602
