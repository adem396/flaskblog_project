"""Make an existing account an admin (admins publish the announcements).

Usage (from the project folder):
    python make_admin.py you@example.com            -> make admin
    python make_admin.py you@example.com --revoke   -> remove admin rights

Register the account on the website first, then run this.
"""
import sys

from flaskblog import create_app, db
from flaskblog.models import User

args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    print(__doc__)
    sys.exit(1)

email = args[0].lower()
revoke = "--revoke" in sys.argv

app = create_app()
with app.app_context():
    user = User.query.filter_by(email=email).first()
    if user is None:
        print(f"No account with the email {email}. Register on the website first.")
        sys.exit(1)
    user.is_admin = not revoke
    db.session.commit()
    print(f"{user.username} is now {'a regular user' if revoke else 'an admin'}.")
