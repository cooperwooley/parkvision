from flask import Blueprint, jsonify, request
from ..models.parking_spot import ParkingSpot, db
from ..utils.camera_processor import process_camera_feed

parking_routes = Blueprint('parking_routes', __name__)

@parking_routes.route('/api/spots', methods=['GET'])
def get_parking_spots():
    spots = ParkingSpot.query.all()
    return jsonify([{
        'id': spot.id,
        'lot_name': spot.lot_name,
        'status': spot.status,
        'last_updated': spot.last_updated.isoformat()
    } for spot in spots])

@parking_routes.route('/api/process_feed', methods=['POST'])
def process_parking_feed():
    # Assume the camera feed is updated via a POST request (URL or direct image)
    file = request.files['camera_feed']
    spots = process_camera_feed(file)

    # Process spots and update database
    for spot in spots:
        existing_spot = ParkingSpot.query.get(spot['id'])
        if existing_spot:
            existing_spot.status = spot['status']
            existing_spot.last_updated = spot['last updated']
        else:
            new_spot = ParkingSpot(id=spot['id'], lot_name=spot['lot_name'], status=spot['status'], last_updated=spot['last updated'])
            db.session.add(new_spot)

    db.session.commit()
    return jsonify({'message': 'Parking feed processed successfully'}), 200