# app/models/horse_image.py

from app.extensions import db

class HorseImage(db.Model):
    __tablename__ = 'horse_images'

    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    horse = db.relationship('Horse', backref=db.backref('images', lazy=True))
