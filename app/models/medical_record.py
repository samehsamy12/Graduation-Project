from app.extensions import db
from datetime import datetime
import enum

class RecordTypeEnum(enum.Enum):
    vaccination = "vaccination"
    medication = "medication"
    surgery = "surgery"
    checkup = "checkup"
    lab = "lab"
    other = "other"

class MedicalRecord(db.Model):
    __tablename__ = "medical_records"

    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey("horses.id"), nullable=False)
    record_type = db.Column(db.Enum(RecordTypeEnum), nullable=False)
    details = db.Column(db.String(500), nullable=False)  # Changed to String
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    horse = db.relationship("Horse", backref="medical_records")