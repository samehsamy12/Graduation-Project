from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.horse import Horse
from app.models.horse_image import HorseImage
from app.utils.jwt_utils import token_required
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

horse_bp = Blueprint("horses", __name__)

def validate_date_format(date_str):
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False

@horse_bp.route("/add-horse", methods=["POST"])
@token_required
def add_horse():
    owner_id = g.user_id

    name = request.form.get("name")
    gender = request.form.get("gender")
    date_of_birth = request.form.get("date_of_birth")
    sire = request.form.get("sire")
    dam = request.form.get("dam")
    coat = request.form.get("coat")
    blood_type = request.form.get("blood_type")
    national_id = request.form.get("national_id")
    image = request.files.get("image")

    if not name or not gender or not date_of_birth:
        return jsonify({"message": "Missing required fields: name, gender, date_of_birth"}), 400

    if not validate_date_format(date_of_birth):
        return jsonify({"message": "Date of birth must be in dd-mm-yyyy format"}), 400

    image_url = None
    if image:
        filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
        image_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'horses')
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, filename)
        image.save(image_path)
        image_url = f"/static/uploads/horses/{filename}"

    try:
        horse_id = str(uuid.uuid4())

        new_horse = Horse(
            name=name,
            gender=gender,
            date_of_birth=date_of_birth,
            sire=sire,
            dam=dam,
            coat=coat,
            blood_type=blood_type,
            national_id=national_id,
            horse_id=horse_id,
            owner_id=owner_id,
            image_url=image_url
        )

        db.session.add(new_horse)
        db.session.commit()

        return jsonify({
            "message": "Horse added successfully",
            "horse": new_horse.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

@horse_bp.route("/delete-horse/<horse_id>", methods=["DELETE"])
@token_required
def delete_horse(horse_id):
    owner_id = g.user_id
    horse = Horse.query.filter_by(horse_id=horse_id, owner_id=owner_id).first()
    if not horse:
        return jsonify({"message": "Horse not found or unauthorized"}), 404

    try:
        db.session.delete(horse)
        db.session.commit()
        return jsonify({"message": "Horse deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting horse: {str(e)}"}), 500

@horse_bp.route("/edit-horse/<horse_id>", methods=['PUT'])
@token_required
def edit_horse(horse_id):
    user_id = g.user_id
    horse = Horse.query.filter_by(horse_id=horse_id, owner_id=user_id).first()
    if not horse:
        return jsonify({"message": "Horse not found or unauthorized"}), 404

    name = request.form.get("name")
    gender = request.form.get("gender")
    date_of_birth = request.form.get("date_of_birth")
    sire = request.form.get("sire")
    dam = request.form.get("dam")
    coat = request.form.get("coat")
    blood_type = request.form.get("blood_type")
    national_id = request.form.get("national_id")
    image = request.files.get("image")

    try:
        if name:
            horse.name = name
        if gender:
            horse.gender = gender
        if date_of_birth:
            if not validate_date_format(date_of_birth):
                return jsonify({"message": "Date of birth must be in dd-mm-yyyy format"}), 400
            horse.date_of_birth = date_of_birth
        if sire is not None:
            horse.sire = sire
        if dam is not None:
            horse.dam = dam
        if coat is not None:
            horse.coat = coat
        if blood_type is not None:
            horse.blood_type = blood_type
        if national_id is not None:
            horse.national_id = national_id
        if image:
            filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
            image_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'horses')
            os.makedirs(image_dir, exist_ok=True)
            image_path = os.path.join(image_dir, filename)
            image.save(image_path)
            horse.image_url = f"/static/uploads/horses/{filename}"

        db.session.commit()
        return jsonify({
            "message": "Horse updated successfully",
            "horse": horse.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating horse: {str(e)}"}), 500

@horse_bp.route("/upload-horse-image/<int:horse_id>", methods=["POST"])
@token_required
def upload_horse_image(horse_id):
    user_id = g.user_id
    horse = Horse.query.get(horse_id)
    if not horse:
        return jsonify({"message": "Horse not found"}), 404
    if horse.owner_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    if 'image' not in request.files:
        return jsonify({"message": "No image uploaded"}), 400

    image = request.files['image']
    filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'horses')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    image.save(filepath)

    image_url = f"/static/uploads/horses/{filename}"
    horse.image_url = image_url
    db.session.commit()

    return jsonify({"message": "Image uploaded", "url": image_url}), 201

@horse_bp.route("/get-horse-images/<int:horse_id>", methods=["GET"])
@token_required
def get_horse_images(horse_id):
    user_id = g.user_id
    horse = Horse.query.get(horse_id)
    if not horse:
        return jsonify({"message": "Horse not found"}), 404
    if horse.owner_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    images = HorseImage.query.filter_by(horse_id=horse_id).all()
    image_urls = [image.image_url for image in images]
    if horse.image_url:
        image_urls.append(horse.image_url)

    return jsonify({"images": image_urls}), 200

@horse_bp.route("/get-horses", methods=["GET"])
@token_required
def get_horses():
    owner_id = g.user_id
    try:
        horses = Horse.query.filter_by(owner_id=owner_id).all()
        horse_list = [horse.to_dict() for horse in horses]
        return jsonify({"horses": horse_list}), 200
    except Exception as e:
        return jsonify({"message": f"Error retrieving horses: {str(e)}"}), 500