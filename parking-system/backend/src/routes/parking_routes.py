from flask import jsonify, request
from ..app import app
from ..models.parking_lot import ParkingLot
from ..models.parking_spot import ParkingSpot
from ..models.spot_status import SpotStatus

@app.route('/api/parking-lots', methods=['GET'])
def get_parking_lots():
    lots = ParkingLot.query.all()
    return jsonify([{
        'id': lot.id,
        'name': lot.name,
        'total_spaces': lot.total_spaces,
        'address': lot.address
    } for lot in lots])

@app.route('/api/parking_lots/<int:lot_id>/status', methods=['GET'])
def get_lot_status(lot_id):
    # TODO: Query to get current status of all spots in lot
    result = None

    return jsonify({'status': 'success', 'data': result})