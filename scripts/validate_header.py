#!/usr/bin/env python3
"""Validate header structure for Step 1: ensure compact 3-zone header, single user menu, theme toggle in dropdown."""
from app import create_app
from app.extensions import db, bcrypt
from flask import render_template
from app.models import User

app = create_app()

def ensure_user(email='ui-test@msrit.edu', name='UITest', password='TestPass123', role=None):
    with app.app_context():
        u = User.query.filter_by(email=email).first()
        if not u:
            u = User(email=email, name=name, is_verified=True)
            if role:
                u.role = role
            u.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.add(u)
            db.session.commit()
            print('Created user', email)
        else:
            if role and u.role != role:
                u.role = role
                db.session.commit()
                print('Updated user role for', email, '->', role)
        return u


def run_checks(user_email='ui-test@msrit.edu', password='TestPass123', role=None):
    ensure_user(email=user_email, role=role)
    with app.app_context():
        # Ensure device token is present so get_current_user() resolves
        from app.models import DeviceToken
        import secrets
        from datetime import datetime, timedelta
        from app.extensions import bcrypt
        token_plain = secrets.token_urlsafe(40)
        token_hash = bcrypt.generate_password_hash(token_plain).decode('utf-8')
        u = User.query.filter_by(email=user_email).first()
        dt = DeviceToken(user_id=u.id, token_hash=token_hash, expires_at=datetime.utcnow()+timedelta(days=7))
        db.session.add(dt)
        db.session.commit()

    # Render base template with current_user injected to validate header structure
    with app.test_request_context('/'):
        # re-fetch user to ensure bound instance in this context
        current = User.query.filter_by(email=user_email).first()
        html = render_template('base.html', current_user=current)
        nav_html = html.split('<nav',1)[1].split('</nav>',1)[0] if '<nav' in html else html
        avatars = nav_html.count(' avatar')
        theme_toggles = nav_html.count('theme-toggle')
        hello_in_header = 'Hello,' in nav_html
        print('avatars:', avatars, 'theme_toggles:', theme_toggles, 'hello_in_header:', hello_in_header)
        admin_badge = 'Admin</span>' in nav_html
        print('admin_badge_present:', admin_badge)
        ok = True
        if avatars != 1:
            print('FAIL: Expected 1 avatar element in header')
            ok = False
        if theme_toggles < 1:
            print('FAIL: Expected at least 1 theme toggle (in dropdown)')
            ok = False
        if hello_in_header:
            print('FAIL: Greeting text appeared in header')
            ok = False
        if role == 'admin' and not admin_badge:
            print('FAIL: Admin badge missing for admin user')
            ok = False
        print('OK' if ok else 'NOT OK')
        return 0 if ok else 2

if __name__ == '__main__':
    import sys
    role = None
    if len(sys.argv) > 1 and sys.argv[1] == 'admin':
        role = 'admin'
    code = run_checks(role=role)
    sys.exit(code)
