from app.extensions import db
from datetime import datetime

class Horse(db.Model):
    __tablename__ = 'horses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)  # Store as dd-mm-yyyy
    sire = db.Column(db.String(150), nullable=True)
    dam = db.Column(db.String(150), nullable=True)
    coat = db.Column(db.String(50), nullable=True)
    blood_type = db.Column(db.String(50), nullable=True)
    national_id = db.Column(db.String(50), unique=True, nullable=True)
    horse_id = db.Column(db.String(50), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(200), nullable=True)

    owner = db.relationship('User', backref='horses')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "sire": self.sire,
            "dam": self.dam,
            "coat": self.coat,
            "blood_type": self.blood_type,
            "national_id": self.national_id,
            "horse_id": self.horse_id,
            "owner_id": self.owner_id,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "image_url": self.image_url,
        }