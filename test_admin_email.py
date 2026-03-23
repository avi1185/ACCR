from app import app, send_admin_notification

def test_admin_notification():
    """Test admin notification function"""
    with app.app_context():
        try:
            send_admin_notification(
                'Test Admin Notification',
                'This is a test notification to verify admin email functionality.',
                123
            )
            print("Admin notification test completed successfully!")
            return True
        except Exception as e:
            print(f"Admin notification test failed: {e}")
            return False

if __name__ == "__main__":
    test_admin_notification()