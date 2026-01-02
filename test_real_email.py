#!/usr/bin/env python3
"""Send a real SMTP email (opt-in) using Flask-Mail."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).parent
load_dotenv(basedir / '.env')

# Force local database for safety during tests
os.environ['DATABASE_URL'] = os.environ.get('TEST_DATABASE_URL', 'sqlite:///test.db')

# Opt-in flag to actually send email; default is suppressed for safety
SEND_REAL_EMAILS = os.environ.get('SEND_REAL_EMAILS', 'false').lower() in ('1', 'true', 'yes')
os.environ['MAIL_SUPPRESS_SEND'] = 'False' if SEND_REAL_EMAILS else 'True'

sys.path.insert(0, str(basedir))

from app import create_app

app = create_app()
app.config['MAIL_SUPPRESS_SEND'] = not SEND_REAL_EMAILS

with app.app_context():
    from app.utils.email import send_email

    test_recipient = os.environ.get('TEST_RECIPIENT_EMAIL', 'saishreshth123@gmail.com')

    sender = app.config.get('MAIL_DEFAULT_SENDER')
    server = app.config.get('MAIL_SERVER')
    print(f"🚀 Sending test email to: {test_recipient}")
    print(f"📧 From: {sender}")
    print(f"🛰️ SMTP server: {server}")
    print(f"🧪 MAIL_SUPPRESS_SEND={app.config['MAIL_SUPPRESS_SEND']}")

    result = send_email(
        to_email=test_recipient,
        subject="🎉 Jobsta Email Test - SMTP",
        body="Hello! This is a test email from your Jobsta application.\n\nIf you're reading this, SMTP is working!\n\nBest regards,\nJobsta Team",
        html="""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4CAF50;">🎉 Success!</h2>
            <p>Hello!</p>
            <p>This is a test email from your <strong>Jobsta</strong> application.</p>
            <p>If you're reading this, SMTP is working!</p>
            <p>Best regards,<br><strong>Jobsta Team</strong></p>
        </body>
        </html>
        """
    )

    if result:
        status = "SENT" if SEND_REAL_EMAILS else "SUPPRESSED"
        print(f"\n✅ SUCCESS! Email {status} (check inbox if not suppressed)")
    else:
        print("\n❌ FAILED! Email was not sent. Check logs above.")
