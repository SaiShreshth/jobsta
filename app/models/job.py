from app.extensions import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # relationships
    applications = db.relationship('Application', backref='job', lazy=True)
    reviews = db.relationship('Review', backref='job', lazy=True)

    def __repr__(self):
        return f'<Job {self.title}>'