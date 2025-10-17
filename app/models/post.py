from datetime import datetime
from ..extensions import db

# Модель поста/записи в базе данных
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)