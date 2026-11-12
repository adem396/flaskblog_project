from calendar import Calendar, month_name
from collections import defaultdict
from datetime import date, timedelta
from itertools import groupby

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from flaskblog import db
from flaskblog.events.forms import MAX_YEAR, MIN_YEAR, EventForm
from flaskblog.models import Event
from flaskblog.utils import pretty_date

events = Blueprint("events", __name__, url_prefix="/calendar")

MAX_CHIPS_PER_DAY = 3


def _visible_or_404(event_id):
    """Private events of other people look like they don't exist."""
    event = db.get_or_404(Event, event_id)
    if not event.is_public and not (current_user.is_authenticated and event.user_id == current_user.id):
        abort(404)
    return event


@events.route("/")
def month_view():
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)
    if not (1 <= month <= 12 and MIN_YEAR <= year <= MAX_YEAR):
        abort(404)

    weeks = Calendar(firstweekday=0).monthdatescalendar(year, month)  # weeks start on Monday
    first, last = weeks[0][0], weeks[-1][-1]
    found = (
        Event.visible_query(current_user)
        .filter(Event.event_date <= last, Event.end_date >= first)
        .order_by(Event.event_date, Event.id)
        .all()
    )
    by_day = defaultdict(list)
    for event in found:  # a multi-day event appears on every day it covers
        day, stop = max(event.event_date, first), min(event.end_date, last)
        while day <= stop:
            by_day[day].append(event)
            day += timedelta(days=1)

    prev = (year, month - 1) if month > 1 else (year - 1, 12)
    nxt = (year, month + 1) if month < 12 else (year + 1, 1)
    return render_template(
        "calendar.html",
        title=f"{month_name[month]} {year}",
        weeks=weeks,
        by_day=by_day,
        year=year,
        month=month,
        month_label=f"{month_name[month]} {year}",
        today=today,
        prev_month=prev if prev[0] >= MIN_YEAR else None,
        next_month=nxt if nxt[0] <= MAX_YEAR else None,
        max_chips=MAX_CHIPS_PER_DAY,
    )


@events.route("/timeline")
def timeline():
    today = date.today()
    mine = request.args.get("mine") == "1" and current_user.is_authenticated
    query = Event.visible_query(current_user).filter(Event.end_date >= today)
    if mine:
        query = query.filter(Event.user_id == current_user.id)
    items = query.order_by(Event.event_date, Event.id).limit(200).all()

    def month_key(event):  # events already under way count towards the current month
        start = max(event.event_date, today)
        return (start.year, start.month)

    groups = [
        (f"{month_name[key[1]]} {key[0]}", list(group)) for key, group in groupby(items, key=month_key)
    ]
    return render_template("timeline.html", title="Timeline", groups=groups, mine=mine, today=today)


@events.route("/day/<string:iso>")
def day(iso):
    try:
        chosen = date.fromisoformat(iso)
    except ValueError:
        abort(404)
    if not (MIN_YEAR <= chosen.year <= MAX_YEAR):
        abort(404)
    items = (
        Event.visible_query(current_user)
        .filter(Event.event_date <= chosen, Event.end_date >= chosen)
        .order_by(Event.event_date, Event.id)
        .all()
    )
    return render_template(
        "day.html", title=pretty_date(chosen), chosen=chosen, items=items, today=date.today()
    )


@events.route("/event/new", methods=["GET", "POST"])
@login_required
def new_event():
    form = EventForm()
    if request.method == "GET" and request.args.get("date"):
        try:
            form.event_date.data = date.fromisoformat(request.args["date"])
        except ValueError:
            pass
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            category=form.category.data,
            event_date=form.event_date.data,
            end_date=form.end_date.data or form.event_date.data,
            description=form.description.data or "",
            is_public=form.is_public.data,
            user_id=current_user.id,
        )
        db.session.add(event)
        db.session.commit()
        flash("Your event is on the calendar.", "success")
        return redirect(url_for("events.detail", event_id=event.id))
    return render_template("event_form.html", title="New event", form=form, legend="New event")


@events.route("/event/<int:event_id>")
def detail(event_id):
    event = _visible_or_404(event_id)
    return render_template("event.html", title=event.title, event=event)


@events.route("/event/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event = _visible_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403)
    form = EventForm(obj=event)
    if request.method == "GET" and event.end_date == event.event_date:
        form.end_date.data = None  # single-day event: leave the end date empty
    if form.validate_on_submit():
        event.title = form.title.data
        event.category = form.category.data
        event.event_date = form.event_date.data
        event.end_date = form.end_date.data or form.event_date.data
        event.description = form.description.data or ""
        event.is_public = form.is_public.data
        db.session.commit()
        flash("Your event has been updated.", "success")
        return redirect(url_for("events.detail", event_id=event.id))
    return render_template("event_form.html", title="Edit event", form=form, legend="Edit event")


@events.route("/event/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    event = _visible_or_404(event_id)
    if event.user_id != current_user.id and not current_user.is_admin:  # admins can remove anything
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash("The event has been deleted.", "success")
    return redirect(url_for("events.month_view"))
