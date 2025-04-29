from extensions import db
from datetime import datetime, timezone

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    total_spaces = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    init_frame_path = db.Column(db.Text)
    video_path = db.Column(db.Text)
    video_start_time = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
