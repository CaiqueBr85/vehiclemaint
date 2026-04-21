from app import db
from datetime import datetime


class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    modelo = db.Column(db.String(80), nullable=False)
    matricula = db.Column(db.String(20))
    ano = db.Column(db.Integer)
    combustivel = db.Column(db.String(30))
    km_inicial = db.Column(db.Float, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship(
        "User",
        back_populates="vehicles"
    )
    odometer_logs = db.relationship(
        "OdometerLog",
        back_populates="vehicle",
        lazy="dynamic",
        order_by="OdometerLog.data.desc()",
        cascade="all, delete-orphan"
    )
    plans = db.relationship(
        "MaintenancePlan",
        back_populates="vehicle",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    @property
    def current_km(self):
        last = self.odometer_logs.first()
        return last.km if last else self.km_inicial

    @property
    def status_summary(self):
        statuses = [p.status for p in self.plans if p.ativo]
        if "Vencida" in statuses:
            return "Vencida"
        if "Quase a Vencer" in statuses:
            return "Quase a Vencer"
        return "OK"

    def __repr__(self):
        return f"<Vehicle {self.marca} {self.modelo}>"