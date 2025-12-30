from flask import request
from app.models import User, DeviceToken
from app.extensions import bcrypt
from datetime import datetime

def get_current_user():
    token = request.cookies.get('device_token')
    if not token:
        return None
    # Find any non-expired device tokens for which the hashed value matches
    now = datetime.utcnow()
    candidates = DeviceToken.query.filter(DeviceToken.expires_at >= now).all()
    for dt in candidates:
        try:
            if bcrypt.check_password_hash(dt.token_hash, token):
                return User.query.get(dt.user_id)
        except Exception:
            # If hashing/check fails, continue to next
            continue
    return None