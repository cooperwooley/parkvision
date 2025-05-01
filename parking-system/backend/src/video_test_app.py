from flask import Flask
from extensions import db
from models import *
from routes.parking_routes import parking_bp

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        app.register_blueprint(parking_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)