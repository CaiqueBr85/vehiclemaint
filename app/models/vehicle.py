from app import db
from datetime import datetime, timezone


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    modelo = db.Column(db.String(80), nullable=False)
    ano = db.Column(db.Integer)
    matricula = db.Column(db.String(20))
    combustivel = db.Column(db.String(30))
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="vehicles")
    odometer_logs = db.relationship("OdometerLog", back_populates="vehicle", cascade="all, delete-orphan", order_by="OdometerLog.data.desc()")
    plans = db.relationship("MaintenancePlan", back_populates="vehicle", cascade="all, delete-orphan")

    @property
    def current_km(self):
        log = OdometerLog.query.filter_by(vehicle_id=self.id).order_by(OdometerLog.data.desc()).first()
        return log.km if log else 0

    @property
    def status_summary(self):
        """Retorna o estado mais crítico dos planos do veículo."""
        statuses = [p.status for p in self.plans if p.ativo]
        if "Vencida" in statuses:
            return "Vencida"
        if "Quase a Vencer" in statuses:
            return "Quase a Vencer"
        return "OK"

    def __repr__(self):
        return f"<Vehicle {self.marca} {self.modelo} ({self.matricula})>"


from app.models.odometer import OdometerLog  # noqa: E402
