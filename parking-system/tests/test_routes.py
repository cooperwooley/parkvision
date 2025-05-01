import requests
import time

def test_initialize_lot_route():
    # Wait for Flask app to start
    time.sleep(5)
    url = "http://localhost:5000/initialize_lot"
    response = requests.get(url)
    assert response.status_code == 200
    assert "html" in response.text.lower()

def test_initialize_lot_post_missing_video():
    url = "http://localhost:5000/initialize_lot"
    payload = {
        "name": "Test Lot"
        # missing video_path
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 400
    assert "video_path not provided" in response.text