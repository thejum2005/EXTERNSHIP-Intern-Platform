import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

from config import get_config

# Global extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db.init_app(app)
    login_manager.init_app(app)

    # Import models so SQLAlchemy registers them
    from models.user import Account
    from models.attendance import Attendance
    from models.leave import Leave
    from models.project import Project
    from models.task import Task
    from models.feedback import Feedback
    from models.intern_friday import InternFriday

    # Create tables automatically
    with app.app_context():
        db.create_all()

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.intern_routes import intern_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(intern_bp, url_prefix="/intern")

    @app.route("/")
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))

        return redirect(url_for("intern.dashboard"))

    return app


@login_manager.user_loader
def load_user(user_id):
    from models.user import Account
    return Account.query.get(int(user_id))


def create_default_admin():
    """Create default admin if not exists"""
    from models.user import Account
    from werkzeug.security import generate_password_hash

    admin_email = "admin@spi-edge.local"

    admin = Account.query.filter_by(email=admin_email).first()
    if admin:
        return admin

    admin = Account(
        name="System Admin",
        email=admin_email,
        role="admin",
        password_hash=generate_password_hash("admin123")
    )

    db.session.add(admin)
    db.session.commit()

    return admin


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        create_default_admin()

    app.run(host="0.0.0.0", port=5000)