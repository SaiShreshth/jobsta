"""Email helpers using Resend API."""
from flask import current_app


def send_email(to_email: str, subject: str, body: str, html: str | None = None) -> bool:
    """Send email using Resend API with detailed logging."""
    from app.utils.mail_logger import send_email_with_detailed_logging
    
    success, error = send_email_with_detailed_logging(
        subject=subject,
        recipient=to_email,
        body=body,
        html=html
    )
    
    return success
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
