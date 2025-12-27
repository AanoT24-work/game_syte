# app/models/session.py

from ..extensions import db
from datetime import datetime
from .enums import SessionStatus
import sqlalchemy as sa
import hashlib


class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    refresh_token_hash = db.Column(db.String(255), unique=True, nullable=False)
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))

    status = db.Column(
        sa.Enum(SessionStatus,
                values_callable=lambda x: [e.value for e in x],
                name='sessionstatus'),
        default=SessionStatus.ACTIVE,
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    refreshed_at = db.Column(db.DateTime)
    last_used_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        if 'status' not in kwargs:
            kwargs['status'] = SessionStatus.ACTIVE
        super().__init__(**kwargs)

    @staticmethod
    def hash_token(token: str) -> str:
        """Хэширование токена."""
        return hashlib.sha256(token.encode()).hexdigest()

    @property
    def status_value(self):
        return self.status.value

    def is_active(self) -> bool:
        return self.status == SessionStatus.ACTIVE and self.expires_at > datetime.utcnow()

    def update_last_used(self):
        self.last_used_at = datetime.utcnow()

    def revoke(self):
        self.status = SessionStatus.REVOKED
        db.session.add(self)

    def mark_as_refreshed(self):
        self.status = SessionStatus.REFRESHED
        self.refreshed_at = datetime.utcnow()
        db.session.add(self)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status_value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat(),
            'refreshed_at': self.refreshed_at.isoformat() if self.refreshed_at else None,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address
        }
