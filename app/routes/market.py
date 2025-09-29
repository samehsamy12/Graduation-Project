from flask import Blueprint, g, request, jsonify, current_app
from app.extensions import db
from app.utils.jwt_utils import token_required
from app.models.horse import Horse
from app.models.horse_listing import HorseListing
import os
from werkzeug.utils import secure_filename

market_bp = Blueprint("market", __name__)

# Configure upload folder (use cloud storage like S3 in production)
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@market_bp.route("/market/upload_image", methods=["POST"])
@token_required
def upload_image():
    # Ensure the uploads directory exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    if 'image' not in request.files:
        return jsonify({"message": "No image provided"}), 400
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({"image_url": f"/static/uploads/{filename}"}), 200
    return jsonify({"message": "Invalid file type"}), 400

@market_bp.route("/market/add", methods=["POST"])
@token_required
def add_listing():
    data = request.json
    horse_id = data.get("horse_id")
    price = data.get("price")
    description = data.get("description", "")  # Includes contact info
    image_url = data.get("image_url", "")

    horse = Horse.query.filter_by(id=horse_id, owner_id=g.user_id).first()
    if not horse:
        return jsonify({"message": "Horse not found or not owned by you"}), 404

    listing = HorseListing(
        horse_id=horse.id,
        seller_id=g.user_id,
        price=price,
        description=description,
        image_url=image_url,
        is_active=True
    )

    db.session.add(listing)
    db.session.commit()

    return jsonify({"message": "Horse listed successfully", "listing_id": listing.id}), 201

@market_bp.route("/market/<int:listing_id>/edit", methods=["PUT"])
@token_required
def edit_listing(listing_id):
    data = request.json
    listing = HorseListing.query.join(Horse).filter(
        HorseListing.id == listing_id,
        Horse.owner_id == g.user_id
    ).first()

    if not listing:
        return jsonify({"message": "Listing not found or not authorized"}), 404

    listing.price = data.get("price", listing.price)
    listing.description = data.get("description", listing.description)
    listing.image_url = data.get("image_url", listing.image_url)
    listing.is_active = data.get("is_active", listing.is_active)

    db.session.commit()
    return jsonify({"message": "Listing updated successfully"}), 200

@market_bp.route("/market/<int:listing_id>/delete", methods=["DELETE"])
@token_required
def delete_listing(listing_id):
    listing = HorseListing.query.join(Horse).filter(
        HorseListing.id == listing_id,
        Horse.owner_id == g.user_id
    ).first()

    if not listing:
        return jsonify({"message": "Listing not found or not authorized"}), 404

    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "Listing deleted successfully"}), 200

@market_bp.route("/market", methods=["GET"])
def list_all():
    listings = HorseListing.query.filter_by(is_active=True).all()
    result = []
    for l in listings:
        result.append({
            "id": l.id,
            "horse_id": l.horse_id,
            "horse_name": l.horse.name,  # Assuming Horse model has a 'name' field
            "price": l.price,
            "description": l.description,
            "image_url": l.image_url,
            "seller_username": l.seller.username,  # Assuming User model has a 'username' field
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    return jsonify(result), 200

@market_bp.route("/market/<int:listing_id>", methods=["GET"])
def view_listing(listing_id):
    listing = HorseListing.query.get(listing_id)
    if not listing or not listing.is_active:
        return jsonify({"message": "Listing not found"}), 404

    return jsonify({
        "id": listing.id,
        "horse_id": listing.horse_id,
        "horse_name": listing.horse.name,
        "price": listing.price,
        "description": listing.description,
        "image_url": listing.image_url,
        "seller_username": listing.seller.username,
        "created_at": listing.created_at.strftime("%Y-%m-%d %H:%M"),
    }), 200

@market_bp.route("/market/my_listings", methods=["GET"])
@token_required
def my_listings():
    listings = HorseListing.query.filter_by(seller_id=g.user_id, is_active=True).all()
    result = []
    for l in listings:
        result.append({
            "id": l.id,
            "horse_id": l.horse_id,
            "horse_name": l.horse.name,
            "price": l.price,
            "description": l.description,
            "image_url": l.image_url,
            "seller_username": l.seller.username,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    return jsonify(result), 200