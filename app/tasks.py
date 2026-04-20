from flask import current_app
from app import db, mail
from app.models.plan import MaintenancePlan
from app.models.reminder import Reminder
from app.models.user import User
from app.models.vehicle import Vehicle
from flask_mail import Message
from datetime import date, datetime, timezone


def check_maintenance_plans():
    """Tarefa diária: verifica planos e envia lembretes por email."""
    from app import create_app
    app = create_app()
    with app.app_context():
        plans = MaintenancePlan.query.filter_by(ativo=True).all()
        for plan in plans:
            status = plan.status
            if status in ("Vencida", "Quase a Vencer"):
                # Verificar se já existe lembrete enviado hoje
                today = date.today()
                already_sent = Reminder.query.filter_by(plan_id=plan.id, estado="ENVIADO").filter(
                    Reminder.agendado_para == today
                ).first()
                if already_sent:
                    continue

                vehicle = Vehicle.query.get(plan.vehicle_id)
                user = User.query.get(vehicle.user_id) if vehicle else None
                if not user or not user.email:
                    continue

                # Registar lembrete
                reminder = Reminder(plan_id=plan.id, agendado_para=today)
                db.session.add(reminder)

                # Enviar email
                try:
                    msg = Message(
                        subject=f"[VehicleMaint] Manutenção {status}: {plan.nome}",
                        recipients=[user.email],
                        html=f"""
                        <h2>Alerta de Manutenção</h2>
                        <p>Olá <strong>{user.nome}</strong>,</p>
                        <p>O plano <strong>{plan.nome}</strong> do teu veículo
                        <strong>{vehicle.marca} {vehicle.modelo}</strong>
                        está com estado: <strong>{status}</strong>.</p>
                        <p>
                            {'Próxima revisão em: ' + str(plan.next_km) + ' km' if plan.next_km else ''}
                            {'<br>Data prevista: ' + str(plan.next_date) if plan.next_date else ''}
                        </p>
                        <p>Acede à plataforma para registar a manutenção.</p>
                        """,
                    )
                    mail.send(msg)
                    reminder.marcar_enviado()
                except Exception as e:
                    print(f"Erro ao enviar email para {user.email}: {e}")

                db.session.commit()
