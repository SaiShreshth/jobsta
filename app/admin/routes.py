from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from app.extensions import db
from app.models import Job, User, Notification, Application
from app.forms import JobForm
from functools import wraps


def admin_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != 'root' or auth.password != 'msrit@123':
            response = make_response('Unauthorized', 401)
            response.headers['WWW-Authenticate'] = 'Basic realm="Admin"'
            return response
        return f(*args, **kwargs)
    return wrapped

bp = Blueprint('admin', __name__)

@bp.route('/')
@admin_only
def index():
    jobs = Job.query.all()
    jobs_count = Job.query.count()
    # applications_count intentionally omitted for admin minimal UI
    users_count = User.query.filter(User.role != 'admin').count()
    return render_template('admin/index.html', jobs=jobs, jobs_count=jobs_count, users_count=users_count, admin_root=True, admin_name='root')

@bp.route('/job/new', methods=['GET', 'POST'])
@admin_only
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
        job = Job(title=form.title.data, description=form.description.data, company=form.company.data, location=form.location.data, salary=form.salary.data, posted_by=poster_id)
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