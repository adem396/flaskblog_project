from datetime import datetime, timezone

from flask import current_app
from flask_login import UserMixin
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import or_

from flaskblog import db, login_manager
from flaskblog.utils import pretty_date

EVENT_CATEGORIES = [
    ("release", "Release"),
    ("deadline", "Deadline"),
    ("exam", "Exam"),
    ("meeting", "Meeting"),
    ("other", "Other"),
]
CATEGORY_LABELS = dict(EVENT_CATEGORIES)


def utcnow():
    """Current UTC time (naive, as SQLite stores it)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship("Post", backref="author", lazy=True)

    def get_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="password-reset")
        # The end of the hash is included so the link stops working once the password changes.
        return s.dumps({"user_id": self.id, "pw": self.password[-12:]})

    @staticmethod
    def verify_reset_token(token, max_age=1800):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="password-reset")
        try:
            data = s.loads(token, max_age=max_age)
            user = db.session.get(User, data["user_id"])
        except (BadSignature, KeyError, TypeError):
            return None
        if user is None or user.password[-12:] != data.get("pw"):
            return None
        return user

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Announcement(db.Model):
    """Written by admins only, shown to everyone."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", backref="announcements")

    def __repr__(self):
        return f"Announcement('{self.title}', '{self.date_posted}')"


class Event(db.Model):
    """A date (or a range of dates) on the shared calendar."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False, default="other")
    event_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)  # same as event_date for a single day
    description = db.Column(db.Text, nullable=False, default="")
    is_public = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False, default=utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", backref="events")

    @classmethod
    def visible_query(cls, user):
        """Public events, plus the user's own private ones."""
        query = cls.query
        if user.is_authenticated:
            return query.filter(or_(cls.is_public.is_(True), cls.user_id == user.id))
        return query.filter(cls.is_public.is_(True))

    @property
    def category_label(self):
        return CATEGORY_LABELS.get(self.category, "Other")

    @property
    def date_range(self):
        a, b = self.event_date, self.end_date
        if a == b:
            return pretty_date(a)
        if a.year == b.year:
            return f"{a.strftime('%B')} {a.day} \u2013 {pretty_date(b)}"
        return f"{pretty_date(a)} \u2013 {pretty_date(b)}"

    def __repr__(self):
        return f"Event('{self.title}', '{self.event_date}')"
