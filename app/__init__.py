import os
from flask import Flask
from .config import Config
from .extensions import db, migrate, mail, bcrypt
from dotenv import load_dotenv

# Load environment variables from project `.env` if present
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(basedir, '.env'))

def create_app(config_class=Config):
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.config.from_object(config_class)
    # Normalize DB URI for psycopg if needed and log active DB
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if uri.startswith('postgresql://') and '+psycopg' not in uri:
        uri = uri.replace('postgresql://', 'postgresql+psycopg://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = uri
    print(f"[startup] SQLALCHEMY_DATABASE_URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)

    from . import models

    # Ensure DB tables exist (create missing tables during development/runtime)
    with app.app_context():
        try:
            print('[startup] Ensuring all tables exist (db.create_all)')
            db.create_all()
            from sqlalchemy import inspect
            insp = inspect(db.engine)
            print('[startup] Current tables:', insp.get_table_names())
        except Exception as e:
            print(f"[startup] DB create_all failed: {e}")

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

    @app.route('/')
    def index():
        from flask import redirect, url_for
        from .utils.auth import get_current_user
        if get_current_user():
            return redirect(url_for('users.dashboard'))
        else:
            return redirect(url_for('auth.login'))

    @app.route('/admin')
    def admin():
        from flask import request, make_response
        auth = request.authorization
        if not auth or auth.username != 'root' or auth.password != 'msrit@123':
            response = make_response('Unauthorized', 401)
            response.headers['WWW-Authenticate'] = 'Basic realm="Admin"'
            return response
        return render_template('admin_dashboard.html')

    @app.context_processor
    def inject_current_user():
        from .utils.auth import get_current_user
        return dict(current_user=get_current_user())

    return app