from extensions import db
from models.parking_lot import ParkingLot
from datetime import datetime, timezone

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey(ParkingLot.id))
    spot_number = db.Column(db.String(20), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))