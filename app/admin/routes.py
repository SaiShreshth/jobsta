from flask import Blueprint, render_template, redirect, url_for, flash
from app.extensions import db
from app.models import Job, User, Notification, Application
from app.forms import JobForm
from app.utils.decorators import login_required, admin_required

bp = Blueprint('admin', __name__)

@bp.route('/')
@login_required
@admin_required
def index():
    jobs = Job.query.all()
    jobs_count = Job.query.count()
    applications_count = Application.query.count()
    users_count = User.query.filter(User.role != 'admin').count()
    return render_template('admin/index.html', jobs=jobs, jobs_count=jobs_count, applications_count=applications_count, users_count=users_count)

@bp.route('/job/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_job():
    form = JobForm()
    if form.validate_on_submit():
        from app.utils.auth import get_current_user
        current_user = get_current_user()
        job = Job(title=form.title.data, description=form.description.data, company=form.company.data, location=form.location.data, salary=form.salary.data, posted_by=current_user.id)
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