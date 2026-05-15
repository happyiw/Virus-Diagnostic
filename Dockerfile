FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_USER=virusdb
ENV DB_PASSWORD=viruspass
ENV DB_NAME=virus_diagnostic

# Инициализация: генерация датасета и обучение модели (если нужно)
RUN python init.py 2>&1 | head -100 || echo "Инициализация пропущена или завершена"

# Команда для запуска приложения
CMD ["python", "app/main.py"]
