from datetime import date

from flask import Blueprint, current_app, render_template, request
from flask_login import current_user

from flaskblog import db
from flaskblog.models import Announcement, Event, Post

main = Blueprint("main", __name__)


@main.app_context_processor
def sidebar_data():
    """Latest announcements and the next events, shown in the sidebar on every page."""
    try:
        latest = (
            Announcement.query.order_by(Announcement.date_posted.desc(), Announcement.id.desc())
            .limit(3)
            .all()
        )
        upcoming = (
            Event.visible_query(current_user)
            .filter(Event.end_date >= date.today())
            .order_by(Event.event_date, Event.id)
            .limit(4)
            .all()
        )
    except Exception:  # never let the sidebar break a page
        db.session.rollback()
        latest, upcoming = [], []
    return {"sidebar_announcements": latest, "sidebar_events": upcoming, "sidebar_today": date.today()}


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    notice = None
    if page == 1:
        notice = Announcement.query.order_by(
            Announcement.date_posted.desc(), Announcement.id.desc()
        ).first()
    return render_template("home.html", posts=posts, notice=notice)


@main.route("/about")
def about():
    return render_template("about.html", title="About")
