from extensions import db
from models.parking_lot import ParkingLot
from datetime import datetime, timezone

class ParkingAnalytics(db.Model):
    __tablename__ = 'parking_analytics'

    id = db.Column(db.Integer, primary_key=True)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey(ParkingLot.id))
    time_stamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    total_spaces = db.Column(db.Integer, nullable=False)
    occupied_spaces = db.Column(db.Integer, nullable=False)
    occupancy_rate = db.Column(db.Float)
    peak_hour = db.Column(db.Boolean, default=False)
