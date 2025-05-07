import cv2 as cv
import numpy as np
import os
from utils.database_manager import get_latest_lot_id, get_background_frame, get_parking_spots

"""
    Capture a single reference frame from a video file and save it as an image.

    Args:
        video_path (str): Path to the video file
        frame_number (int): Frame number to capture (default is 0)

    Returns:
        tuple: (captured frame as ndarray, path to saved image)
"""
def capture_reference_image(video_path, frame_number=0):
    cap  = cv.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video file")
        return None

    ret, frame = cap.read()

    if ret:
        frame = remove_black_bars(frame)

        static_folder = os.path.join(os.getcwd(), 'static')
        if not os.path.exists(static_folder):
            os.makedirs(static_folder)

        image_counter = get_latest_lot_id()
        frame_path = f'static/{image_counter}.jpg'

        cv.imwrite(frame_path, frame)
        print(f"Reference image saved from frame {frame_number}")
    else:
        print("Error: Could not read frame")
        frame = None

    cap.release()

    return frame, frame_path


"""
    Remove black bars from a frame/image to fix contour detection in parking space detection
    
    Args:
        frame (np.ndarray): Frame/image removing black bars from

    Returns:
        np.ndarray: Cropped frame/image
"""
def remove_black_bars(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Threshold to create binary mask
    _, thresh = cv.threshold(gray, 1, 255, cv.THRESH_BINARY)

    # Find contours
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Get the largest contour (content area)
    largest_contour = max(contours)

    # Get bounding box
    x, y, w, h = cv.boundingRect(largest_contour)

    # Crop image
    cropped_frame = frame[y:y+h, x:x+w]

    return cropped_frame


"""
    Automatically detect parking spaces using edge detection on a video reference frame.

    Args:
        video_path (str): Path to the input video
        sensitivity (int): Canny edge sensitivity (default: 75)

    Returns:
        tuple: (list of detected parking spot dictionaries, path to saved reference frame)
"""
def detect_parking_spaces_auto(video_path, sensitivity=75):
    img, img_path = capture_reference_image(video_path)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Apply edge detection
    edges1 = cv.Canny(gray, sensitivity, sensitivity * 3)

    # Find contours to draw box
    contours, _ = cv.findContours(edges1, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contour_rectangle = img.copy()

    # Draw bounding box
    for contour in contours:
        area = cv.contourArea(contour)

        if 5000 < area < 20000: 
            x, y, w, h = cv.boundingRect(contour)

            cv.rectangle(contour_rectangle, (x, y), (x + w, y + h), (255, 255, 255), 3)

    # Redo previous operations
    gray = cv.cvtColor(contour_rectangle, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, sensitivity, sensitivity * 3)
    contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    spots = []
    spot_id = 1

    def is_near_existing(x, y, w, h, existing_boxes, threshold=10):
        for ex, ey, ew, eh in existing_boxes:
            if abs(x - ex) < threshold and abs(y - ey) < threshold and abs(w - ew) < threshold and abs(h - eh) < threshold:
                return True
        return False

    existing_boxes = []
    for contour in contours:
        area = cv.contourArea(contour)

        if 500 < area < 16000:
            x, y, w, h = cv.boundingRect(contour)
            if not is_near_existing(x, y, w, h, existing_boxes):
                existing_boxes.append((x, y, w, h))
                spots.append({
                    'id': spot_id,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'status': 'empty'
                })
                spot_id += 1

    return spots, img_path


"""
    Detect cars in a parking lot using background subtraction technique.

    Args:
        frame (np.ndarray): The current frame from the parking lot camera
        lot_id (int): ID of the parking lot being monitored

    Returns:
        list: List of dictionaries with spot IDs and their occupancy status
"""
def detect_cars_background_subtraction(frame, lot_id):
        background = get_background_frame(lot_id)

        if background is None or frame is None:
            raise ValueError("Background or current frame is None")
        
        frame = remove_black_bars(frame)

        # Convert to grayscale
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        
        if background.shape != gray.shape:
            min_width = min(background.shape[1], gray.shape[1])
            min_height = min(background.shape[0], gray.shape[0])

            background = background[:min_height, :min_width]
            gray = gray[:min_height, :min_width]

        # Calculate absolute difference
        frame_delta = cv.absdiff(background, gray)

        # Threshold the delta image
        thresh = cv.threshold(frame_delta, 25, 255, cv.THRESH_BINARY)[1]

        # Dilate the thresholded image to fill in holes
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        thresh = cv.dilate(thresh, kernel, iterations=2)

        spots_status = []

        parking_spots = get_parking_spots(lot_id)

        for spot in parking_spots:
            # Handle rectangular spots
            x, y, w, h = spot['x'], spot['y'], spot['width'], spot['height']
            spot_roi = thresh[y:y+h, x:x+w]

            # Calculate percentage of white pixels
            white_pixel_percentage = np.sum(spot_roi == 255) / (w * h) * 100

            if white_pixel_percentage > 50:
                spot_status = 'occupied'
                color = (0, 0, 255)
            else:
                spot_status = 'empty'
                color = (0, 255, 0)

            cv.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            spots_status.append({
                'id': spot['id'],
                'status': spot_status,
                'x': spot['x'],
                'y': spot['y'],
                'width': spot['width'],
                'height': spot['height']
            })


            label_pos = (spot['x'], spot['y'] - 5)
            cv.putText(frame, f"ID: {spot['id']} - {spot_status}", label_pos, cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # For testing 
        # static_folder = os.path.join(os.getcwd(), 'static')
        # if not os.path.exists(static_folder):
        #     os.makedirs(static_folder)

        # image_counter = get_latest_lot_id() - 1
        # frame_path = f'static/{image_counter}-car-detected.jpg'
        # thresh_path = f'static/{image_counter}-car-thresh.jpg'

        # cv.imwrite(frame_path, frame)
        # cv.imwrite(thresh_path, thresh)

        return spots_status