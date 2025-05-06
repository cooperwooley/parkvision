from flask import Blueprint, request, jsonify
from utils.camera_processor import detect_parking_spaces_auto, detect_cars_background_subtraction
from utils.database_manager import init_lot_db, update_lot_info_db, get_current_frame_for_lot, get_latest_lot_id
from utils.data_processor import normalize
from flask_cors import cross_origin

parking_bp = Blueprint('parking', __name__)

"""
    Handle parking lot initialization via POST request.

    Expects:
        JSON body with 'video_path' and 'name' (required),
        'description' and 'address' (optional).

    Returns:
        JSON: Contains 'lot_id' and list of detected parking spots.
"""
@parking_bp.route('/initialize_lot', methods=['POST'])
def initialize_lot():
    data = request.get_json()
    video_path = data.get('video_path')
    name = data.get('name')
    description = data.get('description')
    address = data.get('address')

    if not video_path:
        return jsonify({"error": "video_path not provided"}), 400
    if not name:
        return jsonify({"error": "Lot name not provided"}), 400

    lot_info, frame_path = detect_parking_spaces_auto(video_path)

    if not lot_info:
        return jsonify({"error": "No parking spots detected"}), 500
    
    lot_info = normalize(lot_info)

    init_lot_db(lot_info, name, frame_path, video_path, description, address)
    lot_id = get_latest_lot_id() - 1

    response = {"lot_id": lot_id,
                "spots": lot_info}

    return jsonify(response)


"""
    Route for fetching lot status by ID.

    Args:
        lot_id (int): ID of the parking lot to get status for

    Returns:
        JSON data of parking lot info after running through car detection
"""
@parking_bp.route('/lot_status/<int:lot_id>', methods=['GET'])
@cross_origin(origins='http://localhost:5173', supports_credentials=True)
def lot_status(lot_id):
    current_frame = get_current_frame_for_lot(lot_id)
    if current_frame is None:
        return jsonify({"error": "no current frame"}), 400

    # Run car detection
    updated_info = detect_cars_background_subtraction(current_frame, lot_id)

    # Update database
    update_lot_info_db(lot_id, updated_info)

    return jsonify(updated_info)


# Shows the info for specific lot id
# @parking_bp.route('/lot_info/<int:lot_id>', methods=['GET'])
# def get_lot_info(lot_id):
#     lot = ParkingLot.query.get(lot_id)

#     if lot is None:
#         return jsonify({"error": "Lot not found"}), 404

#     lot_info = {
#         "id": lot.id,
#         "name": lot.name,
#         "address": lot.address,
#         "total_spaces": lot.total_spaces,
#         "description": lot.description,
#         "init_frame_path": lot.init_frame_path,
#         "video_path": lot.video_path,
#         "created_at": lot.created_at,
#         "updated_at": lot.updated_at
#     }

#     return jsonify(lot_info)

