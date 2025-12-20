from datetime import datetime
import json  # Импортируем json для работы с историей
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

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Новые поля для редактирования
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    edit_history = db.Column(db.JSON, default=list)  # История изменений
    
    # Relationships - исправляем обратные ссылки
    sender = db.relationship('User', 
                            foreign_keys=[sender_id], 
                            backref='sent_messages',
                            lazy=True)
    
    receiver = db.relationship('User', 
                              foreign_keys=[receiver_id], 
                              backref='received_messages',
                              lazy=True)
    
    __table_args__ = (
        db.Index('idx_message_sender_receiver', 'sender_id', 'receiver_id'),
        db.Index('idx_message_created', 'created_at'),
        CheckConstraint('sender_id != receiver_id', name='no_self_messages'),
    )
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.receiver_id}>'
    
    def add_edit_history(self, old_text):
        """Добавляет запись в историю редактирования"""
        try:
            # Инициализируем историю если пусто
            if self.edit_history is None:
                self.edit_history = []
            
            # Добавляем новую запись
            self.edit_history.append({
                'old_text': old_text,
                'new_text': self.text,
                'edited_at': datetime.utcnow().isoformat()
            })
            
            # Ограничиваем историю последними 10 изменениями
            if len(self.edit_history) > 10:
                self.edit_history = self.edit_history[-10:]
                
        except Exception as e:
            print(f"Error adding edit history: {e}")
            # В случае ошибки создаем новую историю
            self.edit_history = [{
                'old_text': old_text,
                'new_text': self.text,
                'edited_at': datetime.utcnow().isoformat()
            }]
    
    def get_edit_history(self):
        """Получает историю редактирования"""
        try:
            if self.edit_history:
                return self.edit_history
        except Exception as e:
            print(f"Error getting edit history: {e}")
        return []