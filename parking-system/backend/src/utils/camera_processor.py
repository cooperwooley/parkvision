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

        if 500 < area < 6000: 
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

        if 500 < area < 5000:
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

        # Convert to grayscale
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Calculate absolute difference
        frame_delta = cv.absdiff(background, gray)

        # Threshold the delta image
        thresh = cv.threshold(frame_delta, 25, 255, cv.THRESH_BINARY)[1]

        # Dilate the thresholded image to fill in holes
        thresh = cv.dilate(thresh, None, iterations=2)

        spots_status = []

        parking_spots = get_parking_spots(lot_id)

        for spot in parking_spots:
            if 'points' in spot:
                # Handle skewed spots
                pts = np.array(spot['points'], dtype=np.float32)
                dst_size = (int(max(np.linalg.norm(pts[0] - pts[1]), np.linalg.norm(pts[2] - pts[3]))),
                            int(max(np.linalg.norm(pts[0] - pts[3]), np.linalg.norm(pts[1] - pts[2]))))
                rect_pts = np.array([[0, 0], [dst_size[0]-1, 0], [dst_size[0]-1, dst_size[1]-1], [0, dst_size[1]-1]], dtype=np.float32)

                matrix = cv.getPerspectiveTransform(pts, rect_pts)
                warped = cv.warpPerspective(thresh, matrix, dst_size)

                # Calculate percentage of white pixels
                white_pixel_percentage = np.sum(warped == 255) / (dst_size[0] * dst_size[1]) * 100

                if white_pixel_percentage > 50:
                    spot_status = 'occupied'
                    color = (0, 0, 255)
                else:
                    spot_status = 'empty'
                    color = (0, 255, 0)

                cv.polylines(frame, [pts.astype(np.int32)], isClosed=True, color=color, thickness=2)

            else:
                # Handle rectangular spots
                x, y, w, h = spot['x'], spot['y'], spot['width'], spot['height']
                spot_roi = thresh[y:y+h, x:x+w]

                # Calculate percentage of white pixels
                white_pixel_percentage = np.sum(spot_roi == 255) / (w * h) * 100

                if white_pixel_percentage > 50:
                    spot_status = 'occupied'
                else:
                    spot_status = 'empty'

            spots_status.append({
                'id': spot['id'],
                'status': spot_status
            })

        return spots_status