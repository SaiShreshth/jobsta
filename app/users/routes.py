from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Job, Application, Review, Notification
from app.utils.decorators import login_required
from app.utils.auth import get_current_user
from app.extensions import db, mail
from flask_mail import Message

bp = Blueprint('users', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.all()
    return render_template('users/dashboard.html', jobs=jobs)

@bp.route('/job/<int:job_id>')
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    user = get_current_user()
    applied = Application.query.filter_by(user_id=user.id, job_id=job_id).first() is not None
    reviews = Review.query.filter_by(job_id=job_id).all()
    return render_template('users/job_detail.html', job=job, applied=applied, reviews=reviews)

@bp.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    user = get_current_user()
    existing = Application.query.filter_by(user_id=user.id, job_id=job_id).first()
    if existing:
        flash('Already applied')
        return redirect(url_for('users.job_detail', job_id=job_id, _external=True))
    application = Application(user_id=user.id, job_id=job_id)
    db.session.add(application)
    db.session.commit()
    # Send confirmation email
    msg = Message('Application Received', sender='noreply@jobsta.com', recipients=[user.email])
    msg.body = f'You have successfully applied for {job.title} at {job.company}.'
    mail.send(msg)
    flash('Applied successfully')
    return redirect(url_for('users.dashboard', _external=True))

@bp.route('/review/<int:job_id>', methods=['POST'])
@login_required
def review(job_id):
    job = Job.query.get_or_404(job_id)
    user = get_current_user()
    application = Application.query.filter_by(user_id=user.id, job_id=job_id).first()
    if not application:
        flash('You must apply first')
        return redirect(url_for('users.job_detail', job_id=job_id, _external=True))
    rating = int(request.form['rating'])
    comment = request.form.get('comment')
    review_obj = Review(job_id=job_id, user_id=user.id, rating=rating, comment=comment)
    db.session.add(review_obj)
    db.session.commit()
    flash('Review submitted')
    return redirect(url_for('users.job_detail', job_id=job_id, _external=True))

@bp.route('/applications')
@login_required
def applications():
    user = get_current_user()
    applications = Application.query.filter_by(user_id=user.id).all()
    return render_template('users/applications.html', applications=applications)

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