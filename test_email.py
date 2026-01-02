#!/usr/bin/env python3
"""
Comprehensive test script for Resend email functionality
Tests all email types: verification, temp password, and application confirmation
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
    """Initialize Flask app context"""
    from app import create_app
    app = create_app()
    return app

def test_verification_email(app):
    """Test account verification email"""
    print("\n" + "="*60)
    print("TEST 1: Account Verification Email")
    print("="*60)
    
    with app.app_context():
        from app.utils.email import send_verification_email
        
        test_email = "test.user@msrit.edu"
        verification_link = "https://jobsta.com/auth/verify/abc123token456"
        
        print(f"📧 Sending verification email to: {test_email}")
        print(f"🔗 Verification link: {verification_link}")
        
        result = send_verification_email(test_email, verification_link)
        
        if result:
            print("✅ Verification email sent successfully!")
            return True
        else:
            print("❌ Failed to send verification email")
            return False

def test_temp_password_email(app):
    """Test temporary password email"""
    print("\n" + "="*60)
    print("TEST 2: Temporary Password Email")
    print("="*60)
    
    with app.app_context():
        from app.utils.email import send_temp_password_email
        
        test_email = "test.user@msrit.edu"
        temp_password = "TempPass123!@#"
        
        print(f"📧 Sending temp password email to: {test_email}")
        print(f"🔐 Temporary password: {temp_password}")
        
        result = send_temp_password_email(test_email, temp_password)
        
        if result:
            print("✅ Temp password email sent successfully!")
            return True
        else:
            print("❌ Failed to send temp password email")
            return False

def test_application_email(app):
    """Test job application confirmation email"""
    print("\n" + "="*60)
    print("TEST 3: Job Application Confirmation Email")
    print("="*60)
    
    with app.app_context():
        from app.utils.email import send_application_confirmation_email
        
        test_email = "test.user@msrit.edu"
        job_title = "Software Engineer Intern"
        company = "TechCorp India"
        apply_url = "https://careers.techcorp.com/apply/12345"
        
        print(f"📧 Sending application confirmation email to: {test_email}")
        print(f"💼 Job: {job_title} at {company}")
        print(f"🔗 Application URL: {apply_url}")
        
        result = send_application_confirmation_email(test_email, job_title, company, apply_url)
        
        if result:
            print("✅ Application confirmation email sent successfully!")
            return True
        else:
            print("❌ Failed to send application email")
            return False

def test_with_suppression(app):
    """Test email sending with MAIL_SUPPRESS_SEND enabled"""
    print("\n" + "="*60)
    print("TEST 4: Email Suppression (Dev Mode)")
    print("="*60)
    
    with app.app_context():
        from app.utils.email import send_verification_email
        
        # Enable suppression
        app.config['MAIL_SUPPRESS_SEND'] = True
        
        test_email = "dev@test.local"
        verification_link = "https://jobsta.com/auth/verify/test123"
        
        print(f"📧 Testing with MAIL_SUPPRESS_SEND=True")
        print(f"   Email should NOT be sent, only logged")
        
        result = send_verification_email(test_email, verification_link)
        
        if result:
            print("✅ Suppression mode working correctly!")
            return True
        else:
            print("❌ Suppression mode failed")
            return False

def test_config(app):
    """Display current email configuration"""
    print("\n" + "="*60)
    print("EMAIL CONFIGURATION")
    print("="*60)
    
    with app.app_context():
        api_key = app.config.get('RESEND_API_KEY')
        if api_key:
            print(f"RESEND_API_KEY: {api_key[:20]}...")
        else:
            print(f"RESEND_API_KEY: NOT SET ⚠️")
        print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print(f"MAIL_SENDER_NAME: {app.config.get('MAIL_SENDER_NAME')}")
        print(f"MAIL_SUPPRESS_SEND: {app.config.get('MAIL_SUPPRESS_SEND')}")

def main():
    """Run all email tests"""
    print("\n" + "🚀 "*30)
    print("RESEND EMAIL FUNCTIONALITY TEST SUITE")
    print("🚀 "*30)
    print(f"\nTest Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup app
    try:
        app = setup_app()
        print("✅ Flask app initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Flask app: {e}")
        sys.exit(1)
    
    # Display config
    test_config(app)
    
    # Run tests
    results = []
    
    try:
        results.append(("Verification Email", test_verification_email(app)))
    except Exception as e:
        print(f"❌ Error in verification email test: {e}")
        results.append(("Verification Email", False))
    
    try:
        results.append(("Temp Password Email", test_temp_password_email(app)))
    except Exception as e:
        print(f"❌ Error in temp password email test: {e}")
        results.append(("Temp Password Email", False))
    
    try:
        results.append(("Application Email", test_application_email(app)))
    except Exception as e:
        print(f"❌ Error in application email test: {e}")
        results.append(("Application Email", False))
    
    try:
        results.append(("Email Suppression", test_with_suppression(app)))
    except Exception as e:
        print(f"❌ Error in suppression test: {e}")
        results.append(("Email Suppression", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Email functionality is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check configuration and logs above.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
