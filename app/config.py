import os
from datetime import timedelta
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Config(object):
    # Основные настройки приложения
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = 'static/upload/'
    
    # Данные для подключения к PostgreSQL
    USER = os.environ.get('POSTGRES_USER', 'danila')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'bmws1000rr')
    HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    PORT = os.environ.get('POSTGRES_PORT', '54322')
    DB = os.environ.get('POSTGRES_DB', 'mydb_site2')
    
    # Настройки SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = os.environ.get('KEY', 'asb5142hvkjsafv9234r32kjasfilaweurfa')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-change-me')
    JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY', 'default-refresh-secret-change-me')
    
    # Время жизни токенов (в секундах)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 900))  # 15 минут
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 дней
    
    # CSRF Settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', f"{SECRET_KEY}_csrf_extra")
    WTF_CSRF_TIME_LIMIT = 3600  # 1 час в секундах