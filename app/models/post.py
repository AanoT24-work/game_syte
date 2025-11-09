from datetime import datetime

from sqlalchemy import CheckConstraint
from ..extensions import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    liked_by = db.Column(db.JSON, default=list)
    
    # Связь с комментариями
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    
    @property
    def likes_count(self):
        return len(self.liked_by) if self.liked_by else 0
    
    def user_has_liked(self, user_id):
        if not self.liked_by:
            return False
        return user_id in self.liked_by

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
# Добавить моель для чата
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    
    __table_args__ = (
        db.Index('idx_message_sender_receiver', 'sender_id', 'receiver_id'),
        db.Index('idx_message_created', 'created_at'),
        CheckConstraint('sender_id != receiver_id', name='no_self_messages'),
    )
    