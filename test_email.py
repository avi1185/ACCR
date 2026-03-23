from app import app, mail
from flask_mail import Message

def test_email():
    with app.app_context():
        try:
            msg = Message(
                'Test Email from City Samadhan',
                sender=app.config['MAIL_USERNAME'],
                recipients=['hakyakrudost@gmail.com']  # Send to yourself for testing
            )
            msg.body = """
This is a test email to verify that the email functionality is working correctly.

If you receive this email, the email configuration is working properly.

Best regards,
City Samadhan Test
            """
            mail.send(msg)
            print("Test email sent successfully!")
            return True
        except Exception as e:
            print(f"Failed to send test email: {e}")
            return False

if __name__ == "__main__":
    test_email()