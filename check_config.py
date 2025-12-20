from app.config import Config
config = Config()
print(f"Database URI: {config.SQLALCHEMY_DATABASE_URI}")
