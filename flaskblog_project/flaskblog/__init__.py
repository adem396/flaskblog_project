from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text

from flaskblog.config import Config
from flaskblog.utils import pretty_date

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"


def _upgrade_old_database():
    """create_all() adds new tables but never new columns, so add them here.

    This lets an existing site.db (made before admins existed) keep working.
    """
    columns = {c["name"] for c in inspect(db.engine).get_columns("user")}
    if "is_admin" not in columns:
        with db.engine.begin() as conn:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE'))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    app.add_template_filter(pretty_date, "pretty_date")

    from flaskblog.announcements.routes import announcements
    from flaskblog.errors.handlers import errors
    from flaskblog.events.routes import events
    from flaskblog.main.routes import main
    from flaskblog.posts.routes import posts
    from flaskblog.users.routes import users

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(announcements)
    app.register_blueprint(events)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    from flaskblog import models  # noqa: F401  (registers the tables)

    with app.app_context():
        db.create_all()
        _upgrade_old_database()

    return app
