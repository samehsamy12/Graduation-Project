from app.extensions import db

class PasswordResetCode(db.Model):
    __tablename__ = "password_reset_codes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reset_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    expired_at = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('reset_codes', lazy=True))
