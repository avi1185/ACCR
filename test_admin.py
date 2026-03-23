import requests
from app import app, db, Admin

def test_admin_login():
    """Test admin login functionality"""
    with app.test_client() as client:
        # Test admin login
        response = client.post('/admin_login', data={
            'email': 'iamqwertyui11@gmail.com',
            'password': 'admin123'
        }, follow_redirects=True)

        if response.status_code == 200:
            print("Admin login successful!")
            # Check if we can access the admin dashboard
            dashboard_response = client.get('/admin_dashboard')
            if dashboard_response.status_code == 200:
                print("Admin dashboard access successful!")
                return True
            else:
                print(f"Admin dashboard access failed with status code: {dashboard_response.status_code}")
                return False
        else:
            print(f"Admin login failed with status code: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
            return False

if __name__ == "__main__":
    test_admin_login()