"""
Скрипт для установки команд бота в Telegram
Это позволит увидеть автодополнение команд при вводе /
"""
# SSL FIX
import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import asyncio
from telegram import Bot, BotCommand
from dotenv import load_dotenv
import httpx

# Патч для httpx
original_init = httpx.AsyncClient.__init__

def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_init(self, *args, **kwargs)

httpx.AsyncClient.__init__ = patched_init

load_dotenv()

async def set_commands():
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    
    commands = [
        BotCommand("start", "🚀 Начать работу с ботом"),
        BotCommand("help", "❓ Справка по всем командам"),
        BotCommand("create", "➕ Создать новый курс"),
        BotCommand("view", "👁️ Просмотреть структуру курса"),
        BotCommand("edit", "✏️ Редактировать курс/модули/уроки"),
        BotCommand("generate", "📚 Сгенерировать лекции и слайды"),
        BotCommand("regenerate", "🔄 Перегенерировать лекции/слайды"),
        BotCommand("regenerate_lesson", "🔁 Перегенерировать отдельный урок"),
        BotCommand("generate_topics", "📖 Детальные материалы по темам урока"),
        BotCommand("export", "📥 Экспортировать курс (JSON/HTML/MD/TXT)"),
    ]
    
    await bot.set_my_commands(commands)
    print("✅ Команды бота успешно установлены!")
    print("\nТеперь при вводе '/' в Telegram вы увидите:")
    for cmd in commands:
        print(f"  /{cmd.command} - {cmd.description}")

if __name__ == "__main__":
    asyncio.run(set_commands())

