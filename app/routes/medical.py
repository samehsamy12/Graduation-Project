from flask import Blueprint, request, jsonify, g
from app.models.medical_record import MedicalRecord, RecordTypeEnum
from app.extensions import db
from app.utils.jwt_utils import token_required
from datetime import datetime
from app.routes.horse_routes import Horse

medical_bp = Blueprint("medical", __name__)

@medical_bp.route("/medical", methods=["POST"])
@token_required
def add_medical_record():
    data = request.json
    horse_id = data.get("horse_id")
    record_type = data.get("record_type")
    details = data.get("details")

    if not all([horse_id, record_type, details]):
        return jsonify({"message": "Missing required fields"}), 400

    if record_type not in RecordTypeEnum.__members__:
        return jsonify({"message": "Invalid record type"}), 400

    record = MedicalRecord(
        horse_id=horse_id,
        record_type=RecordTypeEnum[record_type],
        details=details  # Store as string
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({
        "message": "Medical record added successfully",
        "record_id": record.id
    }), 201

@medical_bp.route("/medical/<int:horse_id>", methods=["GET"])
@token_required
def list_medical_records(horse_id):
    record_type = request.args.get("type")
    records_query = MedicalRecord.query.filter_by(horse_id=horse_id)

    if record_type and record_type in RecordTypeEnum.__members__:
        records_query = records_query.filter_by(record_type=RecordTypeEnum[record_type])

    records = records_query.order_by(MedicalRecord.created_at.desc()).all()
    return jsonify([
        {
            "id": r.id,
            "record_type": r.record_type.value,
            "details": r.details,  # Return string directly
            "created_at": r.created_at.strftime("%Y-%m-%d"),
        } for r in records
    ])

@medical_bp.route("/medical/<int:record_id>", methods=["PUT"])
@token_required
def update_medical_record(record_id):
    record = MedicalRecord.query.get(record_id)

    if not record:
        return jsonify({"message": "Record not found"}), 404

    horse = Horse.query.filter_by(id=record.horse_id, owner_id=g.user_id).first()
    if not horse:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    details = data.get("details")
    if not details:
        return jsonify({"message": "Details field is required"}), 400

    record.details = details  # Store as string
    db.session.commit()

    return jsonify({"message": "Record updated successfully"}), 200

@medical_bp.route("/medical/<int:record_id>", methods=["DELETE"])
@token_required
def delete_medical_record(record_id):
    record = MedicalRecord.query.get(record_id)

    if not record:
        return jsonify({"message": "Record not found"}), 404

    horse = Horse.query.filter_by(id=record.horse_id, owner_id=g.user_id).first()
    if not horse:
        return jsonify({"message": "Unauthorized"}), 403

    db.session.delete(record)
    db.session.commit()

    return jsonify({"message": "Record deleted successfully"}), 200