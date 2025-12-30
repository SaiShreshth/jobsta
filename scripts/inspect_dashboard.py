import sys
sys.path.insert(0, r'c:\Users\saish\Documents\projs\jobsta')
from app import create_app
from app.models import User, DeviceToken
from app.extensions import bcrypt
from datetime import datetime, timedelta
import secrets
app=create_app()
with app.app_context():
    u=User.query.filter_by(email='ui-test@msrit.edu').first()
    token_plain = secrets.token_urlsafe(40)
    token_hash = bcrypt.generate_password_hash(token_plain).decode('utf-8')
    dt = DeviceToken(user_id=u.id, token_hash=token_hash, expires_at=datetime.utcnow()+timedelta(days=7))
    from app.extensions import db
    db.session.add(dt)
    db.session.commit()
with app.test_client() as c:
    c.set_cookie('localhost','device_token', token_plain)
    r = c.get('/dashboard')
    print('/dashboard status', r.status_code)
    html = r.get_data(as_text=True)
    s = html.find('<nav')
    e = html.find('</nav>')
    print('nav present?', s!=-1)
    if s!=-1 and e!=-1:
        print(html[s:e+6])
    else:
        print('nav not found')