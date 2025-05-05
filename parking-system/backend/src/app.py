from flask import Flask
from flask_cors import CORS
from extensions import db
from models import *
from routes.parking_routes import parking_bp
from routes.auth import auth_bp

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    
    @app.route('/')
    def index():
        return 'Flask server is up and running!'

    with app.app_context():
        # This takes in the json file generated from the camera_test.py file.
        # In the future you could put this in a loop to constantly update the database with correct information.
        db.create_all()
        app.register_blueprint(parking_bp)
        app.register_blueprint(auth_bp)

    # ✅ Enable CORS for React frontend (Vite runs at port 5173 by default)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"])
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)