from ..extensions import db, login_manager
from datetime import datetime
from flask_login import UserMixin

# Функция загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    posts = db.relationship('Post', backref='user', lazy=True)  # ← строка как строка!
    status = db.Column(db.String(50), default='user')
    login = db.Column(db.String(50))
    password = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(200))