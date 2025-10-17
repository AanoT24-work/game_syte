FROM python:3.11

WORKDIR /app

# 1. ТОЛЬКО requirements.txt для кэширования
COPY requirements.txt .

# 2. Устанавливаем зависимости
RUN apt update && apt install -y gcc && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt

# 3. ТОЛЬКО ПОСЛЕ этого копируем весь код
COPY . .

CMD ["uwsgi", "app.ini"]