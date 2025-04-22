import cv2 as cv
import numpy as np
from datetime import datetime

def process_camera_feed(file):
    # Feed is assumed to be image file
    # Convert image to format OpenCV can process
    nparr = np.fromstring(file.read(), np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)

    # Apply cv logic to detectr parking spots and their status
    # Placeholder
    parking_spots = detect_parking_spots(img)

    return parking_spots

def detect_parking_spots(img):
    # Placeholder, should return list of spots
    spots = []
    # Example: Return dummy data
    spots.append({
        'id': 1,
        'status': 'Occupied',
        'last_updated': datetime.now(datetime.timezone.utc),
        'lot_name': 'Lot A'
    })
    spots.append({
        'id': 2,
        'status': 'Available',
        'last_updated': datetime.now(datetime.timezone.utc)
    })
    return spots