# app/__init__.py
from flask import Flask
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализируем расширения
    from .extensions import db, migrate, login_manager, csrf
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    from .routes.auth import auth_bp  # <-- ИМПОРТИРУЕМ ДО использования!
    csrf.exempt(auth_bp)  # Теперь auth_bp доступна
    
    # Настраиваем login_manager
    login_manager.login_view = 'user.login'  # Указываем endpoint для входа (user.login существует)
    login_manager.login_message = 'Вы не можете получить доступ к этой странице'
    login_manager.login_message_category = 'danger'
    
    # Импортируем user_loader функцию
    from .models.user import load_user
    login_manager.user_loader(load_user)
    
    # РЕГИСТРИРУЕМ ВСЕ БЛЮПРИНТЫ, включая user!
    from .routes.post import post
    from .routes.user import user  # <-- ДОБАВЬТЕ ЭТУ СТРОКУ!
    from .routes.chat import chat
    
    app.register_blueprint(post)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user)  # <-- ДОБАВЬТЕ ЭТУ СТРОКУ!
    app.register_blueprint(chat)
    
    # Создаем таблицы
    with app.app_context():
        db.create_all()
    
    return app