from flask import Flask

from .models.user import User
from .extensions import db, migrate, login_manager
from .config import Config

from .routes.post import post
from .routes.user import user

def create_app(config_class=Config):
    # Создаем экземпляр Flask приложения
    app = Flask(__name__)
    
    # Загружаем конфигурацию из класса Config
    app.config.from_object(config_class)
    
    # Инициализируем расширения с нашим приложением
    db.init_app(app)           # База данных SQLAlchemy
    migrate.init_app(app, db)  # Миграции базы данных
    login_manager.init_app(app) # Менеджер аутентификации
    
    # Регистрируем блюпринты ПОСЛЕ инициализации расширений
    # Это важно, чтобы расширения были доступны в роутах
    app.register_blueprint(post)  # Блюпринт для постов
    app.register_blueprint(user)  # Блюпринт для пользователей
    
    # Настраиваем менеджер логина
    login_manager.login_view = 'user.login'  # Эндпоинт для страницы входа
    login_manager.login_message = 'Вы не можете получить доступ к этой странице'  # Сообщение при редиректе
    login_manager.login_message_category = 'danger'  # Категория сообщения (для стилизации)
    
    # Создаем таблицы в базе данных в контексте приложения
    with app.app_context():
        db.create_all()  # Создает все таблицы, определенные в моделях
    
    # Возвращаем готовое приложение
    return app