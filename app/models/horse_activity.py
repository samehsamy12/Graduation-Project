# models/horse_activity.py
from app.extensions import db
from datetime import datetime

class HorseActivity(db.Model):
    __tablename__ = 'horse_activities'

    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    trainer_name = db.Column(db.String(100), nullable=True)
    intensity_level = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    attachment = db.Column(db.String(255), nullable=True)  # URL or filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    horse = db.relationship('Horse', backref='activities')
