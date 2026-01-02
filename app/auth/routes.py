from flask import Blueprint, request, redirect, url_for, flash, make_response, render_template
from flask import current_app
from app.extensions import db, bcrypt
from app.models import User, Token, DeviceToken
import secrets
from datetime import datetime, timedelta
from app.forms import RegistrationForm, LoginForm, SetPasswordForm, ChangePasswordForm
from app.utils.auth import get_current_user

def generate_temp_password(length=12):
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        current_app.logger.info("auth.register attempt email=%s", email)
        if not email.endswith('@msrit.edu'):
            current_app.logger.warning("auth.register blocked_non_msrit email=%s", email)
            flash('Only @msrit.edu emails are allowed')
            return redirect(url_for('auth.register'))
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            current_app.logger.info("auth.register exists email=%s", email)
            flash('User already exists. Please login.')
            return redirect(url_for('auth.login'))
        # Create user
        user = User(email=email, name=name, is_verified=False)
        if email == 'admin@msrit.edu':
            user.role = 'admin'
        db.session.add(user)
        db.session.commit()
        current_app.logger.info("auth.register created_user id=%s email=%s", user.id, email)
        # Generate magic token
        token_str = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1)  # short-lived
        token = Token(email=email, token=token_str, expires_at=expires, used=False)
        db.session.add(token)
        db.session.commit()
        current_app.logger.info("auth.register token_created email=%s", email)
        # Send verification email via SMTP with detailed logging
        login_url = url_for('auth.verify', token=token_str, _external=True)
        current_app.logger.info("auth.register email_send_start to=%s", email)
        
        from app.utils.mail_logger import send_email_with_detailed_logging
        
        email_body = f"Click here to verify your account: {login_url}"
        success, error = send_email_with_detailed_logging(
            subject="Verify your Jobsta account",
            recipient=email,
            body=email_body
        )
        
        if success:
            current_app.logger.info("auth.register email_sent to=%s", email)
            flash('Registration successful! Check your email to verify your account.', 'success')
        else:
            current_app.logger.error("auth.register email_failed to=%s error=%s", email, error)
            flash(f'Account created. Email service error: {error}', 'warning')
        return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if user:
        return redirect(url_for('users.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        current_app.logger.info("auth.login attempt email=%s", email)
        user = User.query.filter_by(email=email).first()
        if not user or not user.is_verified:
            current_app.logger.warning("auth.login invalid_or_unverified email=%s", email)
            flash('Invalid email or user not verified')
            return redirect(url_for('auth.login'))
        if user.password_hash and password:
            if bcrypt.check_password_hash(user.password_hash, password):
                # Issue device token
                device_token = secrets.token_urlsafe(64)
                expires = datetime.utcnow() + timedelta(days=7)
                token_hash = bcrypt.generate_password_hash(device_token[:72]).decode('utf-8')
                device = DeviceToken(user_id=user.id, token_hash=token_hash, expires_at=expires)
                db.session.add(device)
                db.session.commit()
                resp = make_response(redirect(url_for('users.dashboard')))
                resp.set_cookie('device_token', device_token, httponly=True, secure=current_app.config.get('COOKIE_SECURE', False), samesite='Lax', max_age=7*24*3600)
                return resp
            else:
                flash('Invalid password')
                return redirect(url_for('auth.login'))
        else:
            # Send magic link
            token_str = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(hours=1)
            token = Token(email=email, token=token_str, expires_at=expires, used=False)
            db.session.add(token)
            db.session.commit()
            login_url = url_for('auth.verify', token=token_str, _external=True)
            print(f"Magic link for {email}: {login_url}")
            current_app.logger.info("auth.login magic_link_issued email=%s", email)
            flash('Check the console for the magic link')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)

@bp.route('/verify/<token>')
def verify(token):
    token_obj = Token.query.filter_by(token=token, used=False).first()
    if not token_obj or token_obj.expires_at < datetime.utcnow():
        current_app.logger.warning("auth.verify invalid_or_expired token=%s", token)
        flash('Invalid or expired token')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(email=token_obj.email).first()
    if not user:
        current_app.logger.error("auth.verify user_not_found token=%s email=%s", token, token_obj.email)
        flash('User not found')
        return redirect(url_for('auth.login'))
    # Mark verified if not already
    if not user.is_verified:
        user.is_verified = True
        # Generate temp password
        temp_pw = generate_temp_password()
        user.password_hash = bcrypt.generate_password_hash(temp_pw).decode('utf-8')
        current_app.logger.info("auth.verify password_set user=%s", user.id)
        
        # Send temp password email with detailed logging
        current_app.logger.info("auth.verify email_send_start to=%s", user.email)
        
        from app.utils.mail_logger import send_email_with_detailed_logging
        
        email_body = f"Your account has been verified. Your temporary password is: {temp_pw}\nPlease log in and change your password as soon as possible."
        success, error = send_email_with_detailed_logging(
            subject="Welcome to Jobsta - Your Temporary Password",
            recipient=user.email,
            body=email_body
        )
        
        if success:
            current_app.logger.info("auth.verify email_sent to=%s", user.email)
        else:
            current_app.logger.error("auth.verify email_failed to=%s error=%s", user.email, error)
    token_obj.used = True
    # Issue device token
    device_token = secrets.token_urlsafe(64)
    expires = datetime.utcnow() + timedelta(days=7)
    token_hash = bcrypt.generate_password_hash(device_token).decode('utf-8')
    device = DeviceToken(user_id=user.id, token_hash=token_hash, expires_at=expires)
    db.session.add(device)
    db.session.commit()
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('device_token', device_token, httponly=True, secure=current_app.config.get('COOKIE_SECURE', False), samesite='Lax', max_age=7*24*3600)
    return resp

@bp.route('/logout')
def logout():
    resp = make_response(redirect(url_for('auth.login')))
    # Clear cookie (match secure setting when clearing)
    resp.set_cookie('device_token', '', expires=0, secure=current_app.config.get('COOKIE_SECURE', False), httponly=True, samesite='Lax')
    return resp

@bp.route('/set_password', methods=['GET', 'POST'])
def set_password():
    from app.utils.auth import get_current_user
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login', _external=True))
    if user.password_hash:
        flash('Password already set. Use change password.')
        return redirect(url_for('users.dashboard'))
    form = SetPasswordForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match')
            return redirect(url_for('auth.set_password'))
        user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Password set successfully')
        return redirect(url_for('users.dashboard'))
    return render_template('auth/set_password.html', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    from app.utils.auth import get_current_user
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login', _external=True))
    if not user.password_hash:
        flash('No password set. Set password first.')
        return redirect(url_for('auth.set_password'))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(user.password_hash, form.current_password.data):
            flash('Current password incorrect')
            return redirect(url_for('auth.change_password'))
        if form.new_password.data != form.confirm_password.data:
            flash('New passwords do not match')
            return redirect(url_for('auth.change_password'))
        user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        # Invalidate all device tokens
        DeviceToken.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        flash('Password changed. All sessions invalidated.')
        return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html', form=form)