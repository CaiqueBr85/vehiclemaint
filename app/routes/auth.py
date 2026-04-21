from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import (
    create_access_token, set_access_cookies, unset_jwt_cookies,
    jwt_required, get_jwt_identity, verify_jwt_in_request
)
from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


def already_logged_in():
    """Verifica se já existe um token JWT válido no cookie."""
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        return uid is not None
    except Exception:
        return False


@auth_bp.route("/")
def index():
    if already_logged_in():
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if already_logged_in():
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email, ativo=True).first()
        if user and user.check_password(password):
            token = create_access_token(identity=str(user.id))
            response = redirect(url_for("dashboard.index"))
            set_access_cookies(response, token)
            return response
        flash("Email ou palavra-passe incorretos.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if already_logged_in():
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("password_confirm", "")

        if password != confirm:
            flash("As passwords não coincidem.", "danger")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("A password deve ter pelo menos 8 caracteres.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Este email já está registado.", "warning")
            return render_template("auth/register.html")

        user = User(nome=nome, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))
        response = redirect(url_for("dashboard.index"))
        set_access_cookies(response, token)
        return response

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    response = redirect(url_for("auth.login"))
    unset_jwt_cookies(response)
    flash("Sessão terminada com sucesso.", "success")
    return response


@auth_bp.route("/perfil", methods=["GET", "POST"])
@jwt_required()
def perfil():
    uid = get_jwt_identity()
    user = User.query.get(int(uid))

    if not user:
        return redirect(url_for("auth.logout"))

    if request.method == "POST":
        action = request.form.get("action")

        # ── Atualizar nome e email ──────────────────────────────────────────
        if action == "update_info":
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()

            if not nome or not email:
                flash("Nome e email são obrigatórios.", "danger")
                return redirect(url_for("auth.perfil"))

            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != user.id:
                flash("Esse email já está em uso.", "danger")
                return redirect(url_for("auth.perfil"))

            user.nome = nome
            user.email = email
            db.session.commit()
            flash("Informações atualizadas com sucesso!", "success")

        # ── Alterar senha ───────────────────────────────────────────────────
        elif action == "change_password":
            senha_atual = request.form.get("senha_atual", "")
            nova_senha = request.form.get("nova_senha", "")
            confirmar_senha = request.form.get("confirmar_senha", "")

            if not user.check_password(senha_atual):
                flash("Senha atual incorreta.", "danger")
                return redirect(url_for("auth.perfil"))

            if len(nova_senha) < 8:
                flash("A nova senha deve ter pelo menos 8 caracteres.", "danger")
                return redirect(url_for("auth.perfil"))

            if nova_senha != confirmar_senha:
                flash("As novas senhas não coincidem.", "danger")
                return redirect(url_for("auth.perfil"))

            user.set_password(nova_senha)
            db.session.commit()
            flash("Senha alterada com sucesso!", "success")

        # ── Eliminar conta ──────────────────────────────────────────────────
        elif action == "delete_account":
            db.session.delete(user)
            db.session.commit()
            response = redirect(url_for("auth.login"))
            unset_jwt_cookies(response)
            flash("A tua conta foi eliminada.", "info")
            return response

        return redirect(url_for("auth.perfil"))

    # ── GET: estatísticas ───────────────────────────────────────────────────
    from app.models.vehicle import Vehicle
    from app.models.plan import MaintenancePlan
    from app.models.record import MaintenanceRecord

    total_veiculos = Vehicle.query.filter_by(user_id=user.id).count()

    total_manutencoes = (
        db.session.query(MaintenanceRecord)
        .join(MaintenancePlan, MaintenanceRecord.plan_id == MaintenancePlan.id)
        .join(Vehicle, MaintenancePlan.vehicle_id == Vehicle.id)
        .filter(Vehicle.user_id == user.id)
        .count()
    )

    total_veiculos = Vehicle.query.filter_by(user_id=user.id).count()
        # GET — estatísticas
    MESES_PT = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    if hasattr(user, "criado_em") and user.criado_em:
        membro_desde = f"{user.criado_em.day} {MESES_PT[user.criado_em.month]} {user.criado_em.year}"
    else:
        membro_desde = "N/A"

    return render_template(
        "auth/perfil.html",
        user=user,
        total_veiculos=total_veiculos,
        total_manutencoes=total_manutencoes,
        membro_desde=membro_desde,
    )