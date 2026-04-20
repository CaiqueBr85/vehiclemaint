from flask import Blueprint, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def get_current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid))


def require_admin(f):
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != "admin":
            flash("Acesso restrito a administradores.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/users")
@require_admin
def users():
    user = get_current_user()
    all_users = User.query.order_by(User.criado_em.desc()).all()
    return render_template("admin/users.html", user=user, all_users=all_users)


@admin_bp.route("/users/<int:uid>/toggle", methods=["POST"])
@require_admin
def toggle_user(uid):
    u = User.query.get_or_404(uid)
    u.ativo = not u.ativo
    db.session.commit()
    flash(f"Utilizador {'ativado' if u.ativo else 'desativado'}.", "info")
    return redirect(url_for("admin.users"))
