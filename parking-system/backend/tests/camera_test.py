import cv2 as cv
import numpy as np
import os
from datetime import datetime
import json

empty_lot_path = 'lot/empty_lot.png'
used_lot_path = 'lot/used_lot.png'
json_path = 'parking_spots.json'

cascade_path = os.path.join(os.path.dirname(__file__), 'haarcascade_car.xml')
parking_spots = []
is_skewed = False

def toggle_mode():
    global is_skewed
    is_skewed = not is_skewed
    mode = "Skewed" if is_skewed else "Rectangular"
    print(f"Switching to {mode} mode")
    return mode


# Extracts a reference frame from a video file
def capture_reference_image(video_path, frame_number=0):
    cap  = cv.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video file")
        return None
    
    # total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    # if frame_number >= total_frames:
    #     print(f"Error: Requested frame {frame_number} exceeds total frames ({total_frames})")
    #     return None
    
    # cap.set(cv.CAP_PROP_POS_FRAMES, frame_number)

    ret, frame = cap.read()

    if ret:
        cv.imwrite('empty_parking_lot.jpg', frame)
        print(f"Reference image saved from frame {frame_number}")
    else:
        print("Error: Could not read frame")
        frame = None

    cap.release()
    
    return frame

def click_event(event, x, y, flags, param):
    global parking_spots
    if event == cv.EVENT_LBUTTONDOWN:
        # Add first point of a parking spot
        if len(parking_spots) % (4 if is_skewed else 2) == 0:
            parking_spots.append((x, y))
            print(f"Point {len(parking_spots)}: ({x}, {y})")
        else:
            # Add subsequent point(s)
            parking_spots.append((x, y))
            print(f"Point {len(parking_spots)}: ({x}, {y})")

            # Draw the defined lot over image
            if is_skewed and len(parking_spots) % 4 == 0:
                pts = np.array(parking_spots[-4:], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            elif not is_skewed and len(parking_spots) % 2 == 0:
                cv.rectangle(img, parking_spots[-2], parking_spots[-1], (0, 255, 0), 2)

            cv.imshow('image', img)


def define_parking_spaces(img):
    global is_skewed

    mode_window = "Select Mode"
    mode = "Skewed" if is_skewed else "Rectangular"
    black_screen = np.zeros_like(img)

    while True:
        display = black_screen.copy()
        cv.putText(display, "Hit T to toggle mode", (30, 200),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv.putText(display, "Press Enter to continue", (30, 250),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv.putText(display, f"Current Mode: {mode}", (30, 300),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv.imshow(mode_window, display)
        key = cv.waitKey(1) & 0xFF

        if key == ord('t'):
            mode = toggle_mode()
        elif key == 13:  # Enter
            break

    cv.destroyWindow(mode_window)

    working_img = img.copy()
    display_img = working_img.copy()
    cv.putText(display_img, f"Mode: {mode}", (10, working_img.shape[0] - 10),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv.imshow('Empty Lot', display_img)
    cv.setMouseCallback('Empty Lot', click_event)

    while True:
        key = cv.waitKey(1) & 0xFF
        if key == 13 or key == 27:  # Enter or Esc to finish
            break

    cv.destroyAllWindows()

    # Format data
    spots = []
    for i in range(0, len(parking_spots), 4 if is_skewed else 2):
        if is_skewed:
            x1, y1 = parking_spots[i]
            x2, y2 = parking_spots[i+1]
            x3, y3 = parking_spots[i+2]
            x4, y4 = parking_spots[i+3]
            spots.append({
                'id': i // 4 + 1,
                'points': [(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
                'status': 'empty'
            })
        else:
            x1, y1 = parking_spots[i]
            x2, y2 = parking_spots[i+1]
            spots.append({
                'id': i // 2 + 1,
                'x': min(x1, x2),
                'y': min(y1, y2),
                'width': abs(x2 - x1),
                'height': abs(y2 - y1),
                'status': 'empty'
            })

    with open(json_path, 'w') as f:
        json.dump(spots, f)


def detect_parking_spaces_auto(img, sensitivity=75):
    original = img.copy()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Apply edge detection
    edges1 = cv.Canny(gray, sensitivity, sensitivity * 3)

    # Find contours to draw box
    contours, _ = cv.findContours(edges1, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contour_rectangle = img.copy()

    # Draw bounding box
    for contour in contours:
        area = cv.contourArea(contour)

        print(area)

        if 500 < area < 6000: 
            x, y, w, h = cv.boundingRect(contour)

            cv.rectangle(contour_rectangle, (x, y), (x + w, y + h), (255, 255, 255), 3)

    print('\n\n')
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
        print(area)

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

                cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv.putText(img, str(spot_id), (x + 5, y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                spot_id += 1

    # Show the images
    cv.imshow('Original', original)
    cv.imshow('Edges', edges1)
    cv.imshow('Contour', contour_rectangle)
    cv.imshow('Detected Parking Spots', img)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # Save to JSON file
    with open('parking_spots.json', 'w') as f:
        json.dump(spots, f)
    
    
class ParkingLotMonitor:
    def __init__(self):
        # Load parking spot data
        with open(json_path, 'r') as f:
            self.parking_spots = json.load(f)

        self.car_cascade = cv.CascadeClassifier(cascade_path)

        self.hog = cv.HOGDescriptor()
        self.hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())

    def detect_cars_basic(self, frame):
        # Convert to grayscale
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # Apply gaussian blur
        blur = cv.GaussianBlur(gray, (21, 21), 0)

        spots_status = []

        # Check each parking spot
        for spot in self.parking_spots:
            # Extract spot region
            x, y, w, h = spot['x'], spot['y'], spot['width'], spot['height']
            spot_roi = blur[y:y+h, x: x+w]

            # Calculate mean pixel value in the region
            spot_mean = np.mean(spot_roi)

            # Simple threshold detection
            if spot_mean < 100: # Adjust this threshold
                spot_status = 'occupied'
            else:
                spot_status = 'empty'
            
            spots_status.append({
                'id': spot['id'],
                'status': spot_status
            })

            # Draw rectangle with color based on status
            color = (0, 255, 0) if spot_status == 'empty' else (0, 0, 255)
            cv.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv.putText(frame, f"ID: {spot['id']} - {spot_status}", (x, y-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame, spots_status
    
    def detect_cars_haar(self, frame):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        spots_status = []

        for spot in self.parking_spots:
            x, y, w, h = spot['x'], spot['y'], spot['width'], spot['height']
            spot_roi = gray[y:y+h, x:x+w]

            # Detect cars in ROI
            cars = self.car_cascade.detectMultiScale(spot_roi, 1.1, 1)

            if len(cars) > 0:
                spot_status = 'occupied'
                color = (0, 0, 255) # Red
            else:
                spot_status = 'empty'
                color = (0, 255, 0) # Green

            spots_status.append({
                'id': spot['id'],
                'status': spot_status
            })

            # Draw rectangle
            cv.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv.putText(frame, f"ID: {spot['id']} - {spot_status}", (x, y-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame, spots_status
    
    def detect_cars_background_subtraction(self, frame, background):
        # Convert to grayscale
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Calculate absolute difference
        frame_delta = cv.absdiff(background, gray)
        cv.imshow('Frame Delta', frame_delta)

        # Threshold the delta image
        thresh = cv.threshold(frame_delta, 25, 255, cv.THRESH_BINARY)[1]
        cv.imshow('Thresh', thresh)

        # Dilate the thresholded image to fill in holes
        thresh = cv.dilate(thresh, None, iterations=2)
        cv.imshow('Dilate', thresh)

        spots_status = []

        for spot in self.parking_spots:
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
                    color = (0, 0, 255)
                else:
                    spot_status = 'empty'
                    color = (0, 255, 0)

                cv.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            spots_status.append({
                'id': spot['id'],
                'status': spot_status
            })
            label_pos = (spot['x'], spot['y'] - 5) if 'x' in spot else tuple(pts[0].astype(int))
            cv.putText(frame, f"ID: {spot['id']} - {spot_status}", label_pos, cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv.waitKey(0)
        return frame, spots_status
    
    def test_monitoring(self, background_path, video_path):
        cap = cv.VideoCapture(background_path)

        # Capture background frame for background subtraction
        _, background_frame = cap.read()
        background_frame = cv.resize(background_frame, (512, 512))
        background = cv.cvtColor(background_frame, cv.COLOR_BGR2GRAY)
        background = cv.GaussianBlur(background, (21, 21), 0)

        # Use when live
        # while True:
        #     ret, frame = cap.read()
        #     if not ret:
        #         break

        #     # Choose one detection method:
        #     # frame_with_status, spots_status = self.detect_cars_basic(frame)
        #     # frame_with_status, spots_status = self.detect_cars_haar(frame)
        #     frame_with_status, spots_status = self.detect_cars_background_subtraction(frame, background)

        #     print(spots_status)

        #     cv.imshow('Parking Lot Monitor', frame_with_status)

        #     if cv.waitKey(1) & 0xFF == ord('q'):
        #         break

        cap = cv.VideoCapture(video_path)

        ret, frame = cap.read()
        frame = cv.resize(frame, (512, 512))
        # frame_with_status, spots_status = self.detect_cars_basic(frame)
        # frame_with_status, spots_status = self.detect_cars_haar(frame)
        frame_with_status, spots_status = self.detect_cars_background_subtraction(frame, background) # This one is optimized to work currently

        print(spots_status)
        cv.imshow('Parking Lot Monitor', frame_with_status)

        cap.release()

        while True:
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        cv.destroyAllWindows()


if __name__ == "__main__":
    img = capture_reference_image(empty_lot_path)
    img = cv.resize(img, (512, 512))

    # Only run first time
    # define_parking_spaces(img)
    detect_parking_spaces_auto(img)

    monitor = ParkingLotMonitor()
    monitor.test_monitoring(empty_lot_path, used_lot_path)