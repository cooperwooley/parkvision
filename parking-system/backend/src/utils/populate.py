import json
import os
from models.lot import ParkingLot
from models.spot import ParkingSpot
from extensions import db

def populate_test_db():
    if ParkingLot.query.first():
        return

    lot = ParkingLot(id=1, name="Test Lot")
    db.session.add(lot)
    db.session.flush()

    # I think in the future, we would move around the paths cause this is janky ngl
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'parking_spots.json'))
    
    with open(json_path) as f:
        spots = json.load(f)
        for s in spots:
            spot = ParkingSpot(
                id=s['id'],
                x=s['x'],
                y=s['y'],
                width=s['width'],
                height=s['height'],
                status=s['status'],
                lot_id=lot.id
            )
            db.session.add(spot)

    db.session.commit()
    print("Test lot and spots populated.")
