from app.extensions import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    apply_url = db.Column(db.String(500), nullable=False)
    application_email = db.Column(db.String(254), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)
    posted_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # relationships
    applications = db.relationship('Application', backref='job', lazy=True)
    reviews = db.relationship('Review', backref='job', lazy=True)

    def __repr__(self):
        return f'<Job {self.title}>'