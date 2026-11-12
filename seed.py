"""Optional: fill the database with demo data so you can see every page.

Run once from the project folder:   python seed.py
Then log in with  demo@example.com / demo1234   (this demo account is an admin)

Adds: a demo admin, 12 posts (for pagination), 2 announcements and a few
calendar events around today's date.
"""
from datetime import date, timedelta

from flaskblog import bcrypt, create_app, db
from flaskblog.models import Announcement, Event, Post, User

SAMPLE_POSTS = [
    ("Hello, Flask", "My first post. Routes and templates are starting to make sense."),
    ("Why I like templates", "Jinja lets one layout serve every page. Change it once, see it everywhere."),
    ("Forms and validation", "WTForms checks the input so I don't have to write every check by hand."),
    ("Databases with SQLAlchemy", "Users and posts are rows now, not a Python list."),
    ("Splitting the app into a package", "Fewer circular imports, and the files are easier to find."),
    ("Hashing passwords", "Never store the password itself. Bcrypt stores a salted hash."),
    ("Profile pictures", "Resize on upload, save under a random name, delete the old file."),
    ("Create, edit, delete", "Only the author can change a post. Everyone else gets a 403."),
    ("Pagination", "Five posts per page keeps the home page short."),
    ("Password reset by email", "A signed token that expires after 30 minutes."),
    ("Blueprints", "users, posts, main and errors each live in their own folder."),
    ("Custom error pages", "A friendly 404 beats a blank browser error."),
]

SAMPLE_ANNOUNCEMENTS = [
    ("Welcome to the blog", "Create an account to write posts and add your own dates to the calendar."),
    ("Calendar is open", "Add releases, deadlines or exams. Tick 'Visible to everyone' off to keep one private."),
]

today = date.today()
SAMPLE_EVENTS = [  # (title, category, start offset in days, length in days, description)
    ("Release: A Field Guide to Python (sample)", "release", 9, 1, "Example of a book release date."),
    ("Project deadline", "deadline", 3, 1, "Hand in the final version."),
    ("Study Skills exam", "exam", 14, 1, "Chapters 1 and 2."),
    ("Team meeting", "meeting", 1, 1, "Weekly check-in."),
    ("Revision week", "other", 5, 4, "Several days in a row, to see how ranges look."),
]

app = create_app()
with app.app_context():
    user = User.query.filter_by(username="demo").first()
    if user is None:
        user = User(
            username="demo",
            email="demo@example.com",
            password=bcrypt.generate_password_hash("demo1234").decode("utf-8"),
        )
        db.session.add(user)
    user.is_admin = True
    db.session.commit()

    if Post.query.filter_by(user_id=user.id).count() == 0:
        for title, content in SAMPLE_POSTS:
            db.session.add(Post(title=title, content=content, user_id=user.id))
    if Announcement.query.count() == 0:
        for title, content in SAMPLE_ANNOUNCEMENTS:
            db.session.add(Announcement(title=title, content=content, user_id=user.id))
    if Event.query.count() == 0:
        for title, category, offset, length, description in SAMPLE_EVENTS:
            start = today + timedelta(days=offset)
            db.session.add(
                Event(
                    title=title,
                    category=category,
                    event_date=start,
                    end_date=start + timedelta(days=length - 1),
                    description=description,
                    user_id=user.id,
                )
            )
    db.session.commit()
    print("Done. Log in with demo@example.com / demo1234 (admin).")
