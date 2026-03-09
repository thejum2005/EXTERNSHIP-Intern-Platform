from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(role: str):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role != role:
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


admin_required = role_required("admin")
intern_required = role_required("intern")

