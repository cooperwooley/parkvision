from ..app import db
from datetime import datetime

class ParkingLot(db.Model):
    __table__name = 'parking_lots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    total_spaces = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.Datetime, default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc))
    