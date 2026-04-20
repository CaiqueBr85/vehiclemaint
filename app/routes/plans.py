from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.plan import MaintenancePlan
from app.models.record import MaintenanceRecord
from datetime import date

plans_bp = Blueprint("plans", __name__)


def get_current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid))


@plans_bp.route("/vehicles/<int:vehicle_id>/plans/new", methods=["GET", "POST"])
@jwt_required()
def create(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    if request.method == "POST":
        p = MaintenancePlan(
            vehicle_id=v.id,
            nome=request.form["nome"],
            intervalo_km=request.form.get("intervalo_km") or None,
            intervalo_meses=request.form.get("intervalo_meses") or None,
            margem_alerta_km=request.form.get("margem_alerta_km") or 500,
            margem_alerta_dias=request.form.get("margem_alerta_dias") or 30,
            ultimo_km=v.current_km,
            ultima_data=date.today(),
        )
        db.session.add(p)
        db.session.commit()
        flash(f"Plano '{p.nome}' criado!", "success")
        return redirect(url_for("vehicles.detail", vehicle_id=v.id))
    return render_template("plans/form.html", user=user, vehicle=v, plan=None)


@plans_bp.route("/plans/<int:plan_id>/record", methods=["GET", "POST"])
@jwt_required()
def add_record(plan_id):
    user = get_current_user()
    p = MaintenancePlan.query.get_or_404(plan_id)
    v = Vehicle.query.filter_by(id=p.vehicle_id, user_id=user.id).first_or_404()
    if request.method == "POST":
        km = int(request.form["km"])
        data_str = request.form.get("data") or str(date.today())
        record = MaintenanceRecord(
            plan_id=p.id,
            data=date.fromisoformat(data_str),
            km=km,
            custo=request.form.get("custo") or None,
            notas=request.form.get("notas"),
        )
        db.session.add(record)
        p.update_after_service(km, date.fromisoformat(data_str))
        # Cancelar lembretes pendentes
        from app.models.reminder import Reminder
        for r in p.reminders:
            if r.estado == "PENDENTE":
                r.estado = "CANCELADO"
        db.session.commit()
        flash("Manutenção registada! Próxima revisão recalculada.", "success")
        return redirect(url_for("vehicles.detail", vehicle_id=v.id))
    return render_template("plans/record_form.html", user=user, vehicle=v, plan=p)


@plans_bp.route("/plans/<int:plan_id>/delete", methods=["POST"])
@jwt_required()
def delete(plan_id):
    user = get_current_user()
    p = MaintenancePlan.query.get_or_404(plan_id)
    Vehicle.query.filter_by(id=p.vehicle_id, user_id=user.id).first_or_404()
    p.ativo = False
    db.session.commit()
    flash("Plano removido.", "info")
    return redirect(url_for("vehicles.detail", vehicle_id=p.vehicle_id))
