"""
Comprehensive mail logging wrapper with step-by-step diagnostics using Resend API.
Logs every single step of the email sending process.
"""
from flask import current_app


def log_mail_step(step, details="", level="INFO"):
    """Log a mail operation step with detailed information."""
    prefix = "📧 MAIL" if level == "INFO" else "❌ MAIL ERROR" if level == "ERROR" else "⚠️ MAIL WARNING"
    if details:
        current_app.logger.info(f"{prefix} | {step} | {details}")
    else:
        current_app.logger.info(f"{prefix} | {step}")


def send_email_with_detailed_logging(subject, recipient, body, html=None):
    """
    Send email with comprehensive step-by-step logging using Resend API.
    
    Returns: (success: bool, error_message: str or None)
    """
    log_mail_step("STEP 1/8: Email send initiated", f"subject='{subject}' recipient='{recipient}'")
    
    try:
        # Step 1: Load configuration
        log_mail_step("STEP 2/8: Loading Resend API configuration")
        resend_api_key = current_app.config.get('RESEND_API_KEY')
        mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        sender_name = current_app.config.get('MAIL_SENDER_NAME', 'Jobsta')
        suppress_send = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        
        log_mail_step("STEP 2/8: Configuration loaded", 
                     f"sender={mail_sender}, sender_name={sender_name}, suppress={suppress_send}, api_key_set={bool(resend_api_key)}")
        
        if not resend_api_key:
            log_mail_step("STEP 2/8: Configuration check FAILED", "RESEND_API_KEY not set", "ERROR")
            return False, "Resend API key not configured"
        
        if not mail_sender:
            log_mail_step("STEP 2/8: Configuration check FAILED", "MAIL_DEFAULT_SENDER not set", "ERROR")
            return False, "Mail sender not configured"
        
        # Step 2: Check suppression mode
        if suppress_send:
            log_mail_step("STEP 3/8: Suppression mode enabled - email NOT sent", "MAIL_SUPPRESS_SEND=True", "WARNING")
            return True, None
        
        log_mail_step("STEP 3/8: Suppression check passed - proceeding to send")
        
        # Step 3: Import Resend library
        log_mail_step("STEP 4/8: Importing Resend library")
        try:
            import resend
            log_mail_step("STEP 4/8: Resend library imported successfully")
        except ImportError as e:
            log_mail_step("STEP 4/8: Failed to import Resend library", str(e), "ERROR")
            return False, "Resend library not installed"
        
        # Step 4: Configure Resend API key
        log_mail_step("STEP 5/8: Configuring Resend API key")
        resend.api_key = resend_api_key
        log_mail_step("STEP 5/8: API key configured")
        
        # Step 5: Prepare email parameters
        log_mail_step("STEP 6/8: Preparing email parameters")
        from_address = f"{sender_name} <{mail_sender}>"
        
        params = {
            "from": from_address,
            "to": [recipient],
            "subject": subject,
        }
        
        # Add body content
        if html:
            params["html"] = html
            params["text"] = body  # Fallback text
            log_mail_step("STEP 6/8: Parameters prepared", f"from={from_address}, to={recipient}, html=True")
        else:
            params["text"] = body
            log_mail_step("STEP 6/8: Parameters prepared", f"from={from_address}, to={recipient}, html=False")
        
        # Step 6: Send via Resend API
        log_mail_step("STEP 7/8: Calling Resend API to send email")
        try:
            response = resend.Emails.send(params)
            log_mail_step("STEP 7/8: Resend API call successful", f"response_id={response.get('id', 'unknown')}")
            
            # Step 7: Verify response
            log_mail_step("STEP 8/8: Email sent successfully! ✅", f"email_id={response.get('id', 'unknown')}")
            return True, None
            
        except resend.exceptions.ResendError as e:
            log_mail_step("STEP 7/8: Resend API error", f"error={str(e)}", "ERROR")
            return False, f"Resend API error: {str(e)}"
            
        except Exception as e:
            log_mail_step("STEP 7/8: Unexpected API error", f"error={type(e).__name__}: {str(e)}", "ERROR")
            return False, f"API error: {str(e)}"
            
    except Exception as e:
        log_mail_step("STEP 1-3: Early failure in email setup", f"error={str(e)}", "ERROR")
        return False, f"Setup error: {str(e)}"


def test_mail_connection_detailed():
    """
    Comprehensive mail connection test with detailed logging.
    Sends test email to saishreshth123@gmail.com using Resend API.
    
    Returns: (success: bool, error_message: str or None)
    """
    log_mail_step("========================================")
    log_mail_step("MAIL SERVICE INITIALIZATION TEST (RESEND API)")
    log_mail_step("========================================")
    
    log_mail_step("TEST PHASE 1: Configuration validation")
    
    # Check all required config
    resend_api_key = current_app.config.get('RESEND_API_KEY')
    mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    sender_name = current_app.config.get('MAIL_SENDER_NAME', 'Jobsta')
    suppress_send = current_app.config.get('MAIL_SUPPRESS_SEND', False)
    
    log_mail_step("Configuration retrieved:")
    log_mail_step(f"  - RESEND_API_KEY: {'*' * 20 + resend_api_key[-8:] if resend_api_key else 'NOT SET'}")
    log_mail_step(f"  - MAIL_DEFAULT_SENDER: {mail_sender}")
    log_mail_step(f"  - MAIL_SENDER_NAME: {sender_name}")
    log_mail_step(f"  - MAIL_SUPPRESS_SEND: {suppress_send}")
    
    # Validation
    errors = []
    if not resend_api_key:
        errors.append("RESEND_API_KEY not configured")
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
    
    log_mail_step("TEST PHASE 2: Sending test email to saishreshth123@gmail.com via Resend API")
    
    subject = "Jobsta Mail Service - Initialization Test (Resend API)"
    body = f"""
This is an automated test email from the Jobsta application using Resend API.

Mail service has been successfully initialized with the following configuration:
- API: Resend (HTTPS - no SMTP ports needed)
- Sender: {mail_sender}
- Sender Name: {sender_name}

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

