from app import db
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class MaintenancePlan(db.Model):
    __tablename__ = "maintenance_plans"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    intervalo_km = db.Column(db.Integer)
    intervalo_meses = db.Column(db.Integer)
    margem_alerta_km = db.Column(db.Integer, default=500)
    margem_alerta_dias = db.Column(db.Integer, default=30)
    ultimo_km = db.Column(db.Integer, default=0)
    ultima_data = db.Column(db.Date, default=date.today)
    ativo = db.Column(db.Boolean, default=True)

    vehicle = db.relationship("Vehicle", back_populates="plans")
    records = db.relationship("MaintenanceRecord", back_populates="plan", cascade="all, delete-orphan")
    reminders = db.relationship("Reminder", back_populates="plan", cascade="all, delete-orphan")

    @property
    def next_km(self):
        if self.intervalo_km and self.ultimo_km:
            return self.ultimo_km + self.intervalo_km
        return None

    @property
    def next_date(self):
        if self.intervalo_meses and self.ultima_data:
            try:
                from dateutil.relativedelta import relativedelta
                return self.ultima_data + relativedelta(months=self.intervalo_meses)
            except Exception:
                return self.ultima_data + timedelta(days=self.intervalo_meses * 30)
        return None

    @property
    def status(self):
        """Calcula estado: OK | Quase a Vencer | Vencida"""
        from app.models.vehicle import Vehicle
        from app.models.odometer import OdometerLog

        vehicle = Vehicle.query.get(self.vehicle_id)
        current_km = vehicle.current_km if vehicle else 0
        today = date.today()

        km_vencida = self.next_km and current_km >= self.next_km
        date_vencida = self.next_date and today >= self.next_date

        if km_vencida or date_vencida:
            return "Vencida"

        km_quase = self.next_km and (self.next_km - current_km) <= self.margem_alerta_km
        date_quase = self.next_date and (self.next_date - today).days <= self.margem_alerta_dias

        if km_quase or date_quase:
            return "Quase a Vencer"

        return "OK"

    def update_after_service(self, km, data):
        self.ultimo_km = km
        self.ultima_data = data

    def __repr__(self):
        return f"<MaintenancePlan {self.nome}>"
