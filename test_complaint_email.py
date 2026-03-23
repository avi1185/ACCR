import requests
from app import app, db, User
import tempfile
import os
import random
import string

def generate_random_email():
    """Generate a random email for testing"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"

def test_complaint_submission_with_email():
    """Test complaint submission with email notification"""
    with app.test_client() as client:
        with app.app_context():
            # Create a test user first
            user = User(
                name="Test User",
                email=generate_random_email(),
                phone="1234567890",
                password="testpassword",
                city="Mumbai",
                state="Maharashtra"
            )
            db.session.add(user)
            db.session.commit()

            # Log in the user
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['user_email'] = user.email

            # Submit a complaint
            response = client.post('/submit_complaint', data={
                'title': 'Test Complaint with Admin Email',
                'description': 'This is a test complaint to verify admin email notifications work',
                'location': 'Test Location',
                'state': 'Maharashtra',
                'city': 'Mumbai',
                'department': 'Public Works Department',
                'map_location': '19.0760, 72.8777',  # Mumbai coordinates
                'phone_number': '9876543210'
            }, follow_redirects=True)

            if response.status_code == 200:
                print("Complaint submitted successfully!")
                print("Check both user and admin emails for notifications.")
                return True
            else:
                print(f"Complaint submission failed with status code: {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)}")
                return False

if __name__ == "__main__":
    test_complaint_submission_with_email()