import sys
sys.path.insert(0, r'c:\Users\saish\Documents\projs\jobsta')
from app import create_app
from app.models import User, DeviceToken
from app.extensions import bcrypt, db
from datetime import datetime, timedelta
import secrets
app=create_app()
with app.app_context():
    u=User.query.filter_by(email='ui-test@msrit.edu').first()
    token_plain = secrets.token_urlsafe(40)
    token_hash = bcrypt.generate_password_hash(token_plain).decode('utf-8')
    dt = DeviceToken(user_id=u.id, token_hash=token_hash, expires_at=datetime.utcnow()+timedelta(days=7))
    db.session.add(dt)
    db.session.commit()

    from app.utils.auth import get_current_user
    # simulate request with cookie
    with app.test_request_context('/', headers={'Cookie': f'device_token={token_plain}'}):
        cu = get_current_user()
        print('get_current_user returned:', cu and cu.email)
