from app import db


class Leave(db.Model):
    __tablename__ = "leaves"

    id = db.Column(db.Integer, primary_key=True)
    intern_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    leave_date = db.Column(db.Date, nullable=False, index=True)
    reason = db.Column(db.Text, nullable=False)
    leave_type = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending", index=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    intern = db.relationship("Account", back_populates="leaves")

