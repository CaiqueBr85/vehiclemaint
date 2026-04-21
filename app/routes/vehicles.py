from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.odometer import OdometerLog
from datetime import date

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")


def get_current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid))


@vehicles_bp.route("/")
@jwt_required()
def index():
    user = get_current_user()
    vehicles = Vehicle.query.filter_by(user_id=user.id).all()
    return render_template("vehicles/index.html", user=user, vehicles=vehicles)


@vehicles_bp.route("/create", methods=["GET", "POST"])
@jwt_required()
def create():
    user = get_current_user()
    if request.method == "POST":
        v = Vehicle(
            user_id=user.id,
            marca=request.form["marca"].strip(),
            modelo=request.form["modelo"].strip(),
            matricula=request.form.get("matricula", "").strip() or None,
            ano=request.form.get("ano") or None,
            combustivel=request.form.get("combustivel", "").strip() or None,
            km_inicial=float(request.form.get("km_inicial") or 0),
        )
        db.session.add(v)
        db.session.commit()
        flash("Veículo adicionado com sucesso.", "success")
        return redirect(url_for("vehicles.detail", vehicle_id=v.id))
    return render_template("vehicles/form.html", user=user, vehicle=None)


@vehicles_bp.route("/<int:vehicle_id>")
@jwt_required()
def detail(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    return render_template("vehicles/detail.html", user=user, vehicle=v, today=date.today())


@vehicles_bp.route("/<int:vehicle_id>/edit", methods=["GET", "POST"])
@jwt_required()
def edit(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    if request.method == "POST":
        v.marca = request.form["marca"].strip()
        v.modelo = request.form["modelo"].strip()
        v.matricula = request.form.get("matricula", "").strip() or None
        v.ano = request.form.get("ano") or None
        v.combustivel = request.form.get("combustivel", "").strip() or None
        db.session.commit()
        flash("Veículo atualizado.", "success")
        return redirect(url_for("vehicles.detail", vehicle_id=v.id))
    return render_template("vehicles/form.html", user=user, vehicle=v)


@vehicles_bp.route("/<int:vehicle_id>/delete", methods=["POST"])
@jwt_required()
def delete(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    db.session.delete(v)
    db.session.commit()
    flash("Veículo removido.", "success")
    return redirect(url_for("vehicles.index"))


@vehicles_bp.route("/<int:vehicle_id>/odometer", methods=["POST"])
@jwt_required()
def add_odometer(vehicle_id):
    user = get_current_user()
    v = Vehicle.query.filter_by(id=vehicle_id, user_id=user.id).first_or_404()
    km = float(request.form.get("km", 0))
    data_str = request.form.get("data") or str(date.today())

    # Converter string para objeto date
    try:
        from datetime import datetime
        data = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        data = date.today()

    if km <= v.current_km:
        flash("A nova leitura tem de ser maior que a atual.", "warning")
        return redirect(url_for("vehicles.detail", vehicle_id=v.id))

    log = OdometerLog(vehicle_id=v.id, km=km, data=data)
    db.session.add(log)
    db.session.commit()
    flash("Leitura de odómetro registada.", "success")
    return redirect(url_for("vehicles.detail", vehicle_id=v.id))