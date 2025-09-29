from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.utils.jwt_utils import token_required
from app.models.daily_data import DailyData
from app.models.horse import Horse
from datetime import datetime

daily_bp = Blueprint("daily", __name__)

@daily_bp.route("/horses/<int:horse_id>/daily", methods=["POST"])
@token_required
def add_daily_data(horse_id):
    data = request.json

    if not Horse.query.filter_by(id=horse_id, owner_id=g.user_id).first():
        return jsonify({"message": "Horse not found or not yours"}), 404

    date_str = data.get("date")
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()
    except ValueError:
        return jsonify({"message": "Invalid date format, use YYYY-MM-DD"}), 400

    existing = DailyData.query.filter_by(horse_id=horse_id, date=selected_date).first()
    
    if existing:
        existing.food_type = data.get("food_type")
        existing.meals_number = data.get("meals_number")
        existing.water_intake = data.get("water_intake")
        existing.water_amount = data.get("water_amount")
        existing.exercised = data.get("exercised")
        existing.activity_type = data.get("activity_type")
        existing.exercise_duration = data.get("exercise_duration")
        existing.poop_quality = data.get("poop_quality")
        existing.temperature = data.get("temperature")
        existing.appetite = data.get("appetite")
        existing.energy_level = data.get("energy_level")
        existing.mood = data.get("mood")
        existing.notes = data.get("notes")
        message = "Daily data updated"
    else:
        daily = DailyData(
            horse_id=horse_id,
            date=selected_date,
            food_type=data.get("food_type"),
            meals_number=data.get("meals_number"),
            water_intake=data.get("water_intake"),
            water_amount=data.get("water_amount"),
            exercised=data.get("exercised"),
            activity_type=data.get("activity_type"),
            exercise_duration=data.get("exercise_duration"),
            poop_quality=data.get("poop_quality"),
            temperature=data.get("temperature"),
            appetite=data.get("appetite"),
            energy_level=data.get("energy_level"),
            mood=data.get("mood"),
            notes=data.get("notes"),
        )
        message = "Daily data recorded successfully"
        db.session.add(daily)
    
    db.session.commit()

    return jsonify({"message": message}), 201

@daily_bp.route("/horses/<int:horse_id>/daily", methods=["GET"])
@token_required
def get_daily_data(horse_id):
    if not Horse.query.filter_by(id=horse_id, owner_id=g.user_id).first():
        return jsonify({"message": "Horse not found or not yours"}), 404

    date_str = request.args.get("date")
    query = DailyData.query.filter_by(horse_id=horse_id)

    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter_by(date=selected_date)
        except ValueError:
            return jsonify({"message": "Invalid date format, use YYYY-MM-DD"}), 400

    records = query.order_by(DailyData.date.desc()).all()
    return jsonify([
        {
            "date": r.date.isoformat(),
            "food_type": r.food_type,
            "meals_number": r.meals_number,
            "water_intake": r.water_intake,
            "water_amount": r.water_amount,
            "exercised": r.exercised,
            "activity_type": r.activity_type,
            "exercise_duration": r.exercise_duration,
            "poop_quality": r.poop_quality,
            "temperature": r.temperature,
            "appetite": r.appetite,
            "energy_level": r.energy_level,
            "mood": r.mood,
            "notes": r.notes,
        } for r in records
    ])