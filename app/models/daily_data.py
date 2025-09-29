from app.extensions import db
from datetime import datetime

class DailyData(db.Model):
    __tablename__ = 'daily_data'

    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)

    food_type = db.Column(db.String(100))
    meals_number = db.Column(db.Integer)
    water_intake = db.Column(db.Boolean)
    water_amount = db.Column(db.Float)

    exercised = db.Column(db.Boolean)
    activity_type = db.Column(db.String(100))
    exercise_duration = db.Column(db.Integer)

    poop_quality = db.Column(db.String(20))

    temperature = db.Column(db.Float)
    appetite = db.Column(db.String(20))
    energy_level = db.Column(db.String(20))
    mood = db.Column(db.String(20))
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    horse = db.relationship("Horse", backref="daily_records")
