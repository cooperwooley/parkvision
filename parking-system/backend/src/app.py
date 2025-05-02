from flask import Flask
from flask_cors import CORS
from extensions import db
from models import *
from routes.parking_routes import parking_bp

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app)

    with app.app_context():
        # This takes in the json file generated from the camera_test.py file.
        # In the future you could put this in a loop to constantly update the database with correct information.
        db.create_all()
        app.register_blueprint(parking_bp, url_prefix='/api')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)