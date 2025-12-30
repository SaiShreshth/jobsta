from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response, current_app
from app.extensions import db
from app.models import Job, User, Notification, Application
from app.models import Recommendation
from app.forms import JobForm, EditJobForm, DeleteJobForm
from functools import wraps
from datetime import datetime, timedelta
import secrets
from app.models.admin_token import AdminToken
from flask import jsonify


def admin_token_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.cookies.get('admin_token')
        if token:
            at = AdminToken.query.filter_by(token=token).first()
            if at and at.expires_at >= datetime.utcnow():
                return f(*args, **kwargs)
        # not authorized, redirect to login for Basic auth
        login_url = url_for('admin.login')
        return redirect(login_url)
    return wrapped


def create_admin_token(response, minutes=30):
    token = secrets.token_urlsafe(48)
    expires = datetime.utcnow() + timedelta(minutes=minutes)
    at = AdminToken(token=token, expires_at=expires)
    db.session.add(at)
    db.session.commit()
    # set cookie
    secure = False
    try:
        secure = request.environ.get('wsgi.url_scheme') == 'https'
    except Exception:
        secure = False
    # when testing, avoid Secure flag so Werkzeug test client stores the cookie
    if current_app and current_app.config.get('TESTING'):
        secure = False
    response.set_cookie('admin_token', token, httponly=True, secure=secure, samesite='Lax', max_age=minutes*60)
    return response


bp = Blueprint('admin', __name__)

bp = Blueprint('admin', __name__)


@bp.route('/logout')
def logout():
    # clear cookie and remove token from DB if present
    token = request.cookies.get('admin_token')
    if token:
        try:
            at = AdminToken.query.filter_by(token=token).first()
            if at:
                db.session.delete(at)
                db.session.commit()
        except Exception:
            db.session.rollback()
    resp = make_response(redirect(url_for('admin.login')))
    resp.set_cookie('admin_token', '', expires=0, httponly=True, path='/')
    return resp

@bp.route('/')
@admin_token_required
def index():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    jobs_count = Job.query.count()
    users_count = User.query.filter(User.role != 'admin').count()
    return render_template('admin/index.html', jobs=jobs, jobs_count=jobs_count, users_count=users_count, admin_root=True, admin_name='root')


@bp.route('/recommendations')
@admin_token_required
def recommendations():
    recs = Recommendation.query.order_by(Recommendation.created_at.desc()).all()
    return render_template('admin/recommendations.html', recommendations=recs)

@bp.route('/job/new', methods=['GET', 'POST'])
@admin_token_required
def new_job():
    form = JobForm()
    if form.validate_on_submit():
        # Admin posts should not rely on session tokens; set posted_by to an admin user id if present
        from app.utils.auth import get_current_user
        current_user = get_current_user()
        if current_user:
            poster_id = current_user.id
        else:
            admin_user = User.query.filter_by(role='admin').first()
            poster_id = admin_user.id if admin_user else None
        
        # Validate apply_url is a proper URL
        apply_url = form.apply_url.data
        if not apply_url.startswith(('http://', 'https://')):
            flash('Apply URL must start with http:// or https://')
            return render_template('admin/new_job.html', form=form)
        
        # Create job with new fields if they exist in the model
        job_kwargs = {
            'title': form.title.data,
            'description': form.description.data,
            'company': form.company.data,
            'location': form.location.data,
            'salary': form.salary.data,
            'posted_by': poster_id
        }
        
        # Add new fields if model supports them
        if hasattr(Job, 'apply_url'):
            job_kwargs['apply_url'] = apply_url
        if hasattr(Job, 'application_email'):
            job_kwargs['application_email'] = form.application_email.data
        if hasattr(Job, 'deadline'):
            job_kwargs['deadline'] = form.deadline.data
        if hasattr(Job, 'status'):
            job_kwargs['status'] = 'active'
        
        job = Job(**job_kwargs)
        db.session.add(job)
        db.session.commit()
        # Notify all users
        users = User.query.filter(User.role != 'admin').all()
        for user in users:
            notification = Notification(user_id=user.id, message=f'New job posted: {job.title} at {job.company}')
            db.session.add(notification)
        db.session.commit()
        flash('Job created successfully')
        return redirect(url_for('admin.index'))
    return render_template('admin/new_job.html', form=form)

@bp.route('/job/<int:job_id>/edit', methods=['GET', 'POST'])
@admin_token_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    form = EditJobForm(obj=job)
    
    if form.validate_on_submit():
        # Detect critical field changes
        critical_changed = False
        if (form.title.data != job.title or 
            form.company.data != job.company or 
            form.deadline.data != job.deadline):
            critical_changed = True
        
        # Store old values for comparison
        old_title = job.title
        old_company = job.company
        old_deadline = job.deadline
        
        # Update job
        job.title = form.title.data
        job.description = form.description.data
        job.company = form.company.data
        job.location = form.location.data
        job.salary = form.salary.data
        
        # Update new fields if they exist
        if hasattr(job, 'apply_url'):
            job.apply_url = form.apply_url.data
        if hasattr(job, 'application_email'):
            job.application_email = form.application_email.data
        if hasattr(job, 'deadline'):
            job.deadline = form.deadline.data
        if hasattr(job, 'updated_at'):
            job.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # If critical fields changed, notify all applicants
        if critical_changed:
            applications = Application.query.filter_by(job_id=job_id).all()
            for app in applications:
                user = User.query.get(app.user_id)
                if user:
                    changes = []
                    if old_title != job.title:
                        changes.append(f"Title: {old_title} → {job.title}")
                    if old_company != job.company:
                        changes.append(f"Company: {old_company} → {job.company}")
                    if old_deadline != job.deadline:
                        changes.append(f"Deadline updated")
                    
                    message = f'Job "{job.title}" has been updated: ' + ', '.join(changes)
                    notification = Notification(user_id=user.id, message=message)
                    db.session.add(notification)
            db.session.commit()
        
        flash('Job updated successfully')
        return redirect(url_for('admin.index'))
    
    # Pre-populate form with existing data
    if job.deadline:
        form.deadline.data = job.deadline
    return render_template('admin/edit_job.html', form=form, job=job)

@bp.route('/job/<int:job_id>/delete', methods=['GET', 'POST'])
@admin_token_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    form = DeleteJobForm()
    
    if form.validate_on_submit():
        action = form.action.data
        applications = Application.query.filter_by(job_id=job_id).all()
        applicants = [app.user_id for app in applications]
        
        if action == 'delete':
            # Hard delete job and related applications
            for app in applications:
                db.session.delete(app)
            db.session.delete(job)
            db.session.commit()
            flash('Job and all applications have been permanently deleted')
        elif action == 'mark_as_deleted':
            # Mark as deleted and notify applicants
            if hasattr(job, 'status'):
                job.status = 'deleted'
            if hasattr(job, 'updated_at'):
                job.updated_at = datetime.utcnow()
            db.session.commit()
            
            for user_id in applicants:
                user = User.query.get(user_id)
                if user:
                    notification = Notification(
                        user_id=user_id,
                        message=f'Job "{job.title}" has been removed. Your application is no longer active.'
                    )
                    db.session.add(notification)
            db.session.commit()
            flash('Job marked as deleted. Applicants have been notified.')
        elif action == 'archive':
            # Archive and notify applicants
            if hasattr(job, 'status'):
                job.status = 'archived'
            if hasattr(job, 'updated_at'):
                job.updated_at = datetime.utcnow()
            db.session.commit()
            
            for user_id in applicants:
                user = User.query.get(user_id)
                if user:
                    notification = Notification(
                        user_id=user_id,
                        message=f'Job "{job.title}" has been archived. Your application status remains unchanged.'
                    )
                    db.session.add(notification)
            db.session.commit()
            flash('Job archived. Applicants have been notified.')
        
        return redirect(url_for('admin.index'))
    
    # Count applications
    app_count = Application.query.filter_by(job_id=job_id).count()
    return render_template('admin/delete_job.html', form=form, job=job, app_count=app_count)


@bp.route('/login')
def login():
    # basic auth endpoint to exchange credentials for a short-lived admin token
    auth = request.authorization
    if not auth or auth.username != 'root' or auth.password != 'msrit@123':
        response = make_response('Unauthorized', 401)
        response.headers['WWW-Authenticate'] = 'Basic realm="Admin"'
        return response
    # create token and set cookie
    resp = make_response(redirect(url_for('admin.index')))
    return create_admin_token(resp, minutes=30)