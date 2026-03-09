from datetime import date, datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app import db
from models.attendance import Attendance
from models.feedback import Feedback
from models.intern_friday import InternFriday
from models.leave import Leave
from models.project import Project
from models.task import Task
from models.user import Account
from routes.decorators import admin_required
from routes.pagination import paginate

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    total_interns = Account.query.filter_by(role="intern").count()
    pending_leaves = Leave.query.filter_by(status="Pending").count()
    assigned_projects = Project.query.filter_by(status="Assigned").count()
    assigned_tasks = Task.query.filter_by(status="Assigned").count()
    today_attendance = Attendance.query.filter_by(date=date.today()).count()

    return render_template(
        "admin_dashboard.html",
        total_interns=total_interns,
        pending_leaves=pending_leaves,
        assigned_projects=assigned_projects,
        assigned_tasks=assigned_tasks,
        today_attendance=today_attendance,
    )


@admin_bp.route("/interns", methods=["GET"])
@admin_required
def interns():
    interns_q = Account.query.filter_by(role="intern").order_by(Account.name.asc())
    interns_list = interns_q.all()
    return render_template("admin_interns.html", interns=interns_list)

@admin_bp.route("/attendance")
@admin_required
def attendance():

    intern_id = request.args.get("intern_id", type=int)
    month_str = (request.args.get("month") or "").strip()

    interns = Account.query.filter_by(role="intern").order_by(Account.name.asc()).all()

    q = Attendance.query.join(Account, Attendance.intern_id == Account.id)\
        .filter(Account.role == "intern")

    # Do not show anything until intern selected
    if not intern_id:
        q = q.filter(False)

    if intern_id:
        q = q.filter(Account.id == intern_id)

    # Month filter
    if month_str:
        try:
            year, month = month_str.split("-")
            q = q.filter(
                db.extract("year", Attendance.date) == int(year),
                db.extract("month", Attendance.date) == int(month)
            )
        except ValueError:
            flash("Invalid month selected", "warning")

    q = q.order_by(Attendance.date.desc(), Attendance.time.desc())

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    p = paginate(q, page=page, per_page=per_page)

    return render_template(
        "admin_attendance.html",
        page=p,
        interns=interns,
        selected_intern_id=intern_id,
        selected_month=month_str
    )

@admin_bp.route("/leaves")
@admin_required
def leaves():
    status = (request.args.get("status") or "").strip()

    q = Leave.query.join(Account, Leave.intern_id == Account.id).filter(Account.role == "intern")
    if status:
        q = q.filter(Leave.status == status)
    q = q.order_by(Leave.leave_date.desc(), Leave.id.desc())

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)
    p = paginate(q, page=page, per_page=per_page)
    return render_template("admin_leave.html", page=p, status_filter=status)


@admin_bp.route("/leaves/<int:leave_id>/approve", methods=["POST"])
@admin_required
def approve_leave(leave_id: int):
    leave = Leave.query.get_or_404(leave_id)
    leave.status = "Approved"
    leave.rejection_reason = None
    db.session.commit()
    flash("Leave approved.", "success")
    return redirect(url_for("admin.leaves"))


@admin_bp.route("/leaves/<int:leave_id>/reject", methods=["POST"])
@admin_required
def reject_leave(leave_id: int):
    leave = Leave.query.get_or_404(leave_id)
    reason = (request.form.get("rejection_reason") or "").strip()
    if not reason:
        flash("Rejection reason is required.", "danger")
        return redirect(url_for("admin.leaves"))
    leave.status = "Rejected"
    leave.rejection_reason = reason
    db.session.commit()
    flash("Leave rejected.", "warning")
    return redirect(url_for("admin.leaves"))


@admin_bp.route("/projects", methods=["GET", "POST"])
@admin_required
def projects():
    interns = Account.query.filter_by(role="intern").order_by(Account.name.asc()).all()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        deadline_str = (request.form.get("deadline") or "").strip()
        intern_id = request.form.get("intern_id", type=int)

        if not title or not description or not deadline_str or not intern_id:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin.projects"))

        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid deadline date.", "danger")
            return redirect(url_for("admin.projects"))

        p = Project(title=title, description=description, deadline=deadline, intern_id=intern_id, status="Assigned")
        db.session.add(p)
        db.session.commit()
        flash("Project assigned.", "success")
        return redirect(url_for("admin.projects"))

    q = Project.query.join(Account, Project.intern_id == Account.id).order_by(Project.deadline.asc(), Project.id.desc())
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)
    p = paginate(q, page=page, per_page=per_page)
    return render_template("admin_projects.html", page=p, interns=interns)


@admin_bp.route("/tasks", methods=["GET", "POST"])
@admin_required
def tasks():
    interns = Account.query.filter_by(role="intern").order_by(Account.name.asc()).all()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        intern_id = request.form.get("intern_id", type=int)

        if not title or not description or not intern_id:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin.tasks"))

        t = Task(title=title, description=description, intern_id=intern_id, status="Assigned")
        db.session.add(t)
        db.session.commit()
        flash("Task assigned.", "success")
        return redirect(url_for("admin.tasks"))

    q = Task.query.join(Account, Task.intern_id == Account.id).order_by(Task.id.desc())
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)
    p = paginate(q, page=page, per_page=per_page)
    return render_template("admin_tasks.html", page=p, interns=interns)


@admin_bp.route("/feedback", methods=["GET", "POST"])
@admin_required
def feedback():
    interns = Account.query.filter_by(role="intern").order_by(Account.name.asc()).all()

    if request.method == "POST":
        intern_id = request.form.get("intern_id", type=int)
        week = (request.form.get("week") or "").strip()
        feedback_text = (request.form.get("feedback_text") or "").strip()
        date_str = (request.form.get("date") or "").strip()

        if not intern_id or not week or not feedback_text or not date_str:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin.feedback"))

        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid feedback date.", "danger")
            return redirect(url_for("admin.feedback"))

        f = Feedback(intern_id=intern_id, week=week, feedback_text=feedback_text, date=d)
        db.session.add(f)
        db.session.commit()
        flash("Feedback saved.", "success")
        return redirect(url_for("admin.feedback"))

    q = Feedback.query.join(Account, Feedback.intern_id == Account.id).order_by(Feedback.date.desc(), Feedback.id.desc())
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)
    p = paginate(q, page=page, per_page=per_page)
    return render_template("admin_feedback.html", page=p, interns=interns)


@admin_bp.route("/intern-friday", methods=["GET", "POST"])
@admin_required
def intern_friday():
    interns = Account.query.filter_by(role="intern").order_by(Account.name.asc()).all()

    if request.method == "POST":
        intern_id = request.form.get("intern_id", type=int)
        topic = (request.form.get("topic") or "").strip()
        date_str = (request.form.get("date") or "").strip()

        if not intern_id or not topic or not date_str:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin.intern_friday"))

        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date.", "danger")
            return redirect(url_for("admin.intern_friday"))

        item = InternFriday(intern_id=intern_id, topic=topic, date=d)
        db.session.add(item)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Could not save Intern Friday selection.", "danger")
            return redirect(url_for("admin.intern_friday"))

        flash("Intern Friday assigned.", "success")
        return redirect(url_for("admin.intern_friday"))

    q = InternFriday.query.join(Account, InternFriday.intern_id == Account.id).order_by(InternFriday.date.desc())
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)
    p = paginate(q, page=page, per_page=per_page)
    return render_template("admin_intern_friday.html", page=p, interns=interns)

