#!/usr/bin/env python3
"""Simple test script to exercise the /admin route with Flask test_client.

Usage: python scripts/test_admin.py
"""
from app import create_app
import base64

app = create_app()

def run():
    with app.test_client() as c:
        def check(headers=None, label=None):
            r = c.get('/admin', headers=headers or {})
            print(f"{label or '/admin'} -> {r.status_code}")
            if r.status_code == 200:
                text = r.get_data(as_text=True)
                print(f"  body length: {len(text)}")
                print("  snippet:", text[:200].replace('\n',' ') )

        check(label='/admin (no auth)')
        bad = {'Authorization': 'Basic ' + base64.b64encode(b'root:wrong').decode()}
        check(bad, label='/admin (bad auth)')
        good = {'Authorization': 'Basic ' + base64.b64encode(b'root:msrit@123').decode()}
        check(good, label='/admin (good auth)')

if __name__ == '__main__':
    run()
