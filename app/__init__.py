import os
from flask import Flask, send_from_directory
from .config import Config
from .extensions import db, migrate, bcrypt
from dotenv import load_dotenv
from whitenoise import WhiteNoise

# Load environment variables from project `.env` if present
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(basedir, '.env'))

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
    
    # Add WhiteNoise middleware for serving static files in production
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=static_folder, prefix='static/')
    
    # Explicit route for CSS files as fallback
    @app.route('/static/css/<path:filename>')
    def serve_css(filename):
        css_dir = os.path.join(static_folder, 'css')
        return send_from_directory(css_dir, filename, mimetype='text/css')
    
    # Normalize DB URI for psycopg if needed and log active DB
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if uri.startswith('postgresql://') and '+psycopg' not in uri:
        uri = uri.replace('postgresql://', 'postgresql+psycopg://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = uri
    print(f"[startup] SQLALCHEMY_DATABASE_URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")

    db.init_app(app)
    migrate.init_app(app, db)
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