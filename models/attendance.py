from app import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    intern_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Present")

    intern = db.relationship("Account", back_populates="attendances")

    __table_args__ = (
        db.UniqueConstraint("intern_id", "date", name="uq_attendance_intern_date"),
    )

