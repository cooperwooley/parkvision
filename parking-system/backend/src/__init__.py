from flask import Flask
from .models import db
from .routes import parking_routes

def create_app():
    app = Flask(__name__)

    # Config
    app.config.from_object('config.Config')

    # Initialize DB
    db.init_app(app)

    # Register routes
    app.register_blueprint(parking_routes)

    return app