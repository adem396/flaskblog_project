from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image, UnidentifiedImageError

from flaskblog import bcrypt, db
from flaskblog.models import Post, User
from flaskblog.users.forms import (
    LoginForm,
    RegistrationForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm,
)
from flaskblog.users.utils import (
    check_password,
    is_safe_url,
    remove_picture,
    save_picture,
    send_reset_email,
)

users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created. You can now log in.", "success")
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for("main.home"))
        flash("Login failed. Check your email and password.", "danger")
    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        new_picture = None
        if form.picture.data:
            try:
                new_picture = save_picture(form.picture.data)
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                flash("That file could not be read as an image. Try a JPG or PNG.", "danger")
                new_picture = False
        if new_picture is not False:
            if new_picture:
                remove_picture(current_user.image_file)
                current_user.image_file = new_picture
            current_user.username = form.username.data
            current_user.email = form.email.data.lower()
            db.session.commit()
            flash("Your account has been updated.", "success")
            return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template("account.html", title="Account", image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("user_posts.html", title=user.username, posts=posts, user=user)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if send_reset_email(user):
            flash("We sent you an email with a link to reset your password.", "info")
            return redirect(url_for("users.login"))
        flash("The email could not be sent. Please try again later.", "danger")
    return render_template("reset_request.html", title="Reset password", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That reset link is invalid or has expired. Request a new one.", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        db.session.commit()
        flash("Your password has been updated. You can now log in.", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Choose a new password", form=form)
