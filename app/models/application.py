from app.extensions import db

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    applied_at = db.Column(db.DateTime, default=db.func.now())

    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_application'),)

    def __repr__(self):
        return f'<Application {self.user_id} - {self.job_id}>'