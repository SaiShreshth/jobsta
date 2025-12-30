import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app

app = create_app()
client = app.test_client()
paths = ['/', '/login', '/register', '/dashboard', '/jobs', '/settings', '/applications', '/notifications', '/admin', '/job/1']
results = {}
for p in paths:
    try:
        r = client.get(p, follow_redirects=False)
        loc = r.headers.get('Location')
        results[p] = (r.status_code, loc)
    except Exception as e:
        results[p] = ('EXCEPTION', str(e))

for p, v in results.items():
    print(p, '->', v)
