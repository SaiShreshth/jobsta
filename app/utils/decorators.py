from functools import wraps
from flask import redirect, url_for
from .auth import get_current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('auth.login', _external=True))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != 'admin':
            return redirect(url_for('auth.login', _external=True))
        return f(*args, **kwargs)
    return decorated_function