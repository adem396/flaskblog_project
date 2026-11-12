from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from flaskblog.models import User


def _check_bcrypt_length(password):
    # bcrypt only looks at the first 72 bytes and refuses anything longer.
    if len(password.data.encode("utf-8")) > 72:
        raise ValidationError("Password is too long (72 bytes maximum).")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("That username is taken. Please choose a different one.")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data.lower()).first():
            raise ValidationError("That email is already registered. Try logging in instead.")

    def validate_password(self, password):
        _check_bcrypt_length(password)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField(
        "Profile picture (JPG or PNG)", validators=[FileAllowed(["jpg", "jpeg", "png"])]
    )
    submit = SubmitField("Save changes")

    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError("That username is taken. Please choose a different one.")

    def validate_email(self, email):
        if email.data.lower() != current_user.email:
            if User.query.filter_by(email=email.data.lower()).first():
                raise ValidationError("That email is already registered.")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send reset link")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data.lower()).first() is None:
            raise ValidationError("There is no account with that email. Sign up first.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm new password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Save new password")

    def validate_password(self, password):
        _check_bcrypt_length(password)
