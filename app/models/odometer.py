from app import db
from datetime import date


class OdometerLog(db.Model):
    __tablename__ = "odometer_logs"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    km = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Date, default=date.today)
    criado_em = db.Column(db.DateTime)

    vehicle = db.relationship("Vehicle", back_populates="odometer_logs")

    def __repr__(self):
        return f"<OdometerLog vehicle={self.vehicle_id} km={self.km}>"