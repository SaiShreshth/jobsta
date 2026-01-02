import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Only apply PostgreSQL-specific engine options if using PostgreSQL (checked at init time)
    # Default to empty dict; will be set in create_app() if needed
    SQLALCHEMY_ENGINE_OPTIONS = {}
    # Logging
    LOG_LEVEL = (os.environ.get('LOG_LEVEL') or 'INFO').upper()
    
    # Resend API configuration (replaces SMTP)
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'onboarding@resend.dev'
    MAIL_SENDER_NAME = os.environ.get('MAIL_SENDER_NAME') or 'Jobsta'
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'False').lower() in ('1', 'true', 'yes')
    
    WTF_CSRF_ENABLED = True
    # Use secure cookies (only set to True in production with HTTPS)
    COOKIE_SECURE = os.environ.get('COOKIE_SECURE', 'False').lower() in ('1', 'true', 'yes')
    # PREFERRED_URL_SCHEME used by Flask for URL generation
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'https'