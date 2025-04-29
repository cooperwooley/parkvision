from extensions import db
from models.parking_spot import ParkingSpot
from datetime import datetime, timezone

class SpotStatus(db.Model):
    __tablename__ = 'spot_status'

    id = db.Column(db.Integer, primary_key=True)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey(ParkingSpot.id))
    status = db.Column(db.String(20), nullable=False)
    detected_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    detection_method = db.Column(db.String(50))