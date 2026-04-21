from app import db
from datetime import datetime, timezone


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("maintenance_plans.id"), nullable=False)
    agendado_para = db.Column(db.Date)
    estado = db.Column(db.String(20), default="PENDENTE")
    enviado_em = db.Column(db.DateTime)

    plan = db.relationship("MaintenancePlan", back_populates="reminders")

    def marcar_enviado(self):
        self.estado = "ENVIADO"
        self.enviado_em = datetime.now(timezone.utc)

    def __repr__(self):
        return f"<Reminder plan={self.plan_id} estado={self.estado}>"