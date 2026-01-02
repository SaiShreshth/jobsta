"""Email sending utilities using Resend API"""
from flask import current_app
import resend


def send_email(to_email: str, subject: str, body: str, html: str = None) -> bool:
    """
    Send an email using Resend API.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text email body
        html: Optional HTML email body
        
    Returns:
        True if email was sent successfully or suppressed, False on error
    """
    # Check if email sending is suppressed (for development)
    if current_app.config.get('MAIL_SUPPRESS_SEND'):
        print(f"[mail suppressed] To: {to_email}, Subject: {subject}")
        print(f"Body: {body}")
        return True
    
    # Get Resend API key
    api_key = current_app.config.get('RESEND_API_KEY')
    if not api_key:
        print('[email error] RESEND_API_KEY not configured')
        return False
    
    try:
        # Set API key for resend
        resend.api_key = api_key
        
        # Build email data
        sender_addr = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@jobsta.com')
        sender_name = current_app.config.get('MAIL_SENDER_NAME', 'jobsta')
        
        email_data = {
            'from': f"{sender_name} <{sender_addr}>",
            'to': to_email,
            'subject': subject,
            'text': body,
        }
        
        # Add HTML if provided
        if html:
            email_data['html'] = html
        
        # Send the email
        response = resend.Emails.send(email_data)
        
        print(f"[mail sent] Email to {to_email}, Subject: {subject}, Response: {response}")
        return True
        
    except Exception as e:
        print(f'[email error] Failed to send email to {to_email}: {e}')
        return False


def send_verification_email(email: str, verification_link: str) -> bool:
    """Send account verification email"""
    subject = 'Verify your Jobsta account'
    body = f'Click here to verify your account: {verification_link}'
    
    html = f"""
    <html>
        <body>
            <h2>Verify Your Jobsta Account</h2>
            <p>Click the link below to verify your account:</p>
            <p><a href="{verification_link}">Verify Account</a></p>
            <p>Or copy and paste this link: {verification_link}</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body, html)


def send_temp_password_email(email: str, temp_password: str) -> bool:
    """Send temporary password email"""
    subject = 'Welcome to Jobsta - Your Temporary Password'
    body = f"""Your account has been verified. Your temporary password is: {temp_password}

Please log in and change your password as soon as possible."""
    
    html = f"""
    <html>
        <body>
            <h2>Welcome to Jobsta</h2>
            <p>Your account has been verified.</p>
            <p><strong>Your temporary password is:</strong> <code>{temp_password}</code></p>
            <p>Please log in and change your password as soon as possible.</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body, html)


def send_application_confirmation_email(email: str, job_title: str, company: str, apply_url: str) -> bool:
    """Send application confirmation email"""
    subject = 'Application Received'
    body = f'You have successfully applied for {job_title} at {company}. Apply at: {apply_url}'
    
    html = f"""
    <html>
        <body>
            <h2>Application Received</h2>
            <p>You have successfully applied for <strong>{job_title}</strong> at <strong>{company}</strong>.</p>
            <p><a href="{apply_url}">View Application</a></p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body, html)
