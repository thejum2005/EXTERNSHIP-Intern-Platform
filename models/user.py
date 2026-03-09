from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Account(db.Model, UserMixin):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, index=True)  # admin | intern
    password_hash = db.Column(db.String(255), nullable=False)

    attendances = db.relationship("Attendance", back_populates="intern", cascade="all,delete-orphan")
    leaves = db.relationship("Leave", back_populates="intern", cascade="all,delete-orphan")
    projects = db.relationship("Project", back_populates="intern", cascade="all,delete-orphan")
    tasks = db.relationship("Task", back_populates="intern", cascade="all,delete-orphan")
    feedback_items = db.relationship("Feedback", back_populates="intern", cascade="all,delete-orphan")
    intern_friday_items = db.relationship(
        "InternFriday", back_populates="intern", cascade="all,delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_intern(self) -> bool:
        return self.role == "intern"


# Backward-compatible alias for existing imports.
User = Account

