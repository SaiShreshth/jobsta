"""
Comprehensive mail logging wrapper with step-by-step diagnostics.
Logs every single step of the email sending process.
"""
import smtplib
import socket
from flask import current_app
from flask_mail import Message


def log_mail_step(step, details="", level="INFO"):
    """Log a mail operation step with detailed information."""
    prefix = "📧 MAIL" if level == "INFO" else "❌ MAIL ERROR" if level == "ERROR" else "⚠️ MAIL WARNING"
    if details:
        current_app.logger.info(f"{prefix} | {step} | {details}")
    else:
        current_app.logger.info(f"{prefix} | {step}")


def send_email_with_detailed_logging(subject, recipient, body, html=None):
    """
    Send email with comprehensive step-by-step logging.
    
    Returns: (success: bool, error_message: str or None)
    """
    from app.extensions import mail
    
    log_mail_step("STEP 1/10: Email send initiated", f"subject='{subject}' recipient='{recipient}'")
    
    try:
        # Step 1: Load configuration
        log_mail_step("STEP 2/10: Loading mail configuration")
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_port = current_app.config.get('MAIL_PORT')
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_use_tls = current_app.config.get('MAIL_USE_TLS')
        mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        suppress_send = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        
        log_mail_step("STEP 2/10: Configuration loaded", 
                     f"server={mail_server}:{mail_port}, tls={mail_use_tls}, sender={mail_sender}, suppress={suppress_send}")
        
        if not mail_username or not current_app.config.get('MAIL_PASSWORD'):
            log_mail_step("STEP 2/10: Configuration check FAILED", "MAIL_USERNAME or MAIL_PASSWORD not set", "ERROR")
            return False, "Mail credentials not configured"
        
        # Step 2: Create message
        log_mail_step("STEP 3/10: Creating email message")
        sender_name = current_app.config.get('MAIL_SENDER_NAME', 'Jobsta')
        sender_full = f"{sender_name} <{mail_sender}>"
        
        msg = Message(
            subject=subject,
            sender=sender_full,
            recipients=[recipient]
        )
        msg.body = body
        if html:
            msg.html = html
        
        log_mail_step("STEP 3/10: Message created", 
                     f"from={sender_full}, to={recipient}, has_html={html is not None}")
        
        # Step 3: Check suppression mode
        if suppress_send:
            log_mail_step("STEP 4/10: Suppression mode enabled - email NOT sent", "MAIL_SUPPRESS_SEND=True", "WARNING")
            return True, None
        
        log_mail_step("STEP 4/10: Suppression check passed - proceeding to send")
        
        # Step 4: Set socket timeout
        log_mail_step("STEP 5/10: Setting socket timeout", "timeout=10 seconds")
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(10)
        
        try:
            # Step 5: Attempt SMTP connection
            log_mail_step("STEP 6/10: Establishing SMTP connection", f"connecting to {mail_server}:{mail_port}")
            
            # Flask-Mail will handle the connection internally, but we'll log it
            mail.send(msg)
            
            # If we reach here, send was successful
            log_mail_step("STEP 10/10: Email sent successfully! ✅", f"to={recipient}")
            return True, None
            
        except smtplib.SMTPAuthenticationError as e:
            log_mail_step("STEP 7/10: SMTP authentication FAILED", f"error={str(e)}", "ERROR")
            return False, f"Authentication failed: {str(e)}"
            
        except smtplib.SMTPConnectError as e:
            log_mail_step("STEP 6/10: SMTP connection FAILED", f"error={str(e)}", "ERROR")
            return False, f"Connection failed: {str(e)}"
            
        except smtplib.SMTPException as e:
            log_mail_step("STEP 6-10: SMTP error occurred", f"error={str(e)}", "ERROR")
            return False, f"SMTP error: {str(e)}"
            
        except socket.timeout:
            log_mail_step("STEP 6-10: Socket timeout", "timeout after 10 seconds", "ERROR")
            return False, "Connection timeout after 10 seconds"
            
        except Exception as e:
            log_mail_step("STEP 6-10: Unexpected error", f"error={type(e).__name__}: {str(e)}", "ERROR")
            return False, f"Unexpected error: {str(e)}"
            
        finally:
            # Restore timeout
            socket.setdefaulttimeout(old_timeout)
            log_mail_step("STEP CLEANUP: Socket timeout restored")
            
    except Exception as e:
        log_mail_step("STEP 1-3: Early failure in email setup", f"error={str(e)}", "ERROR")
        return False, f"Setup error: {str(e)}"


def test_mail_connection_detailed():
    """
    Comprehensive mail connection test with detailed logging.
    Sends test email to saishreshth123@gmail.com.
    
    Returns: (success: bool, error_message: str or None)
    """
    log_mail_step("========================================")
    log_mail_step("MAIL SERVICE INITIALIZATION TEST")
    log_mail_step("========================================")
    
    log_mail_step("TEST PHASE 1: Configuration validation")
    
    # Check all required config
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT')
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    mail_use_tls = current_app.config.get('MAIL_USE_TLS')
    suppress_send = current_app.config.get('MAIL_SUPPRESS_SEND', False)
    
    log_mail_step("Configuration retrieved:")
    log_mail_step(f"  - MAIL_SERVER: {mail_server}")
    log_mail_step(f"  - MAIL_PORT: {mail_port}")
    log_mail_step(f"  - MAIL_USERNAME: {mail_username}")
    log_mail_step(f"  - MAIL_PASSWORD: {'*' * len(mail_password) if mail_password else 'NOT SET'}")
    log_mail_step(f"  - MAIL_DEFAULT_SENDER: {mail_sender}")
    log_mail_step(f"  - MAIL_USE_TLS: {mail_use_tls}")
    log_mail_step(f"  - MAIL_SUPPRESS_SEND: {suppress_send}")
    
    # Validation
    errors = []
    if not mail_server:
        errors.append("MAIL_SERVER not configured")
    if not mail_port:
        errors.append("MAIL_PORT not configured")
    if not mail_username:
        errors.append("MAIL_USERNAME not configured")
    if not mail_password:
        errors.append("MAIL_PASSWORD not configured")
    if not mail_sender:
        errors.append("MAIL_DEFAULT_SENDER not configured")
    
    if errors:
        log_mail_step("TEST PHASE 1: FAILED - Missing configuration", ", ".join(errors), "ERROR")
        return False, "Configuration incomplete: " + ", ".join(errors)
    
    log_mail_step("TEST PHASE 1: PASSED - All configuration present ✅")
    
    # Skip actual sending if suppressed
    if suppress_send:
        log_mail_step("TEST PHASE 2: SKIPPED - Suppression mode enabled", "Set MAIL_SUPPRESS_SEND=False to test actual sending", "WARNING")
        log_mail_step("========================================")
        log_mail_step("MAIL SERVICE TEST: SKIPPED (suppression on)")
        log_mail_step("========================================")
        return True, "Skipped (suppression enabled)"
    
    log_mail_step("TEST PHASE 2: Sending test email to saishreshth123@gmail.com")
    
    subject = "Jobsta Mail Service - Initialization Test"
    body = f"""
This is an automated test email from the Jobsta application.

Mail service has been successfully initialized with the following configuration:
- Server: {mail_server}:{mail_port}
- TLS Enabled: {mail_use_tls}
- Sender: {mail_sender}

If you receive this email, the mail service is working correctly.

Timestamp: {current_app.config.get('STARTUP_TIME', 'unknown')}
    """.strip()
    
    success, error = send_email_with_detailed_logging(
        subject=subject,
        recipient="saishreshth123@gmail.com",
        body=body
    )
    
    if success:
        log_mail_step("TEST PHASE 2: PASSED - Test email sent successfully ✅")
        log_mail_step("========================================")
        log_mail_step("MAIL SERVICE TEST: SUCCESS ✅")
        log_mail_step("========================================")
        return True, None
    else:
        log_mail_step("TEST PHASE 2: FAILED - Test email failed", error, "ERROR")
        log_mail_step("========================================")
        log_mail_step("MAIL SERVICE TEST: FAILED ❌")
        log_mail_step("========================================")
        return False, error
