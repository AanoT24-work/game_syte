from flask import Flask
from .config import Config

def create_app(config_class=Config):
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализируем расширения
    from .extensions import db, migrate, login_manager, csrf  # ← ДОБАВЬТЕ csrf
    from .models.user import User
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)  # ← ИНИЦИАЛИЗИРУЙТЕ CSRF
    
    # Регистрируем блюпринты
    from .routes.post import post
    from .routes.user import user
    from .routes.chat import chat
    
    app.register_blueprint(post)
    app.register_blueprint(user)
    app.register_blueprint(chat)
    
    # Настраиваем login_manager
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Вы не можете получить доступ к этой странице'
    login_manager.login_message_category = 'danger'
    
    # Настраиваем user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Создаем таблицы
    with app.app_context():
        db.create_all()
    
    return app