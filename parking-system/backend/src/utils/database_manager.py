import cv2 as cv
import time
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.spot_status import SpotStatus
from extensions import db

def init_lot_db(lot_info, name, frame_path, video_path, description="", address=""):
    description = description or "" # For None case
    address = address or "" # For None case

    # Create ParkingLot entry
    new_lot = ParkingLot(
        name=name,
        description=description,
        total_spaces=len(lot_info),
        address=address,
        init_frame_path=frame_path,
        video_path=video_path,
        video_start_time=0.0
    )
    db.session.add(new_lot)
    db.session.commit()

    # Create ParkingSpots
    for spot in lot_info:
        new_spot = ParkingSpot(
            parking_lot_id=new_lot.id,
            spot_number=str(spot['id']),
            x=spot['x'],
            y=spot['y'],
            width=spot['width'],
            height=spot['height']
        )
        db.session.add(new_spot)

    db.session.commit()

def update_lot_info_db(lot_id, updated_info):
    # Update SpotStatus for each spot
    for spot_update in updated_info:
        spot_number = spot_update['id']
        status = spot_update['status']

        # Find parking spot by lot_id and spot_number
        parking_spot = ParkingSpot.query.filter_by(parking_lot_id=lot_id, spot_number=str(spot_number)).first()
        if parking_spot:
            new_status = SpotStatus(
                parking_spot_id=parking_spot.id,
                status=status,
                detection_method="background_subtraction"
            )
            db.session.add(new_status)

    db.session.commit()

def get_latest_lot_id():
    latest_lot_id = ParkingLot.query.order_by(ParkingLot.id.desc()).first()

    if latest_lot_id:
        return latest_lot_id + 1
    return 1

def get_current_frame_for_lot(lot_id):
    # TODO: Get frame of video at current time for the request being sent
    # Might have to add video_path to ParkingLot as well

    # Testing currently (Real time video)
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        raise ValueError(f"Lot with id {lot_id} does not exist.")
    
    cap = cv.VideoCapture(lot.video_path)
    fps = cap.get(cv.CAP_PROP_FPS)

    if not lot.video_start_time:
        lot.video_start_time = time.time()
        db.session.commit()

    elapsed_time = time.time() - lot.video_start_time
    target_frame = int(elapsed_time * fps)

    cap.set(cv.CAP_PROP_POS_FRAMES, target_frame)
    ret, frame = cap.read()

    cap.release()

    if not ret:
        return None
    
    return frame

def get_background_frame(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        raise ValueError(f"Lot with id {lot_id} does not exist.")
    
    frame = cv.imread(lot.init_frame_path)
    if frame is None:
        raise ValueError(f"Failed to load frame from {lot.init_frame_path}.")
    
    # Convert to grayscale
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    return gray

def get_parking_spots(lot_id):
    spots = ParkingSpot.query.filter_by(parking_lot_id=lot_id).all()

    spots_data = []
    for spot in spots:
        spots_data.append({
            'id': int(spot.spot_number),
            'x': spot.x,
            'y': spot.y,
            'width': spot.width,
            'height': spot.height
        })

    return spots_data