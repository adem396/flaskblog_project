from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def pretty_date(value):
    """date/datetime -> 'November 5, 2026' (no zero-padded day, works on Windows too)."""
    return f"{value.strftime('%B')} {value.day}, {value.year}"


def admin_required(view):
    """Log in first, then only let admins through (everyone else gets a 403 page)."""

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
