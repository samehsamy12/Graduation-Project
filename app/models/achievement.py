from datetime import datetime
from app.extensions import db 

class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    badge = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'horse_id': self.horse_id,
            'title': self.title,
            'desc': self.desc,
            'icon': self.icon,
            'type': self.type,
            'badge': self.badge,
            'date': self.date.strftime('%Y-%m-%d')
        }
