import logging
import os
import sys
import time
import uuid
from flask import Flask, send_from_directory
from .config import Config
from .extensions import db, migrate, bcrypt, mail
from dotenv import load_dotenv
from whitenoise import WhiteNoise

# Load environment variables from project `.env` if present
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(basedir, '.env'))


class RequestContextFilter(logging.Filter):
    """Inject request-aware fields into log records."""

    def filter(self, record):
        try:
            from flask import g, request
            record.request_id = getattr(g, 'request_id', '-')
            record.method = getattr(request, 'method', '-')
            record.path = getattr(request, 'path', '-')
            record.remote_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
        except Exception:
            record.request_id = '-'
            record.method = '-'
            record.path = '-'
            record.remote_addr = '-'
        return True


def configure_logging(app: Flask) -> None:
    """Configure application logging with request context fields."""

    log_level_name = app.config.get('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] req=%(request_id)s %(method)s %(path)s %(message)s'
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())

    # Reset default handlers to avoid duplicate logs
    app.logger.handlers.clear()
    app.logger.propagate = False
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    # Tone down noisy libraries
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.INFO)

def create_app(config_class=Config):
    # Calculate static folder - check multiple possible locations
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try different possible locations for static folder
    possible_static_paths = [
        os.path.join(app_dir, '..', 'static'),  # Root level (local dev)
        os.path.join(app_dir, 'static'),         # Inside app folder
        'static',                                 # Relative to working directory
    ]
    
    static_folder = None
    for path in possible_static_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            static_folder = abs_path
            print(f"[startup] Found static folder at: {static_folder}")
            break
    
    if not static_folder:
        print(f"[startup] WARNING: Static folder not found! Tried: {possible_static_paths}")
        static_folder = os.path.join(app_dir, '..', 'static')  # Fallback
    
    app = Flask(
        __name__,
        static_folder=static_folder,
        static_url_path='/static'
    )
    # ... rest of your code
    # app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.config.from_object(config_class)

    configure_logging(app)
    
    # Add WhiteNoise middleware for serving static files in production
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=static_folder, prefix='static/')
    
    # Explicit route for CSS files as fallback
    @app.route('/static/css/<path:filename>')
    def serve_css(filename):
        css_dir = os.path.join(static_folder, 'css')
        return send_from_directory(css_dir, filename, mimetype='text/css')

    @app.before_request
    def _log_request_start():
        from flask import request, g
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        g.start_time = time.perf_counter()
        app.logger.info(
            "request.start remote=%s agent=%s",
            request.headers.get('X-Forwarded-For', request.remote_addr),
            request.user_agent.string,
        )

    @app.after_request
    def _log_request_end(response):
        from flask import request, g
        duration_ms = None
        try:
            duration_ms = (time.perf_counter() - getattr(g, 'start_time', time.perf_counter())) * 1000
        except Exception:
            duration_ms = None

        # Attach request id to the response for traceability
        if getattr(g, 'request_id', None):
            response.headers['X-Request-ID'] = g.request_id

        # Best-effort user id
        user_id = None
        try:
            from .utils.auth import get_current_user
            user = get_current_user()
            user_id = getattr(user, 'id', None)
        except Exception:
            user_id = None

        app.logger.info(
            "request.end status=%s duration_ms=%s user_id=%s", response.status_code, f"{duration_ms:.1f}" if duration_ms else 'n/a', user_id
        )
        return response
    
    # Normalize DB URI for psycopg if needed and log active DB
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if uri.startswith('postgresql://') and '+psycopg' not in uri:
        uri = uri.replace('postgresql://', 'postgresql+psycopg://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.logger.info("startup.database uri=%s", app.config.get('SQLALCHEMY_DATABASE_URI'))

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)

    from . import models

    # Ensure DB tables exist (create missing tables during development/runtime)
    with app.app_context():
        try:
            app.logger.info('startup.db_create_all begin')
            db.create_all()
            from sqlalchemy import inspect
            insp = inspect(db.engine)
            app.logger.info('startup.db_tables tables=%s', insp.get_table_names())
        except Exception as e:
            app.logger.exception("startup.db_create_all failed: %s", e)

    # Register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

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

    # Admin blueprint serves admin routes under /admin

    @app.context_processor
    def inject_current_user():
        from .utils.auth import get_current_user
        # detect mobile user-agent roughly and provide flags for templates
        from flask import request
        cu = get_current_user()
        ua = request.user_agent.string or ''
        is_mobile = False
        try:
            key = ua.lower()
            if 'mobile' in key or 'iphone' in key or 'android' in key or 'ipad' in key:
                is_mobile = True
        except Exception:
            is_mobile = False
        is_admin = bool(cu and getattr(cu, 'role', None) == 'admin')
        return dict(current_user=cu, is_mobile=is_mobile, is_admin=is_admin)

    return app