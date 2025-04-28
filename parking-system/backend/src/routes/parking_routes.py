from flask import Blueprint, request, jsonify
from utils.camera_processor import detect_parking_spaces_auto, get_current_frame_for_lot, detect_cars_background_subtraction
from utils.database_manager import init_lot_db, update_lot_info_db

parking_bp = Blueprint('parking', __name__)

@parking_bp.route('/initialize_lot', methods=['POST'])
def initialize_lot_route():
    data = request.get_json() # expect JSON like {"video_path": "...", "name": "...", "description": "...", "address": "..."}
    video_path = data.get('video_path')
    name = data.get('name')
    description = data.get('description')
    address = data.get('address')

    if not video_path:
        return jsonify({"error": "video_path not provided"}), 400
    if not name:
        return jsonify({"error": "Lot name not provided"}), 400
    
    lot_info, frame_path = detect_parking_spaces_auto(video_path)
    init_lot_db(lot_info, name, frame_path, video_path, description, address)
    return jsonify(lot_info)

@parking_bp.route('/lot_status/<int:lot_id>', methods=['GET'])
def lot_status(lot_id):
    # Capture current frame
    current_frame = get_current_frame_for_lot(lot_id)
    # Run car detection
    updated_info = detect_cars_background_subtraction(current_frame, lot_id)
    # Run car detection
    update_lot_info_db(lot_id, updated_info)

    return jsonify(updated_info)