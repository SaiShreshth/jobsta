from app.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=db.func.now())

    # relationships
    jobs = db.relationship('Job', backref='poster', lazy=True)
    applications = db.relationship('Application', backref='applicant', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'