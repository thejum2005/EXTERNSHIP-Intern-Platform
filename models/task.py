from app import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    intern_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="Assigned", index=True)  # Assigned|Completed

    intern = db.relationship("Account", back_populates="tasks")

