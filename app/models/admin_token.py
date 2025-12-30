from app.extensions import db
import uuid
from datetime import datetime


class AdminToken(db.Model):
    token = db.Column(db.String(128), primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)

    def is_valid(self):
        return self.expires_at >= datetime.utcnow()

    def __repr__(self):
        return f'<AdminToken {self.token[:8]}>\n'
