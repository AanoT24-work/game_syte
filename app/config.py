import os

class Config(object):
    # Основные настройки приложения
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)  # Абсолютный путь к приложению
    UPLOAD_PATH = 'static/upload/'   # Директория для загрузок
    
    # Данные для подключения к PostgreSQL
    USER = os.environ.get('POSTGRES_USER')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    HOST = os.environ.get('POSTGRES_HOST')
    PORT = os.environ.get('POSTGRES_PORT')
    DB = os.environ.get('POSTGRES_DB')
    
    # Настройки SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'  # Строка подключения к БД
    SECRET_KEY = os.environ.get('KEY')  # Секретный ключ для безопасности
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Отслеживание изменений объектов
    
    # ════════════════════════════════════════════════════════════════════
    # CSRF SETTINGS (ДОБАВЬТЕ ЭТОТ БЛОК)
    # ════════════════════════════════════════════════════════════════════
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
    WTF_CSRF_TIME_LIMIT = 3600  # 1 час в секундах
    
    # Если WTF_CSRF_SECRET_KEY не указан, используем SECRET_KEY с суффиксом
    if not WTF_CSRF_SECRET_KEY:
        WTF_CSRF_SECRET_KEY = f"{SECRET_KEY}_csrf_extra"