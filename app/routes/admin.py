from flask import Blueprint, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def get_current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid))


@admin_bp.route("/users")
@jwt_required()
def users():
    user = get_current_user()
    if user.role != "admin":
        flash("Acesso negado.", "danger")
        return redirect(url_for("dashboard.index"))
    all_users = User.query.order_by(User.criado_em.desc()).all()
    return render_template("admin/users.html", user=user, users=all_users)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@jwt_required()
def toggle_user(user_id):
    user = get_current_user()
    if user.role != "admin":
        return redirect(url_for("dashboard.index"))
    u = User.query.get_or_404(user_id)
    u.ativo = not u.ativo
    db.session.commit()
    flash(f"Utilizador {'ativado' if u.ativo else 'desativado'}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@jwt_required()
def toggle_role(user_id):
    user = get_current_user()
    if user.role != "admin":
        return redirect(url_for("dashboard.index"))
    u = User.query.get_or_404(user_id)
    u.role = "user" if u.role == "admin" else "admin"
    db.session.commit()
    flash(f"Role alterado para {u.role}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@jwt_required()
def delete_user(user_id):
    user = get_current_user()
    if user.role != "admin" or user.id == user_id:
        return redirect(url_for("dashboard.index"))
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash("Utilizador apagado.", "success")
    return redirect(url_for("admin.users"))