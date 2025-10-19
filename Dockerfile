# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Переменные окружения (будут переопределены при запуске)
ENV TELEGRAM_BOT_TOKEN=""
ENV OPENAI_API_KEY=""

# Запускаем бота
CMD ["python", "course_bot.py"]

