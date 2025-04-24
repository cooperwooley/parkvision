from flask import Blueprint, render_template, jsonify
from models.spot import ParkingSpot
from models.lot import ParkingLot
from extensions import db

parking_bp = Blueprint('parking', __name__)

@parking_bp.route('/')
def index():
    spots = ParkingSpot.query.all()
    return render_template('index.html', spots=spots)

@parking_bp.route("/debug/lot", methods=["GET"])
def show_lot_data():
    lots = ParkingLot.query.all()
    spots = ParkingSpot.query.all()

    return jsonify({
        "lots": [lot.to_dict() for lot in lots],
        "spots": [spot.to_dict() for spot in spots]
    })
