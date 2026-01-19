import requests
import json
from app import app, db, User, Complaint

def test_app():
    with app.app_context():
        # Test database connection
        try:
            user_count = User.query.count()
            complaint_count = Complaint.query.count()
            print(f"Database connection successful!")
            print(f"Users in database: {user_count}")
            print(f"Complaints in database: {complaint_count}")
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

        # Test creating a user
        try:
            user = User(
                name="Test User",
                email="test@example.com",
                phone="1234567890",
                password="testpassword",
                city="Mumbai",
                state="Maharashtra"
            )
            db.session.add(user)
            db.session.commit()
            print("User creation successful!")
        except Exception as e:
            print(f"User creation failed: {e}")
            return False

        # Test creating a complaint
        try:
            complaint = Complaint(
                title="Test Complaint",
                description="This is a test complaint",
                location="Test Location",
                state="Maharashtra",
                city="Mumbai",
                department="Electricity Board",
                user_id=user.id
            )
            db.session.add(complaint)
            db.session.commit()
            print("Complaint creation successful!")
        except Exception as e:
            print(f"Complaint creation failed: {e}")
            return False

        print("All tests passed!")
        return True

if __name__ == '__main__':
    test_app()