from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from flaskblog import db
from flaskblog.announcements.forms import AnnouncementForm
from flaskblog.models import Announcement
from flaskblog.utils import admin_required

announcements = Blueprint("announcements", __name__, url_prefix="/announcements")


@announcements.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    items = Announcement.query.order_by(Announcement.date_posted.desc(), Announcement.id.desc()).paginate(
        page=page, per_page=5
    )
    return render_template("announcements.html", title="Announcements", items=items)


@announcements.route("/new", methods=["GET", "POST"])
@admin_required
def new():
    form = AnnouncementForm()
    if form.validate_on_submit():
        db.session.add(
            Announcement(title=form.title.data, content=form.content.data, user_id=current_user.id)
        )
        db.session.commit()
        flash("Your announcement is published.", "success")
        return redirect(url_for("announcements.index"))
    return render_template(
        "announcement_form.html", title="New announcement", form=form, legend="New announcement"
    )


@announcements.route("/<int:announcement_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(announcement_id):
    item = db.get_or_404(Announcement, announcement_id)
    form = AnnouncementForm(obj=item)
    if form.validate_on_submit():
        item.title = form.title.data
        item.content = form.content.data
        db.session.commit()
        flash("The announcement has been updated.", "success")
        return redirect(url_for("announcements.index"))
    return render_template(
        "announcement_form.html", title="Edit announcement", form=form, legend="Edit announcement"
    )


@announcements.route("/<int:announcement_id>/delete", methods=["POST"])
@admin_required
def delete(announcement_id):
    item = db.get_or_404(Announcement, announcement_id)
    db.session.delete(item)
    db.session.commit()
    flash("The announcement has been deleted.", "success")
    return redirect(url_for("announcements.index"))
