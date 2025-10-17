import os
from app import create_app
from dotenv import load_dotenv

load_dotenv('.env')

app = create_app()  # твоя функция создания приложения

# Добавь эту строку ↓
application = app  # uWSGI ищет именно "application"

if __name__ == '__main__':
    app.run(debug=True)