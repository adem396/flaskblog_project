# Flask Blog

A blog where people can register, log in, write posts, edit or delete their own posts,
change their profile picture and reset a forgotten password. It also has
**announcements** (written by admins) and a shared **calendar** where everyone can add
their own dates, for example when a book comes out. Built by following Corey Schafer's
Flask tutorial series, then extended.

## Run it

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (macOS/Linux: source venv/bin/activate)
python -m pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000. The database is created (and updated) automatically in `instance/site.db`.

Optional: `python seed.py` adds a demo admin (demo@example.com / demo1234), 12 posts,
2 announcements and a few calendar events.

## Admin and announcements

Anyone can register, but only admins can publish announcements. To make yourself admin:

1. Register on the website.
2. In the project folder run `python make_admin.py your-email@example.com`
   (add `--revoke` to remove admin rights).
3. Log in again. A "New announcement" button appears on the Announcements page.

Admins can also delete any calendar event (moderation). They cannot edit other people's events.

## Calendar

- **Month** view with colour-coded events, **Timeline** view of what is coming up.
- Any logged-in user can add events: a date (or a range of dates), a type
  (Release, Deadline, Exam, Meeting, Other) and optional details.
- Events are public by default. Untick "Visible to everyone" to keep one on your own calendar only.
- Only the author can edit an event.

## Settings

Copy `.env.example` to `.env` and fill it in. Without it the app still runs:

- `SECRET_KEY`: use a long random string if the project is ever published.
- `EMAIL_USER` / `EMAIL_PASS`: needed to really send password-reset emails
  (for Gmail, create an App Password). If they are empty, the reset link is
  printed in the terminal instead.

## Project layout

```
run.py                  starts the app
make_admin.py           gives an account admin rights
seed.py                 optional demo data
flaskblog/
  __init__.py           create_app() and the extensions
  config.py             settings
  models.py             User, Post, Announcement, Event
  utils.py              admin_required decorator, date formatting
  users/                register, login, account, password reset
  posts/                create, read, update, delete posts
  announcements/        announcements (admin only to write)
  events/               calendar: month, timeline, day, add/edit/delete events
  main/                 home (paginated), about, sidebar data
  errors/               custom 400 / 403 / 404 / 413 / 500 pages
  templates/ static/    HTML and CSS/JS
```
