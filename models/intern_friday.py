from app import db


class InternFriday(db.Model):
    __tablename__ = "intern_friday"

    id = db.Column(db.Integer, primary_key=True)
    intern_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    topic = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)

    intern = db.relationship("Account", back_populates="intern_friday_items")

