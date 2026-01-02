"""Email helpers using Flask-Mail."""
from flask import current_app
from flask_mail import Message

from app.extensions import mail


def send_email(to_email: str, subject: str, body: str, html: str | None = None) -> bool:
    """Send email with Flask-Mail, honoring MAIL_SUPPRESS_SEND."""
    logger = current_app.logger

    sender_addr = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@jobsta.com')
    sender_name = current_app.config.get('MAIL_SENDER_NAME', 'jobsta')
    sender = f"{sender_name} <{sender_addr}>" if sender_name else sender_addr

    if current_app.config.get('MAIL_SUPPRESS_SEND'):
        logger.info("mail.suppressed to=%s subject=%s", to_email, subject)
        logger.debug("mail.suppressed body=%s", body)
        return True

    msg = Message(subject=subject, recipients=[to_email], sender=sender, body=body)
    if html:
        msg.html = html

    try:
        mail.send(msg)
        logger.info("mail.sent to=%s subject=%s", to_email, subject)
        return True
    except Exception as e:
        logger.exception('mail.error send_failed to=%s subject=%s error=%s', to_email, subject, e)
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
