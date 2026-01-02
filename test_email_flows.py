#!/usr/bin/env python3
"""
Email Functionality Test - Development Mode (Suppression Enabled)
Tests all email functions with MAIL_SUPPRESS_SEND enabled
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
basedir = Path(__file__).parent
load_dotenv(basedir / '.env')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_app():
    """Initialize Flask app context with suppression enabled"""
    from app import create_app
    app = create_app()
    # Enable suppression for testing
    app.config['MAIL_SUPPRESS_SEND'] = True
    return app

def test_registration_flow(app):
    """Test complete registration flow with emails"""
    print("\n" + "="*70)
    print("REGISTRATION FLOW TEST (Dev Mode - Emails Suppressed)")
    print("="*70)
    
    with app.app_context():
        from app.extensions import db
        from app.models import User, Token
        from app.utils.email import send_verification_email
        import secrets
        from datetime import datetime, timedelta
        
        # Simulate registration
        test_email = "john.doe@msrit.edu"
        test_name = "John Doe"
        
        print(f"\n[STEP 1] User Registration")
        print(f"  Name: {test_name}")
        print(f"  Email: {test_email}")
        
        # Create user
        user = User(email=test_email, name=test_name, is_verified=False)
        db.session.add(user)
        db.session.commit()
        print(f"  ✅ User created in database")
        
        # Create verification token
        print(f"\n[STEP 2] Generate Verification Token")
        token_str = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1)
        token = Token(email=test_email, token=token_str, expires_at=expires, used=False)
        db.session.add(token)
        db.session.commit()
        print(f"  ✅ Verification token created: {token_str[:20]}...")
        
        # Send verification email
        print(f"\n[STEP 3] Send Verification Email")
        verification_url = f"https://jobsta.com/auth/verify/{token_str}"
        result = send_verification_email(test_email, verification_url)
        if result:
            print(f"  ✅ Verification email would be sent")
        else:
            print(f"  ❌ Failed to send verification email")
        
        # Cleanup
        Token.query.filter_by(email=test_email).delete()
        User.query.filter_by(email=test_email).delete()
        db.session.commit()
        print(f"\n  ✅ Test data cleaned up")
        
        return result

def test_password_reset_flow(app):
    """Test password reset with email notification"""
    print("\n" + "="*70)
    print("PASSWORD RESET FLOW TEST (Dev Mode - Emails Suppressed)")
    print("="*70)
    
    with app.app_context():
        from app.extensions import db, bcrypt
        from app.models import User
        from app.utils.email import send_temp_password_email
        
        test_email = "jane.smith@msrit.edu"
        test_name = "Jane Smith"
        
        print(f"\n[STEP 1] Create User Account")
        user = User(email=test_email, name=test_name, is_verified=False)
        db.session.add(user)
        db.session.commit()
        print(f"  ✅ User created: {test_name} ({test_email})")
        
        print(f"\n[STEP 2] Generate Temporary Password")
        import string
        import secrets
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        print(f"  Temporary Password: {temp_password}")
        
        print(f"\n[STEP 3] Hash and Store Password")
        user.password_hash = bcrypt.generate_password_hash(temp_password).decode('utf-8')
        user.is_verified = True
        db.session.commit()
        print(f"  ✅ Password hashed and stored")
        
        print(f"\n[STEP 4] Send Temp Password Email")
        result = send_temp_password_email(test_email, temp_password)
        if result:
            print(f"  ✅ Temp password email would be sent")
        else:
            print(f"  ❌ Failed to send temp password email")
        
        # Cleanup
        User.query.filter_by(email=test_email).delete()
        db.session.commit()
        print(f"\n  ✅ Test data cleaned up")
        
        return result

def test_application_flow(app):
    """Test job application with confirmation email"""
    print("\n" + "="*70)
    print("JOB APPLICATION FLOW TEST (Dev Mode - Emails Suppressed)")
    print("="*70)
    
    with app.app_context():
        from app.extensions import db
        from app.models import User, Job, Application
        from app.utils.email import send_application_confirmation_email
        
        test_email = "applicant@msrit.edu"
        test_user_name = "Test Applicant"
        admin_email = "admin@msrit.edu"
        
        print(f"\n[STEP 1] Create Admin User (Job Poster)")
        admin = User(email=admin_email, name="Admin User", is_verified=True, role='admin')
        db.session.add(admin)
        db.session.flush()
        
        print(f"  ✅ Admin user created")
        
        print(f"[STEP 2] Create Test User & Job")
        user = User(email=test_email, name=test_user_name, is_verified=True)
        db.session.add(user)
        db.session.flush()
        
        job = Job(
            title="Senior Software Engineer",
            company="TechCorp Solutions",
            description="We are hiring talented engineers",
            apply_url="https://techcorp.careers.com/apply/12345",
            posted_by=admin.id  # Add the required posted_by field
        )
        db.session.add(job)
        db.session.commit()
        print(f"  ✅ User created: {test_user_name}")
        print(f"  ✅ Job created: {job.title} at {job.company}")
        
        print(f"\n[STEP 2] Submit Application")
        application = Application(user_id=user.id, job_id=job.id)
        db.session.add(application)
        db.session.commit()
        print(f"  ✅ Application submitted")
        
        print(f"\n[STEP 3] Send Confirmation Email")
        result = send_application_confirmation_email(
            test_email,
            job.title,
            job.company,
            job.apply_url
        )
        if result:
            print(f"  ✅ Confirmation email would be sent")
        else:
            print(f"  ❌ Failed to send confirmation email")
        
        # Cleanup
        Application.query.filter_by(user_id=user.id).delete()
        Job.query.filter_by(id=job.id).delete()
        User.query.filter_by(email=test_email).delete()
        User.query.filter_by(email=admin_email).delete()
        db.session.commit()
        print(f"\n  ✅ Test data cleaned up")
        
        return result

def test_config(app):
    """Display current configuration"""
    print("\n" + "="*70)
    print("EMAIL CONFIGURATION")
    print("="*70)
    
    with app.app_context():
        api_key = app.config.get('RESEND_API_KEY')
        suppress = app.config.get('MAIL_SUPPRESS_SEND')
        
        print(f"RESEND_API_KEY: {'✅ Configured' if api_key else '❌ NOT SET'}")
        print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print(f"MAIL_SENDER_NAME: {app.config.get('MAIL_SENDER_NAME')}")
        print(f"MAIL_SUPPRESS_SEND: {suppress} {'(Dev mode - emails not actually sent)' if suppress else '(Production - emails sent via Resend)'}")

def main():
    """Run all email flow tests"""
    print("\n" + "🚀 "*35)
    print("JOBSTA EMAIL FUNCTIONALITY TEST SUITE")
    print("Development Mode (Suppression Enabled)")
    print("🚀 "*35)
    print(f"\nTest Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup app
    try:
        app = setup_app()
        print("✅ Flask app initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Flask app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Display config
    test_config(app)
    
    # Run tests
    results = []
    
    try:
        results.append(("Registration Flow (Verification Email)", test_registration_flow(app)))
    except Exception as e:
        print(f"❌ Error in registration flow: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Registration Flow", False))
    
    try:
        results.append(("Password Reset Flow (Temp Password Email)", test_password_reset_flow(app)))
    except Exception as e:
        print(f"❌ Error in password reset flow: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Password Reset Flow", False))
    
    try:
        results.append(("Job Application Flow (Confirmation Email)", test_application_flow(app)))
    except Exception as e:
        print(f"❌ Error in application flow: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Job Application Flow", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All email flows tested successfully!")
        print("\n📝 NOTES:")
        print("  • Emails are currently suppressed for development")
        print("  • To send real emails, set MAIL_SUPPRESS_SEND=False")
        print("  • Domain verification is required on Resend")
        print("  • Update MAIL_DEFAULT_SENDER to a verified domain")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
