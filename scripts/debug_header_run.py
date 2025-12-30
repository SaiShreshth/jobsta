import sys
sys.path.insert(0, r'c:\Users\saish\Documents\projs\jobsta')
from app import create_app
from app.models import User
from app.extensions import bcrypt, db
app=create_app()
with app.app_context():
    u=User.query.filter_by(email='ui-test@msrit.edu').first()
    if u:
        print('User exists:', bool(u), 'verified=', getattr(u,'is_verified',None))
        print('password_hash:', bool(u.password_hash))
        from app.extensions import bcrypt
        print('bcrypt verify:', bcrypt.check_password_hash(u.password_hash, 'TestPass123'))
    else:
        print('no user')
with app.test_client() as c:
    r = c.post('/login', data={'email':'ui-test@msrit.edu','password':'TestPass123'}, follow_redirects=True)
    print('/login ->', r.status_code)
    print('\n/login response snippet:\n', r.get_data(as_text=True)[:400])
    r2 = c.get('/dashboard', follow_redirects=True)
    print('/dashboard (follow) ->', r2.status_code, 'path:', r2.request.path)
    html = r2.get_data(as_text=True)
    print('len html', len(html))
    start = html.find('<nav')
    end = html.find('</nav>')
    if start!=-1 and end!=-1:
        nav = html[start:end+6]
        print('NAV SNIPPET:')
        print(nav)
    else:
        print('No nav found in page')
