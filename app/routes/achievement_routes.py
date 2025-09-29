from flask import Blueprint, request, jsonify
from app.models.achievement import Achievement
from app.extensions import db

achievement_bp = Blueprint('achievement', __name__)

@achievement_bp.route('/achievements/<int:horse_id>', methods=['GET'])
def get_achievements(horse_id):
    achievements = Achievement.query.filter_by(horse_id=horse_id).all()
    return jsonify([a.to_dict() for a in achievements])

@achievement_bp.route('/achievements', methods=['POST'])
def add_achievement():
    data = request.get_json()
    new_achievement = Achievement(
        horse_id=data['horse_id'],
        title=data['title'],
        desc=data['desc'],
        icon=data['icon'],
        type=data['type'],
        badge=data['badge']
    )
    db.session.add(new_achievement)
    db.session.commit()
    return jsonify(new_achievement.to_dict()), 201
