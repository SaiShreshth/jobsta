from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from app.models import Job, Application, Review, Notification
from app.models import Recommendation
from app.utils.decorators import login_required
from app.utils.auth import get_current_user
from app.forms import RecommendationForm
from app.extensions import db, mail
from flask_mail import Message
from datetime import datetime, timedelta
from flask import abort

bp = Blueprint('users', __name__)

@bp.route('/jobs')
@login_required
def jobs():
    # Check if new columns exist, if not filter without status
    try:
        jobs = Job.query.filter_by(status='active').all()
    except Exception:
        # Fallback if status column doesn't exist yet
        jobs = Job.query.all()
    
    # Calculate days until deadline for each job
    now = datetime.utcnow()
    for job in jobs:
        if hasattr(job, 'deadline') and job.deadline:
            delta = job.deadline - now
            if delta.total_seconds() > 0:
                job.days_left = int(delta.total_seconds() / 86400)
            else:
                job.days_left = None
        else:
            job.days_left = None
    return render_template('users/jobs.html', jobs=jobs, now=now)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Check if new columns exist, if not filter without status
    try:
        jobs = Job.query.filter_by(status='active').limit(6).all()
    except Exception:
        # Fallback if status column doesn't exist yet
        jobs = Job.query.limit(6).all()
    return render_template('users/dashboard.html', jobs=jobs)

@bp.route('/settings')
@login_required
def settings():
    user = get_current_user()
    # Placeholder stats
    total_applications = Application.query.filter_by(user_id=user.id).count()
    # For monthly, assume current month
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    # Use applied_at (existing timestamp) for monthly calculations when available
    try:
        monthly_applications = Application.query.filter(
            Application.user_id == user.id,
            db.extract('month', Application.applied_at) == current_month,
            db.extract('year', Application.applied_at) == current_year
        ).count()
    except Exception:
        # Fallback if extract not supported by DB or column missing
        monthly_applications = 0
    return render_template('users/settings.html', user=user, total_applications=total_applications, monthly_applications=monthly_applications)

@bp.route('/job/<int:job_id>')
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    user = get_current_user()
    applied = Application.query.filter_by(user_id=user.id, job_id=job_id).first() is not None
    reviews = Review.query.filter_by(job_id=job_id).all()
    
    # Check if user has reviewed this job
    user_review = None
    if applied:
        user_review = Review.query.filter_by(job_id=job_id, user_id=user.id).first()
    
    # Calculate days until deadline
    days_until_deadline = None
    deadline_warning = None
    if hasattr(job, 'deadline') and job.deadline:
        delta = job.deadline - datetime.utcnow()
        if delta.days >= 0:
            days_until_deadline = delta.days
            if days_until_deadline < 7:
                deadline_warning = 'urgent'
            elif days_until_deadline < 14:
                deadline_warning = 'warning'
    
    return render_template('users/job_detail.html', 
                         job=job, 
                         applied=applied, 
                         reviews=reviews,
                         user_review=user_review,
                         days_until_deadline=days_until_deadline,
                         deadline_warning=deadline_warning)

@bp.route('/recommendations', methods=['GET', 'POST'])
@login_required
def recommendations():
    user = get_current_user()
    form = RecommendationForm()
    if form.validate_on_submit():
        rec = Recommendation(user_id=user.id, title=form.title.data.strip(), body=form.body.data.strip())
        db.session.add(rec)
        db.session.commit()
        flash('Recommendation submitted.', 'success')
        return redirect(url_for('users.recommendations'))

    # list user's own recommendations
    recs = Recommendation.query.filter_by(user_id=user.id).order_by(Recommendation.created_at.desc()).all()
    return render_template('users/recommendations.html', form=form, recommendations=recs)

@bp.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    user = get_current_user()
    current_app.logger.info("users.apply start user_id=%s job_id=%s", getattr(user, 'id', None), job_id)
    
    # Check if job is active (if status column exists)
    if hasattr(job, 'status') and job.status and job.status != 'active':
        flash('This job is no longer accepting applications')
        return redirect(url_for('users.job_detail', job_id=job_id))
    
    # Check if deadline has passed
    if hasattr(job, 'deadline') and job.deadline and job.deadline < datetime.utcnow():
        flash('The application deadline for this job has passed')
        return redirect(url_for('users.job_detail', job_id=job_id))
    
    # Check if already applied
    existing = Application.query.filter_by(user_id=user.id, job_id=job_id).first()
    if existing:
        current_app.logger.info("users.apply duplicate_application user_id=%s job_id=%s", user.id, job_id)
        flash('You have already applied for this job')
        return redirect(job.apply_url)
    
    # Create application record
    application = Application(user_id=user.id, job_id=job_id)
    db.session.add(application)
    
    # Create notification for user
    notification = Notification(user_id=user.id, message=f'You applied for {job.title} at {job.company}')
    db.session.add(notification)
    
    db.session.commit()
    current_app.logger.info("users.apply recorded user_id=%s job_id=%s", user.id, job_id)
    
    # Send confirmation email
    apply_url = getattr(job, 'apply_url', 'https://example.com/apply')
    try:
        msg = Message('Application Received', sender=current_app.config.get('MAIL_DEFAULT_SENDER'), recipients=[user.email])
        msg.body = f'You have successfully applied for {job.title} at {job.company}. Apply at: {apply_url}'
        if current_app.config.get('MAIL_SUPPRESS_SEND'):
            current_app.logger.info("mail.suppressed application to=%s", user.email)
        else:
            mail.send(msg)
            current_app.logger.info("mail.sent application to=%s", user.email)
    except Exception:
        current_app.logger.exception("mail.error application to=%s", user.email)
    
    # Redirect to external apply URL (or job detail if not available)
    apply_url = getattr(job, 'apply_url', None)
    if apply_url:
        return redirect(apply_url)
    else:
        flash('Applied successfully')
        return redirect(url_for('users.job_detail', job_id=job_id))

@bp.route('/review/<int:job_id>', methods=['POST'])
@login_required
def review(job_id):
    job = Job.query.get_or_404(job_id)
    user = get_current_user()
    application = Application.query.filter_by(user_id=user.id, job_id=job_id).first()
    if not application:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'You must apply first'}), 400
        flash('You must apply first')
        return redirect(url_for('users.job_detail', job_id=job_id))
    
    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '')
    
    # Check if user already reviewed
    existing_review = Review.query.filter_by(job_id=job_id, user_id=user.id).first()
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.comment = comment
    else:
        # Create new review
        review_obj = Review(job_id=job_id, user_id=user.id, rating=rating, comment=comment)
        db.session.add(review_obj)
    
    db.session.commit()
    
    # Handle AJAX requests
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Review submitted'})
    
    flash('Review submitted')
    return redirect(url_for('users.job_detail', job_id=job_id))

@bp.route('/applications')
@login_required
def applications():
    user = get_current_user()
    applications = Application.query.filter_by(user_id=user.id).order_by(Application.applied_at.desc()).all()
    # Put rejected applications at the bottom while keeping others sorted by applied_at desc
    try:
        applications.sort(key=lambda a: (a.status == 'rejected', -(a.applied_at.timestamp() if a.applied_at else 0)))
    except Exception:
        # Fallback: if applied_at not present or not datetime, keep DB ordering
        pass
    return render_template('users/applications.html', applications=applications)


@bp.route('/application/<int:application_id>/status', methods=['POST'])
@login_required
def set_application_status(application_id):
    user = get_current_user()
    application = Application.query.get_or_404(application_id)
    if application.user_id != user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    # Accept status from form or json
    status = None
    if request.is_json:
        status = request.json.get('status')
    else:
        status = request.form.get('status')

    if status not in ('pending', 'accepted', 'rejected'):
        return jsonify({'success': False, 'error': 'Invalid status'}), 400

    application.status = status
    if hasattr(application, 'updated_at'):
        try:
            application.updated_at = datetime.utcnow()
        except Exception:
            pass
    db.session.commit()
    return jsonify({'success': True, 'status': application.status})

@bp.route('/application/<int:application_id>/details')
@login_required
def get_application_details(application_id):
    user = get_current_user()
    application = Application.query.get_or_404(application_id)
    
    # Verify ownership
    if application.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    job = application.job
    user_review = Review.query.filter_by(job_id=job.id, user_id=user.id).first()
    
    # Calculate days until deadline
    days_until_deadline = None
    deadline_warning = None
    if hasattr(job, 'deadline') and job.deadline:
        delta = job.deadline - datetime.utcnow()
        if delta.days >= 0:
            days_until_deadline = delta.days
            if days_until_deadline < 7:
                deadline_warning = 'urgent'
            elif days_until_deadline < 14:
                deadline_warning = 'warning'
    
    return jsonify({
        'job': {
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'salary': job.salary,
            'description': job.description,
            'apply_url': getattr(job, 'apply_url', 'https://example.com/apply'),
            'deadline': job.deadline.isoformat() if hasattr(job, 'deadline') and job.deadline else None,
            'days_until_deadline': days_until_deadline,
            'deadline_warning': deadline_warning
        },
        'application': {
            'id': application.id,
            'status': application.status,
            'applied_at': application.applied_at.isoformat() if application.applied_at else None
        },
        'review': {
            'exists': user_review is not None,
            'rating': user_review.rating if user_review else None,
            'comment': user_review.comment if user_review else None
        }
    })

@bp.route('/notifications')
@login_required
def notifications():
    user = get_current_user()
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    # Mark as read
    for n in notifications:
        if not n.read:
            n.read = True
    db.session.commit()
    return render_template('users/notifications.html', notifications=notifications)