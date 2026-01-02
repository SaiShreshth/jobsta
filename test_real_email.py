#!/usr/bin/env python3
"""Quick test to send a real email via Resend"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).parent
load_dotenv(basedir / '.env')
sys.path.insert(0, str(basedir))

from app import create_app

app = create_app()
app.config['MAIL_SUPPRESS_SEND'] = False  # Send real emails!

with app.app_context():
    from app.utils.email import send_email
    
    # Replace with YOUR email to test
    test_recipient = "saishreshth123@gmail.com"  # Your actual email
    
    print(f"🚀 Sending test email to: {test_recipient}")
    print(f"📧 From: {app.config['MAIL_DEFAULT_SENDER']}")
    print(f"🔑 Using API Key: {app.config['RESEND_API_KEY'][:20]}...\n")
    
    result = send_email(
        to_email=test_recipient,
        subject="🎉 Jobsta Email Test - Resend Integration Working!",
        body="Hello! This is a test email from your Jobsta application.\n\nIf you're reading this, your Resend integration is working perfectly!\n\n✅ SMTP migration successful\n✅ Emails sent via Resend API\n✅ Works on both local and Render\n\nBest regards,\nJobsta Team",
        html="""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4CAF50;">🎉 Success!</h2>
            <p>Hello!</p>
            <p>This is a test email from your <strong>Jobsta</strong> application.</p>
            <p>If you're reading this, your Resend integration is working perfectly!</p>
            <ul>
                <li>✅ SMTP migration successful</li>
                <li>✅ Emails sent via Resend API</li>
                <li>✅ Works on both local and Render</li>
            </ul>
            <p>Best regards,<br><strong>Jobsta Team</strong></p>
        </body>
        </html>
        """
    )
    
    if result:
        print("\n✅ SUCCESS! Email sent successfully!")
        print(f"📬 Check your inbox: {test_recipient}")
    else:
        print("\n❌ FAILED! Email was not sent. Check logs above.")
