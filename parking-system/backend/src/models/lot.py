from extensions import db

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }