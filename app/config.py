import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('EMAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('EMAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@jobsta.com'
    # In development you may set MAIL_SUPPRESS_SEND=True to avoid sending
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'False').lower() in ('1', 'true', 'yes')
    # Display name used in outgoing emails
    MAIL_SENDER_NAME = os.environ.get('MAIL_SENDER_NAME') or 'jobsta'
    WTF_CSRF_ENABLED = True
    # Use secure cookies (only set to True in production with HTTPS)
    COOKIE_SECURE = os.environ.get('COOKIE_SECURE', 'False').lower() in ('1', 'true', 'yes')
    # Server name for URL generation
    SERVER_NAME = os.environ.get('SERVER_NAME') or 'knox-swainish-wonderingly.ngrok-free.dev'
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'https'