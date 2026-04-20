from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
bcrypt = Bcrypt()
scheduler = BackgroundScheduler()


def create_app():
    app = Flask(__name__)

    # Configuração
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///vehiclemaint.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False  # True em produção (HTTPS)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    # Registar blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.vehicles import vehicles_bp
    from app.routes.plans import plans_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(plans_bp)
    app.register_blueprint(admin_bp)

    # Iniciar scheduler (apenas uma vez)
    if not scheduler.running:
        from app.tasks import check_maintenance_plans
        scheduler.add_job(check_maintenance_plans, "interval", hours=24, id="daily_check")
        scheduler.start()

    return app
