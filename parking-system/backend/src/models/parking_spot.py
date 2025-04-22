from flask_sqlalchemy import SQLALchemy

db = SQLALchemy()

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    lot_name = db.Column(db.String(100))
    status = db.Column(db.String(10)) # Available, Occupied, Reserved
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return f"<ParkingSpot {self.id} - {self.status}>"