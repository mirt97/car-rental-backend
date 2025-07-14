from flask import Flask
from app.models import db
from app.auth import auth_bp
from app.cars import cars_bp
from app.rentals import rentals_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Blueprint kayıtları
    app.register_blueprint(auth_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(rentals_bp)

    return app
