from app.utils.jwt_utils import token_required
from flask import Blueprint, request, jsonify, current_app, g
from app.extensions import db
from app.models.user import User
import bcrypt
import jwt
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    name = data.get("name")
    email = data.get("email")

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt).decode("utf-8")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(username=username, password_hash=password_hash, name=name, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"message": "Invalid username or password"}), 401

    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + current_app.config["JWT_EXPIRATION"]
    }

    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    return jsonify({"message": "Login successful", "token": token}), 200

@auth_bp.route("/edit-profile", methods=["PUT"])
@token_required
def edit_profile():
    user_id = g.user_id
    user = User.query.get(user_id)
    data = request.json

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Optional unique checks
    if "username" in data and data["username"] != user.username:
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"message": "Username already taken"}), 400
        user.username = data["username"]

    if "email" in data and data["email"] != user.email:
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"message": "Email already taken"}), 400
        user.email = data["email"]

    if "name" in data:
        user.name = data["name"]

    if "password" in data:
        salt = bcrypt.gensalt()
        user.password_hash = bcrypt.hashpw(data["password"].encode(), salt).decode("utf-8")

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating profile: {str(e)}"}), 500

