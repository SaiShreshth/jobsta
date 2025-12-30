import sys
sys.path.insert(0, r'c:\Users\saish\Documents\projs\jobsta')
from app import create_app
from base64 import b64encode

app = create_app()
app.config['TESTING'] = True
with app.test_client() as c:
    auth = b64encode(b'root:msrit@123').decode()
    r = c.get('/admin/login', headers={'Authorization': 'Basic '+auth})
    print('/admin/login status', r.status_code)
    print('set-cookie header:', r.headers.get('Set-Cookie'))
    # now follow the redirect using the cookie manually
    if r.status_code in (301,302,303,307,308):
        loc = r.headers.get('Location')
        # copy cookie from header into client's cookie jar if present
        sc = r.headers.get('Set-Cookie')
        print('set-cookie raw:', sc)
    print('admin_token cookie in client before follow:', c.get_cookie('admin_token'))
    r2 = c.get('/admin', follow_redirects=True)
    print('/admin status after login follow', r2.status_code)
    print('admin_token cookie in client after follow:', c.get_cookie('admin_token'))
    # try accessing admin index with cookie set in the client automatically
    r2 = c.get('/admin', follow_redirects=True)
    print('/admin status after login follow', r2.status_code)
    # expire token test
    # (manual) -- not implemented
