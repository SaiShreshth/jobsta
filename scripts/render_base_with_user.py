import sys
sys.path.insert(0, r'c:\Users\saish\Documents\projs\jobsta')
from app import create_app
from app.models import User
from flask import render_template
app=create_app()
with app.app_context():
    u=User.query.filter_by(email='ui-test@msrit.edu').first()
    with app.test_request_context('/'):
        html = render_template('base.html', current_user=u)
        s=html.find('<nav')
        e=html.find('</nav>')
        print('nav present?', s!=-1)
        if s!=-1 and e!=-1:
            nav = html[s:e+6]
            print(nav)
        else:
            print('nav not found')