# Parking Lot Backend System

This backend service supports parking lot initialization, space detection, and real-time occupancy monitoring. It is built using Flask and OpenCV, and communicates with a database to store and retrieve parking lot data.

---

## Endpoints

### `POST /api/initialize_lot`
Initializes a new parking lot using a video file. Detects and saves parking spot locations.

**Request Body (JSON):**
```json
{
  "video_path": "path/to/video.mp4",
  "name": "Lot A",
  "description": "Near Engineering Hall",
  "address": "123 Main St"
}
```
**Response**
```json
{ 
  "lot_id": 1,
  "spots": [
    {
      "id": 1,
      "x": 100,
      "y": 150,
      "width": 50,
      "height": 80,
      "status": "empty"
    },
  ]
}
```

### `GET /api/lot_status/<int:lot_id>`
Will return the current status of each parking space in a given lot.


### `POST /admin/login`
Logs in an admin user.

**Request Body:**
```json
{
    "username": "admin_user",
    "password": "admin_password"
}
```

**Response**

`200 OK` with token success:
```json
{
  "message": "Admin login successful",
  "token": "<JWT_TOKEN>"
}
```

`401 Unautherized` on invalid credentials:
```json
{
  "message": "Invalid username or password"
}
```

## Frontend Integration Notes
* Use `/api/initialize_lot` to submit lot video and metadata.

* Detected spot geometry will be returned and should be visualized on the frontend canvas.

* Use saved reference frame (`img_path` in response) for mapping visuals.

* When `/api/lot_status` is active, poll for occupancy updates.



