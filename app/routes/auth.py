from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
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
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if User.query.filter_by(email=email).first():
            flash("Este email já está registado.", "warning")
        else:
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
    return response
