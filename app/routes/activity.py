# routes/activity.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.horse import Horse
from app.models.horse_activity import HorseActivity
from app.utils.jwt_utils import token_required
from flask import g

activity_bp = Blueprint('activity', __name__)

@activity_bp.route("/horses/<int:horse_id>/activity", methods=["POST"])
@token_required
def add_activity(horse_id):
    data = request.json
    horse = Horse.query.filter_by(id=horse_id, owner_id=g.user_id).first()
    if not horse:
        return jsonify({"message": "Horse not found or not yours"}), 404

    activity = HorseActivity(
        horse_id=horse.id,
        activity_type=data.get("activity_type"),
        duration=data.get("duration"),
        trainer_name=data.get("trainer_name"),
        intensity_level=data.get("intensity_level"),
        location=data.get("location"),
        notes=data.get("notes"),
        attachment=data.get("attachment")
    )
    db.session.add(activity)
    db.session.commit()
    return jsonify({"message": "Activity added successfully"}), 201

@activity_bp.route("/horses/<int:horse_id>/activity", methods=["GET"])
@token_required
def get_activities(horse_id):
    horse = Horse.query.filter_by(id=horse_id, owner_id=g.user_id).first()
    if not horse:
        return jsonify({"message": "Horse not found or not yours"}), 404

    result = []
    for a in horse.activities:
        result.append({
            "id": a.id,
            "type": a.activity_type,
            "duration": a.duration,
            "trainer_name": a.trainer_name,
            "intensity_level": a.intensity_level,
            "location": a.location,
            "notes": a.notes,
            "attachment": a.attachment,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(result), 200

@activity_bp.route("/activity/<int:activity_id>", methods=["PUT"])
@token_required
def edit_activity(activity_id):
    data = request.json
    activity = HorseActivity.query.get(activity_id)
    if not activity or activity.horse.owner_id != g.user_id:
        return jsonify({"message": "Activity not found or not authorized"}), 404

    activity.activity_type = data.get("activity_type", activity.activity_type)
    activity.duration = data.get("duration", activity.duration)
    activity.trainer_name = data.get("trainer_name", activity.trainer_name)
    activity.intensity_level = data.get("intensity_level", activity.intensity_level)
    activity.location = data.get("location", activity.location)
    activity.notes = data.get("notes", activity.notes)
    activity.attachment = data.get("attachment", activity.attachment)

    db.session.commit()
    return jsonify({"message": "Activity updated"}), 200

@activity_bp.route("/activity/<int:activity_id>", methods=["DELETE"])
@token_required
def delete_activity(activity_id):
    activity = HorseActivity.query.get(activity_id)
    if not activity or activity.horse.owner_id != g.user_id:
        return jsonify({"message": "Activity not found or not authorized"}), 404

    db.session.delete(activity)
    db.session.commit()
    return jsonify({"message": "Activity deleted"}), 200
