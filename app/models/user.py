# Импорт модели поста для связи с пользователем
from ..models.post import Post
# Импорт расширений Flask (база данных и менеджер авторизации)
from ..extensions import db, login_manager
# Импорт модуля для работы с датой и временем
from datetime import datetime
# Импорт миксина для работы с Flask-Login
from flask_login import UserMixin

# Функция загрузки пользователя - обязательна для Flask-Login
# Вызывается при каждой авторизации для получения объекта пользователя по ID
@login_manager.user_loader
def load_user(user_id):
    # Ищем пользователя в базе данных по ID и возвращаем его
    return User.query.get(int(user_id))

# Модель пользователя в базе данных
class User(db.Model, UserMixin):  # UserMixin добавляет необходимые методы для Flask-Login
    # Уникальный идентификатор пользователя (первичный ключ)
    id = db.Column(db.Integer, primary_key=True)
    
    # Связь "один-ко-многим" с моделью Post
    # backref='author' создает свойство author в модели Post для доступа к автору
    posts = db.relationship(Post, backref='author')
    
    # Статус пользователя (например: 'user', 'admin', 'moderator')
    # По умолчанию устанавливается в 'user'
    status = db.Column(db.String, default='user')
    
    # Логин пользователя (строка длиной до 200 символов)
    login = db.Column(db.String(200))
    
    # Пароль пользователя (должен храниться в хэшированном виде)
    password = db.Column(db.String(200))
    
    # Дата регистрации пользователя
    # По умолчанию устанавливается текущая дата и время
    date = db.Column(db.DateTime, default=datetime.utcnow)