import cv2 as cv
import numpy as np
import os
from datetime import datetime
import json

empty_lot_path = 'tests/empty_lot.png'
used_lot_path = 'tests/used_lot.png'
json_path = 'tests/parking_spots.json'

cascade_path = os.path.join(os.path.dirname(__file__), 'haarcascade_car.xml')
parking_spots = []

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
        cv.imwrite('emtpy_parking_lot.jpg', frame)
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
        if len(parking_spots) % 2 == 0:
            parking_spots.append((x, y))
            print(f"First point: ({x}, {y})")
        else:
            # Add second point to define a rectangle
            parking_spots.append((x, y))
            print(f"Second point: ({x}, {y})")
            # Draw the rectangle
            cv.rectangle(img, parking_spots[-2], parking_spots[-1], (0, 255, 0), 2)
            cv.imshow('image', img)

def define_parking_spaces(img):
    cv.imshow('Empty Lot', img)
    cv.setMouseCallback('Empty Lot', click_event)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # Format data
    spots = []
    for i in range(0, len(parking_spots), 2):
        if i+1 < len(parking_spots):
            x1, y1 = parking_spots[i]
            x2, y2, = parking_spots[i+1]
            spots.append({
                'id': i//2 + 1,
                'x': min(x1, x2), 
                'y': min(y1, y2),
                'width': abs(x2 - x1),
                'height': abs(y2 - y1),
                'status': 'empty'
            })

    with open(json_path, 'w') as f:
        json.dump(spots, f)

        return spots
    
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
            color = (0, 255, 0) if spot_status == 'emtpy' else (0, 0, 255)
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
            x, y, w, h = spot['x'], spot['y'], spot['width'], spot['height']
            spot_roi = thresh[y:y+h, x:x+w]

            # Calculate percentage of white pixels
            white_pixel_percentage = np.sum(spot_roi == 255) / (w * h) * 100

            if white_pixel_percentage > 50:
                spot_status = 'occupied'
                color = (0, 0, 255) # Red 
            else:
                spot_status = 'empty'
                color = (0, 255, 0)

            spots_status.append({
                'id': spot['id'],
                'status': spot_status
            })

            cv.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv.putText(frame, f"ID: {spot['id']} - {spot_status}", (x, y-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

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

    monitor = ParkingLotMonitor()
    monitor.test_monitoring(empty_lot_path, used_lot_path)