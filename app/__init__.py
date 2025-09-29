from flask import Flask
from .config import Config
from .extensions import db, migrate, session
from .routes.auth_routes import auth_bp
from .routes.horse_routes import horse_bp
from .routes.password_routes import password_bp
from .routes.market import market_bp
from .routes.medical import medical_bp
from .routes.daily_data import daily_bp
from .routes.activity import activity_bp
from .routes.community import community_bp
from .routes.achievement_routes import achievement_bp
from .routes.family_tree_routes import family_tree_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)
    session.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(horse_bp, url_prefix="/api")
    app.register_blueprint(password_bp, url_prefix="/api")
    app.register_blueprint(market_bp, url_prefix="/api")
    app.register_blueprint(medical_bp, url_prefix="/api")
    app.register_blueprint(daily_bp, url_prefix="/api")
    app.register_blueprint(activity_bp, url_prefix="/api")
    app.register_blueprint(community_bp, url_prefix="/api")
    app.register_blueprint(achievement_bp, url_prefix="/api")
    app.register_blueprint(family_tree_bp, url_prefix="/api")
    return app