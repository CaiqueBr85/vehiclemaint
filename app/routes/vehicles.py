from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.odometer import OdometerLog
from datetime import date

vehicles_bp = Blueprint("vehicles", __name__)


def get_current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid))


@vehicles_bp.route("/vehicles")
@jwt_required()
def index():
    user = get_current_user()
    vehicles = Vehicle.query.filter_by(user_id=user.id, ativo=True).all()
    return render_template("vehicles/index.html", user=user, vehicles=vehicles)


@vehicles_bp.route("/vehicles/new", methods=["GET", "POST"])
@jwt_required()
def create():
    user = get_current_user()
    if request.method == "POST":
        v = Vehicle(
            user_id=user.id,
            marca=request.form["marca"],
            modelo=request.form["modelo"],
            ano=request.form.get("ano") or None,
            matricula=request.form.get("matricula"),
            combustivel=request.form.get("combustivel"),
        )
        db.session.add(v)
        db.session.commit()
        flash("Veículo adicionado com sucesso!", "success")
        return redirect(url_for("vehicles.detail", vehicle_id=v.id))
    return render_template("vehicles/form.html", user=user, vehicle=None)


@vehicles_bp.route("/vehicles/<int:vehicle_id>")
@jwt_required()
def detail(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    return render_template("vehicles/detail.html", user=user, vehicle=v)


@vehicles_bp.route("/vehicles/<int:vehicle_id>/edit", methods=["GET", "POST"])
@jwt_required()
def edit(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    if request.method == "POST":
        v.marca = request.form["marca"]
        v.modelo = request.form["modelo"]
        v.ano = request.form.get("ano") or None
        v.matricula = request.form.get("matricula")
        v.combustivel = request.form.get("combustivel")
        db.session.commit()
        flash("Veículo atualizado.", "success")
        return redirect(url_for("vehicles.detail", vehicle_id=v.id))
    return render_template("vehicles/form.html", user=user, vehicle=v)


@vehicles_bp.route("/vehicles/<int:vehicle_id>/delete", methods=["POST"])
@jwt_required()
def delete(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    v.ativo = False
    db.session.commit()
    flash("Veículo removido.", "info")
    return redirect(url_for("vehicles.index"))


@vehicles_bp.route("/vehicles/<int:vehicle_id>/odometer", methods=["POST"])
@jwt_required()
def add_odometer(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    km = int(request.form["km"])
    data_str = request.form.get("data") or str(date.today())
    log = OdometerLog(vehicle_id=v.id, km=km, data=date.fromisoformat(data_str))
    db.session.add(log)
    db.session.commit()
    flash(f"Leitura de {km} km registada.", "success")
    return redirect(url_for("vehicles.detail", vehicle_id=v.id))
