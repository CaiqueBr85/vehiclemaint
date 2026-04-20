from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.plan import MaintenancePlan

dashboard_bp = Blueprint("dashboard", __name__)


def get_current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid)) if uid else None


@dashboard_bp.route("/dashboard")
@jwt_required()
def index():
    user = get_current_user()
    vehicles = Vehicle.query.filter_by(user_id=user.id, ativo=True).all()
    # Agrupa planos por estado
    plans_vencidas = []
    plans_quase = []
    plans_ok = []
    for v in vehicles:
        for p in v.plans:
            if not p.ativo:
                continue
            s = p.status
            if s == "Vencida":
                plans_vencidas.append((v, p))
            elif s == "Quase a Vencer":
                plans_quase.append((v, p))
            else:
                plans_ok.append((v, p))
    return render_template(
        "dashboard/index.html",
        user=user,
        vehicles=vehicles,
        plans_vencidas=plans_vencidas,
        plans_quase=plans_quase,
        plans_ok=plans_ok,
    )
