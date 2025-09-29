from app.extensions import db
from datetime import datetime


class FamilyTree(db.Model):
    __tablename__ = 'family_tree'

    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('family_tree.id'), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_root = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    children = db.relationship('FamilyTree', backref=db.backref('parent', remote_side=[id]), lazy=True)
    horse = db.relationship('Horse', backref='family_tree', uselist=False)
    owner = db.relationship('User', backref='family_trees')

    def to_dict(self):
        return {
            "id": self.id,
            "horse_id": self.horse_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "owner_id": self.owner_id,
            "is_root": self.is_root,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "children": [child.to_dict() for child in self.children]
        }