from flask import request
from app.models import User, DeviceToken
from app.extensions import bcrypt
from datetime import datetime

def get_current_user():
    token = request.cookies.get('device_token')
    if not token:
        return None
    token_hash = bcrypt.generate_password_hash(token).decode('utf-8')
    device_token = DeviceToken.query.filter_by(token_hash=token_hash).first()
    if not device_token or device_token.expires_at < datetime.utcnow():
        return None
    user = User.query.get(device_token.user_id)
    return user