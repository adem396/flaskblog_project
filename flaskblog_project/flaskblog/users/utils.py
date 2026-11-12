import os
import secrets
from functools import wraps
from urllib.parse import urljoin, urlparse

from flask import abort, current_app, request, url_for
from flask_login import current_user
from flask_mail import Message
from PIL import Image, ImageOps

from flaskblog import bcrypt, mail

PICTURE_DIR = ("static", "profile_pics")


def save_picture(form_picture):
    """Crop to a square, shrink to 125x125 and save under a random name."""
    _, ext = os.path.splitext(form_picture.filename)
    ext = ".png" if ext.lower() == ".png" else ".jpg"
    picture_fn = secrets.token_hex(8) + ext  # 16 + 4 chars, fits String(20)
    picture_path = os.path.join(current_app.root_path, *PICTURE_DIR, picture_fn)

    img = Image.open(form_picture)
    img = ImageOps.exif_transpose(img)
    img = ImageOps.fit(img, (125, 125))
    if ext == ".jpg":
        img = img.convert("RGB")
    img.save(picture_path)
    return picture_fn


def remove_picture(filename):
    if not filename or filename == "default.jpg":
        return
    try:
        os.remove(os.path.join(current_app.root_path, *PICTURE_DIR, filename))
    except OSError:
        pass


def check_password(hashed, plain):
    try:
        return bcrypt.check_password_hash(hashed, plain)
    except ValueError:  # e.g. password longer than bcrypt's 72-byte limit
        return False


def is_safe_url(target):
    """Only allow redirects to pages on this same site."""
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc


def send_reset_email(user):
    """Returns True if the link was sent (or printed in dev), False if sending failed."""
    token = user.get_reset_token()
    link = url_for("users.reset_token", token=token, _external=True)
    body = (
        "To reset your password, open this link (valid for 30 minutes):\n"
        f"{link}\n\n"
        "If you did not ask for this, ignore this email and nothing will change.\n"
    )

    if not current_app.config.get("MAIL_USERNAME"):
        # No email account configured: show the link in the terminal for development.
        current_app.logger.warning("Email not configured. Reset link for %s: %s", user.email, link)
        return True

    msg = Message(
        "Password reset request",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user.email],
        body=body,
    )
    try:
        mail.send(msg)
    except Exception:  # SMTP login failed, no network, ...
        current_app.logger.exception("Could not send reset email")
        return False
    return True


def admin_required(view):
    """Only logged-in admins may open the page; everyone else gets 403 (or the login page)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
