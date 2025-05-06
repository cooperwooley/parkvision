import cv2 as cv
import time
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.spot_status import SpotStatus
from models.parking_analytics import ParkingAnalytics
from extensions import db

"""
    Initialize database records for a new parking lot and its spots.

    Args:
        lot_info (list): List of detected parking spots
        name (str): Name of the parking lot
        frame_path (str): Path to the saved reference image
        video_path (str): Path to the lot's surveillance video
        description (str, optional): Description of the lot
        address (str, optional): Physical address of the lot

    Returns:
        None
"""
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
        video_start_time=time.time()
    )
    db.session.add(new_lot)
    db.session.commit()
    print(f"Lot {name} added")

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
        print(f"Spot {str(spot['id'])} for Lot {name}")
    db.session.commit()
    
    # Create ParkingAnalytics entry
    analytics_entry = ParkingAnalytics(
        parking_lot_id=new_lot.id,
        total_spaces=len(lot_info),
        occupied_spaces=0
    )
    db.session.add(analytics_entry)
    print(f"Lot analytics for Lot {name} added")

    db.session.commit()
    print(f"Lot {name}, spots, and analytics commited")


"""
    Update the status of parking spots in the database.

    Args:
        lot_id (int): ID of the parking lot
        updated_info (list): List of spot status dictionaries

    Returns:
        None
"""
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

    # Update analytics
    analytics_entry = ParkingAnalytics.query.filter_by(parking_lot_id=lot_id).first()

    if analytics_entry:
        occupied_count = sum(1 for spot in updated_info if spot['status'] == 'occupied')
        analytics_entry.occupied_spaces = occupied_count
        db.session.commit()
        print(f"Updated analytics for Lot {lot_id}: Occupied spaces = {occupied_count}")
    else:
        total_spaces = len(updated_info)
        analytics_entry = ParkingAnalytics(
            parking_lot_id=lot_id,
            total_spaces=total_spaces,
            occupied_spaces=0
        )
        db.session.add(analytics_entry)
        db.session.commit()
        print(f"Created new analytics entry for Lot {lot_id} with {total_spaces} total spaces.")

    db.session.commit()


"""
    Get the ID for a new parking lot by incrementing the latest one.

    Returns:
        int: Next available parking lot ID
"""
def get_latest_lot_id():
    latest_lot_id = ParkingLot.query.order_by(ParkingLot.id.desc()).first()

    if latest_lot_id:
        return latest_lot_id.id + 1
    return 1


"""
    Get the current frame from video for specified lot.

    Returns:
        int: "Current Frame"
"""
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