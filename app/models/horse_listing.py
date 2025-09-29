from app.extensions import db
from datetime import datetime

class HorseListing(db.Model):
    __tablename__ = 'horse_listings'

    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)  # Used for description and contact info
    image_url = db.Column(db.String(255), nullable=True)  # Added for image URL
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    horse = db.relationship("Horse", backref="listing", uselist=False)
    seller = db.relationship("User", backref="listings")