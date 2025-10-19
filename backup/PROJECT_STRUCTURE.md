# 📁 Структура проекта

## 🚀 Основные файлы (используются)

### Код бота
- **`course_bot.py`** - Главный файл бота со всеми командами
- **`config.py`** - Конфигурация (токены, настройки)
- **`models.py`** - Pydantic модели данных (Course, Module, Lesson, Lecture, Slide)
- **`openai_client.py`** - Клиент для работы с OpenAI API
- **`content_generator.py`** - Генератор учебного контента (лекции, слайды)
- **`exporters.py`** - Экспорт курсов в JSON/HTML/Markdown/TXT
- **`prompts.py`** - Шаблоны промптов для AI
- **`set_bot_commands.py`** - Скрипт для регистрации команд в Telegram

### Конфигурация
- **`requirements.txt`** - Python зависимости
- **`.env`** - Переменные окружения (токены, прокси) - НЕ коммитить!
- **`pip.ini`** - Пример конфигурации pip для корпоративных сетей
- **`env_example.txt`** - Пример файла .env

## 📚 Документация

### Руководства пользователя
- **`README.md`** - Основная документация проекта
- **`QUICKSTART.md`** - Быстрый старт
- **`QUICK_START.md`** - Альтернативный быстрый старт
- **`SETUP.md`** - Инструкции по установке
- **`LAUNCH.md`** - Инструкции по запуску

### Руководства по функциям
- **`EDIT_GUIDE.md`** - Как редактировать модули
- **`EXPORT_GUIDE.md`** - Как экспортировать курсы
- **`CONTENT_GENERATION.md`** - Как генерировать контент
- **`REGENERATE_GUIDE.md`** - Как перегенерировать лекции/слайды
- **`REGENERATE_LESSON_GUIDE.md`** - Как перегенерировать уроки

### Технические документы
- **`SSL_FIX.md`** - Решение проблем с SSL в корпоративных сетях
- **`KNOWN_LIMITATIONS.md`** - Известные ограничения проекта
- **`SUMMARY.md`** - Итоговое резюме проекта

### История решения проблем
- **`ADAPTIVE_FORMAT_SOLUTION.md`** - Адаптивное преобразование форматов AI
- **`BIDIRECTIONAL_CONVERSION.md`** - Двунаправленное преобразование Lesson ↔ Lectures
- **`BUGFIX_CALLBACK_PARSING.md`** - Исправление парсинга callback данных
- **`PROMPT_IMPROVEMENTS.md`** - Улучшения промптов (попытка 1)
- **`PROMPT_FIX_V2.md`** - Улучшения промптов (попытка 2)
- **`PROMPT_FIX_V3_FINAL.md`** - Префикс-подсказка для OpenAI (попытка 3)
- **`SOLUTION_JSON_SCHEMA.md`** - Попытка использования JSON Schema
- **`FINAL_SOLUTION_FALLBACK.md`** - Multi-tier fallback стратегия

## 🗑️ Удаленные файлы

Следующие файлы были удалены как устаревшие:
- ❌ `bot_v13.py` - старая версия
- ❌ `bot.py` - старая версия
- ❌ `corporate_bot.py` - функционал в course_bot.py
- ❌ `final_bot.py` - старая версия
- ❌ `main.py` - заменен на course_bot.py
- ❌ `main copy.py` - копия старого файла
- ❌ `simple_bot.py` - простая версия
- ❌ `test_bot.py` - тестовый файл
- ❌ `course_editor.py` - функционал в course_bot.py

## 🎯 Основной flow запуска

1. Установить зависимости: `pip install -r requirements.txt`
2. Настроить `.env` файл с токенами
3. (Опционально) Зарегистрировать команды: `python set_bot_commands.py`
4. Запустить бота: `python course_bot.py`

## 📦 Зависимости

Основные пакеты:
- `python-telegram-bot` - Telegram Bot API
- `openai` - OpenAI API для генерации контента
- `pydantic` - Валидация данных
- `python-dotenv` - Загрузка переменных окружения
- `httpx` - HTTP клиент (для SSL fix)

## 🔧 Технические особенности

### SSL Fix для корпоративных сетей
- Патч `httpx.AsyncClient` для Telegram
- Отключение SSL для OpenAI API
- Поддержка прокси

### Адаптивное преобразование форматов
- Lesson → Lectures (для генерации контента)
- Lecture → Lesson (для перегенерации уроков)
- Multi-tier fallback (Function Calling → JSON mode → Text mode → Test content)

### Функции бота
- `/start` - Начало работы
- `/help` - Справка
- `/create` - Создание курса
- `/view` - Просмотр курса
- `/edit` - Редактирование модулей
- `/generate` - Генерация детального контента
- `/regenerate` - Перегенерация лекций/слайдов
- `/regenerate_lesson` - Перегенерация уроков
- `/export` - Экспорт в JSON/HTML/MD/TXT

---

**Последнее обновление:** 19 октября 2025




