from datetime import date, datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app import db
from models.attendance import Attendance
from models.feedback import Feedback
from models.intern_friday import InternFriday
from models.leave import Leave
from models.project import Project
from models.task import Task
from routes.decorators import intern_required
from routes.pagination import paginate


intern_bp = Blueprint("intern", __name__)

# India timezone
IST = ZoneInfo("Asia/Kolkata")


@intern_bp.route("/dashboard")
@intern_required
def dashboard():
    today = date.today()

    attendance_today = Attendance.query.filter_by(
        intern_id=current_user.id, date=today
    ).first()

    pending_leaves = Leave.query.filter_by(
        intern_id=current_user.id, status="Pending"
    ).count()

    assigned_projects = Project.query.filter_by(
        intern_id=current_user.id, status="Assigned"
    ).count()

    assigned_tasks = Task.query.filter_by(
        intern_id=current_user.id, status="Assigned"
    ).count()

    intern_friday_latest = (
        InternFriday.query.filter_by(intern_id=current_user.id)
        .order_by(InternFriday.date.desc())
        .first()
    )

    return render_template(
        "intern_dashboard.html",
        attendance_today=attendance_today,
        pending_leaves=pending_leaves,
        assigned_projects=assigned_projects,
        assigned_tasks=assigned_tasks,
        intern_friday_latest=intern_friday_latest,
    )


@intern_bp.route("/attendance")
@intern_required
def attendance():

    q = Attendance.query.filter_by(intern_id=current_user.id).order_by(
        Attendance.date.desc(), Attendance.time.desc()
    )

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    p = paginate(q, page=page, per_page=per_page)

    today = date.today()

    attendance_today = Attendance.query.filter_by(
        intern_id=current_user.id, date=today
    ).first()

    return render_template(
        "attendance.html",
        page=p,
        attendance_today=attendance_today,
        today=today,
    )


@intern_bp.route("/attendance/mark", methods=["POST"])
@intern_required
def mark_attendance():

    today = date.today()

    # Get IST time
    now = datetime.now(IST)

    status = request.form.get("status", "Present")

    attendance = Attendance(
        intern_id=current_user.id,
        date=today,
        time=now.time().replace(microsecond=0),
        status=status,
    )

    db.session.add(attendance)

    try:
        db.session.commit()
        flash("Attendance marked successfully.", "success")

    except IntegrityError:
        db.session.rollback()
        flash("You have already marked attendance today.", "warning")

    return redirect(url_for("intern.attendance"))


@intern_bp.route("/leave", methods=["GET", "POST"])
@intern_required
def leave():

    if request.method == "POST":

        leave_date_str = (request.form.get("leave_date") or "").strip()
        leave_type = (request.form.get("leave_type") or "").strip()
        reason = (request.form.get("reason") or "").strip()

        if not leave_date_str or not leave_type or not reason:
            flash("All fields are required.", "danger")
            return redirect(url_for("intern.leave"))

        try:
            leave_date = datetime.strptime(leave_date_str, "%Y-%m-%d").date()

        except ValueError:
            flash("Invalid leave date.", "danger")
            return redirect(url_for("intern.leave"))

        leave = Leave(
            intern_id=current_user.id,
            leave_date=leave_date,
            leave_type=leave_type,
            reason=reason,
            status="Pending",
        )

        db.session.add(leave)
        db.session.commit()

        flash("Leave request submitted.", "success")

        return redirect(url_for("intern.leave"))

    q = Leave.query.filter_by(intern_id=current_user.id).order_by(
        Leave.leave_date.desc(), Leave.id.desc()
    )

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    p = paginate(q, page=page, per_page=per_page)

    return render_template("leave.html", page=p)


@intern_bp.route("/projects")
@intern_required
def projects():

    q = Project.query.filter_by(intern_id=current_user.id).order_by(
        Project.deadline.asc(), Project.id.desc()
    )

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    p = paginate(q, page=page, per_page=per_page)

    return render_template("projects.html", page=p)


@intern_bp.route("/projects/<int:project_id>/complete", methods=["POST"])
@intern_required
def complete_project(project_id):

    project = Project.query.get_or_404(project_id)

    if project.intern_id != current_user.id:
        flash("Not allowed.", "danger")
        return redirect(url_for("intern.projects"))

    project.status = "Completed"

    db.session.commit()

    flash("Project marked as completed.", "success")

    return redirect(url_for("intern.projects"))


@intern_bp.route("/tasks")
@intern_required
def tasks():

    q = Task.query.filter_by(intern_id=current_user.id).order_by(Task.id.desc())

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    p = paginate(q, page=page, per_page=per_page)

    return render_template("tasks.html", page=p)


@intern_bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
@intern_required
def complete_task(task_id):

    task = Task.query.get_or_404(task_id)

    if task.intern_id != current_user.id:
        flash("Not allowed.", "danger")
        return redirect(url_for("intern.tasks"))

    task.status = "Completed"

    db.session.commit()

    flash("Task marked as completed.", "success")

    return redirect(url_for("intern.tasks"))


@intern_bp.route("/feedback")
@intern_required
def feedback():

    q = Feedback.query.filter_by(intern_id=current_user.id).order_by(
        Feedback.date.desc(), Feedback.id.desc()
    )

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    p = paginate(q, page=page, per_page=per_page)

    return render_template("feedback.html", page=p)


@intern_bp.route("/intern-friday")
@intern_required
def intern_friday():

    q = InternFriday.query.filter_by(intern_id=current_user.id).order_by(
        InternFriday.date.desc()
    )

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    p = paginate(q, page=page, per_page=per_page)

    return render_template("intern_friday.html", page=p)