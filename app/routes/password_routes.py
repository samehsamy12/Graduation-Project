from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.models.reset_code import PasswordResetCode
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
import bcrypt

password_bp = Blueprint("password", __name__)

def send_reset_email(email, reset_code):
    from_email = "equicarecommunity@gmail.com"
    app_password = "waoxyzjscoveexpf"

    msg = MIMEText(f"Your password reset code is: {reset_code}")
    msg['Subject'] = "Password Reset Code"
    msg['From'] = from_email
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, app_password)
        server.send_message(msg)

@password_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    username = data.get("username")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    reset_code = ''.join(random.choices('0123456789', k=6))
    expired_at = datetime.now() + timedelta(minutes=30)

    reset_entry = PasswordResetCode(user_id=user.id, reset_code=reset_code, expired_at=expired_at)
    db.session.add(reset_entry)
    db.session.commit()

    send_reset_email(user.email, reset_code)
    return jsonify({"message": "Password reset code sent to your email!"}), 200

# @password_bp.route("/reset-password", methods=["POST"])
# def reset_password():
#     data = request.json
#     username = data.get("username")
#     reset_code = data.get("reset_code")
#     new_password = data.get("new_password")

#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"message": "User not found"}), 404

#     reset_entry = PasswordResetCode.query.filter_by(user_id=user.id, reset_code=reset_code).first()
#     if not reset_entry or datetime.now() > reset_entry.expired_at:
#         return jsonify({"message": "Invalid or expired reset code"}), 400

#     salt = bcrypt.gensalt()
#     new_password_hash = bcrypt.hashpw(new_password.encode(), salt).decode("utf-8")
#     user.password_hash = new_password_hash

#     db.session.delete(reset_entry)
#     db.session.commit()

#     return jsonify({"message": "Password reset successfully!"}), 200

@password_bp.route("/verify-reset-code", methods=["POST"])
def verify_reset_code():
    data = request.json
    username = data.get("username")
    reset_code = data.get("reset_code")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    reset_entry = PasswordResetCode.query.filter_by(user_id=user.id, reset_code=reset_code).first()
    if not reset_entry or datetime.now() > reset_entry.expired_at:
        return jsonify({"message": "Invalid or expired reset code"}), 400


    db.session.commit()

    return jsonify({"message": "Code verified successfully!"}), 200



@password_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    username = data.get("username")
    new_password = data.get("new_password")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # ✅ Check if the code was verified
    reset_entry = PasswordResetCode.query.filter_by(user_id=user.id).order_by(PasswordResetCode.created_at.desc()).first()
    if not reset_entry or datetime.now() > reset_entry.expired_at:
        return jsonify({"message": "No valid reset code found"}), 403


    # ✅ Proceed to reset password
    salt = bcrypt.gensalt()
    new_password_hash = bcrypt.hashpw(new_password.encode(), salt).decode("utf-8")
    user.password_hash = new_password_hash

    db.session.commit()

    return jsonify({"message": "Password reset successfully!"}), 200
