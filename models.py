from datetime import datetime
from app import db

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # status_update, vote_update, thread_update, etc.
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    complaint = db.relationship('Complaint', backref=db.backref('notifications', lazy=True)) 