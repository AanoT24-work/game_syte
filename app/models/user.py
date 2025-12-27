from ..extensions import db, login_manager, bcrypt
from datetime import datetime
import hashlib
from flask_login import UserMixin
from .enums import UserStatus

# УДАЛИТЕ импорт AuthService и Flask-зависимости
# УДАЛИТЕ Blueprint и роуты

# Функция загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Модель пользователя
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default='default_avatar.png')
    status = db.Column(db.String(50), default=UserStatus.USER.value)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # Relationships
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Методы для Flask-Login
    @property
    def is_active(self):
        return self.status != UserStatus.BANNED.value
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    # Методы для работы с паролями
    def set_password(self, password):
        """Хэширование пароля"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Проверка пароля"""
        return bcrypt.check_password_hash(self.password, password)
    
    # Методы для JWT
    @staticmethod
    def hash_refresh_token(token):
        """Хэширование refresh токена для хранения в БД"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def to_dict(self):
        """Конвертация в словарь (для JWT payload)"""
        return {
            'id': self.id,
            'login': self.login,
            'avatar': self.avatar,
            'status': self.status,
            'email': self.email
        }
    
    def create_jwt_payload(self, additional_claims=None):
        """Создание payload для JWT токена"""
        from datetime import datetime  # Локальный импорт
        payload = {
            'sub': str(self.id),
            'login': self.login,
            'avatar': self.avatar,
            'status': self.status,
            'iat': datetime.utcnow()
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return payload
    
    def __repr__(self):
        return f'<User {self.login}>'