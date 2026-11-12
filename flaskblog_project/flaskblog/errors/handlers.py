from flask import Blueprint, render_template

from flaskblog import db

errors = Blueprint("errors", __name__)


def _page(code, heading, message):
    return render_template("errors/error.html", code=code, heading=heading, message=message), code


@errors.app_errorhandler(400)
def error_400(error):
    return _page(
        400,
        "That form has expired",
        "Go back, reload the page and send the form again.",
    )


@errors.app_errorhandler(403)
def error_403(error):
    return _page(403, "You can't do that", "You don't have permission to open this page.")


@errors.app_errorhandler(404)
def error_404(error):
    return _page(404, "Page not found", "This page doesn't exist. It may have been moved or deleted.")


@errors.app_errorhandler(413)
def error_413(error):
    return _page(413, "File too large", "Pick a picture smaller than 5 MB.")


@errors.app_errorhandler(500)
def error_500(error):
    db.session.rollback()
    return _page(500, "Something went wrong", "It's on our side. Try again in a moment.")
