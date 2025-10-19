"""
AI Course Builder Bot - Главный файл запуска

Telegram бот для создания структуры IT-курсов с помощью ИИ.
Поддерживает создание курсов, генерацию контента (лекции, слайды, детальные материалы),
редактирование и экспорт в различные форматы.
"""

# ---------- SSL FIX для корпоративных сетей ----------
import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# ----------------------------------------------------

import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Импортируем обработчики команд
from handlers import (
    start,
    help_command,
    create_course,
    view_course,
    edit_course,
    generate_content,
    regenerate_content,
    regenerate_lesson,
    generate_topics,
    export_course,
    handle_callback,
    handle_message
)

# ---------- ЗАГРУЗКА КОНФИГУРАЦИИ ----------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ---------- ЛОГИРОВАНИЕ ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Главная функция запуска бота"""
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env")
        return

    # Патчим httpx.AsyncClient для отключения SSL
    original_init = httpx.AsyncClient.__init__
    
    def patched_init(self, *args, **kwargs):
        kwargs['verify'] = False
        original_init(self, *args, **kwargs)
    
    httpx.AsyncClient.__init__ = patched_init
    
    # Создаём приложение без JobQueue (для совместимости с Python 3.13)
    app = ApplicationBuilder().token(TOKEN).job_queue(None).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("create", create_course))
    app.add_handler(CommandHandler("view", view_course))
    app.add_handler(CommandHandler("edit", edit_course))
    app.add_handler(CommandHandler("generate", generate_content))
    app.add_handler(CommandHandler("regenerate", regenerate_content))
    app.add_handler(CommandHandler("regenerate_lesson", regenerate_lesson))
    app.add_handler(CommandHandler("generate_topics", generate_topics))
    app.add_handler(CommandHandler("export", export_course))
    
    # Регистрируем обработчики callback и сообщений
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ AI Course Builder запущен! Нажмите Ctrl+C для остановки.")
    logger.info("AI Course Builder bot started successfully")
    
    # Запускаем бота
    app.run_polling(stop_signals=None, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
