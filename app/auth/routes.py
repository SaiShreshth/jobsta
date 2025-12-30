from flask import Blueprint, request, redirect, url_for, flash, make_response, render_template
from flask import current_app
from app.extensions import db, mail, bcrypt
from app.models import User, Token, DeviceToken
from flask_mail import Message
import secrets
from datetime import datetime, timedelta
from app.forms import RegistrationForm, LoginForm, SetPasswordForm, ChangePasswordForm

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        if not email.endswith('@msrit.edu'):
            flash('Only @msrit.edu emails are allowed')
            return redirect(url_for('auth.register'))
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('User already exists. Please login.')
            return redirect(url_for('auth.login'))
        # Create user
        user = User(email=email, name=name, is_verified=False)
        if email == 'admin@msrit.edu':
            user.role = 'admin'
        db.session.add(user)
        db.session.commit()
        # Generate magic token
        token_str = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1)  # short-lived
        token = Token(email=email, token=token_str, expires_at=expires, used=False)
        db.session.add(token)
        db.session.commit()
        # Send verification email via SMTP
        login_url = url_for('auth.verify', token=token_str, _external=True)
        subject = 'Verify your MSRIT Job Portal account'
        body = f'Click here to verify your account: {login_url}'
        sender_addr = current_app.config.get('MAIL_DEFAULT_SENDER')
        sender_name = current_app.config.get('MAIL_SENDER_NAME', 'jobsta')
        sender = f"{sender_name} <{sender_addr}>"
        msg = Message(subject, sender=sender, recipients=[email])
        msg.body = body
        try:
            if current_app.config.get('MAIL_SUPPRESS_SEND'):
                # In dev mode, optionally suppress and print
                print(f"[mail suppressed] Registration link for {email}: {login_url}")
            else:
                mail.send(msg)
                print(f"[mail sent] Registration email queued to {email}")
            flash('Verification email sent (check your inbox)')
        except Exception as e:
            print('Email send error:', e)
            # Fallback to showing link in console for debugging
            print(f"Registration link for {email}: {login_url}")
            flash('Unable to send email; check server console for the verification link')
        return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user or not user.is_verified:
            flash('Invalid email or user not verified')
            return redirect(url_for('auth.login'))
        if user.password_hash and password:
            if bcrypt.check_password_hash(user.password_hash, password):
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
            flash('Check the console for the magic link')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)

@bp.route('/verify/<token>')
def verify(token):
    token_obj = Token.query.filter_by(token=token, used=False).first()
    if not token_obj or token_obj.expires_at < datetime.utcnow():
        flash('Invalid or expired token')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(email=token_obj.email).first()
    if not user:
        flash('User not found')
        return redirect(url_for('auth.login'))
    # Mark verified
    user.is_verified = True
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
        return redirect(url_for('auth.login'))
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
        return redirect(url_for('auth.login'))
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