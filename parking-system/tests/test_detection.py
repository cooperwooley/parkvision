import requests
import json
import time

BASE_URL = "http://localhost:5000"

def initialize_lot():
    url = f"{BASE_URL}/initialize_lot"
    payload = {
        "video_path": "tests/lot_footage.mp4",
        "name": "Test Lot 1",
        "description": "Test lot for detection validation",
        "address": "123 Test St"
    }
    print(f"Sending POST to {url} with payload:")
    print(json.dumps(payload, indent=2))

    response = requests.post(url, json=payload)
    print("Status Code:" , response.status_code)

    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Failed to parse JSON:", e)
        print(response.text)

    return response.json() if response.status_code == 200 else None

def get_lot_status(lot_id):
    url = f"{BASE_URL}/lot_status/{lot_id}"
    print(f"\nRequesting lot status from: {url}")

    response = requests.get(url)
    print("Status Code:", response.status_code)

    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Failed to parse JSON:", e)
        print(response.text)


def main():
    print("Waiting for backend to be ready...")
    time.sleep(5)

    result = initialize_lot()
    if result and 'lot_id' in result:
        get_lot_status(result['lot_id'])
    else:
        get_lot_status(1)

if __name__ == "__main__":
    main()