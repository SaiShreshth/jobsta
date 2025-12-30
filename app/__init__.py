import os
from flask import Flask
from .config import Config
from .extensions import db, migrate, mail, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)

    from . import models

    # Register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from .jobs import bp as jobs_bp
    app.register_blueprint(jobs_bp)

    from .users import bp as users_bp
    app.register_blueprint(users_bp)

    from .reviews import bp as reviews_bp
    app.register_blueprint(reviews_bp)

    from .notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp)

    return app