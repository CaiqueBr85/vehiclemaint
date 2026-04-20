from app import db
from datetime import date
from sqlalchemy import Numeric


class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_records"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("maintenance_plans.id"), nullable=False)
    data = db.Column(db.Date, default=date.today, nullable=False)
    km = db.Column(db.Integer, nullable=False)
    custo = db.Column(Numeric(10, 2))
    notas = db.Column(db.Text)

    plan = db.relationship("MaintenancePlan", back_populates="records")

    def __repr__(self):
        return f"<MaintenanceRecord plan={self.plan_id} km={self.km}>"
