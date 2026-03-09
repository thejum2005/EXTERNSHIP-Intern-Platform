from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app import db
from models.user import Account

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = Account.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        login_user(user)
        flash("Welcome back!", "success")
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("intern.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def _get_serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config["SECRET_KEY"]
    return URLSafeTimedSerializer(secret_key=secret_key, salt="spi-edge-password-reset")

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("forgot_password.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("forgot_password.html")

        user = Account.query.filter_by(email=email).first()

        if not user:
            flash("Account not found.", "danger")
            return render_template("forgot_password.html")

        # Update password
        user.set_password(password)
        db.session.commit()

        flash("Password updated successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    s = _get_serializer()
    try:
        data = s.loads(token, max_age=60 * 60)  # 1 hour
        user_id = data["user_id"]
    except SignatureExpired:
        flash("Reset link has expired. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("Invalid reset link.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = Account.query.get_or_404(user_id)

    if request.method == "POST":
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""
        if not password or not confirm:
            flash("Both password fields are required.", "danger")
            return render_template("reset_password.html", token=token)
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("reset_password.html", token=token)

        user.set_password(password)
        db.session.commit()
        flash("Password has been reset. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        role = (request.form.get("role") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        if role not in {"admin", "intern"}:
            flash("Please select a valid role (Admin or Intern).", "danger")
            return render_template("register.html")

        if not name or not email or not password or not confirm:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if Account.query.filter_by(email=email).first():
            flash("Email already exists. Please login or use forgot password.", "warning")
            return render_template("register.html")

        acc = Account(name=name, email=email, role=role, password_hash="")
        acc.set_password(password)
        db.session.add(acc)
        db.session.commit()
        flash("Account created successfully. You can login now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

