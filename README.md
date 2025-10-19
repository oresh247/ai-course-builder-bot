# 🤖 AI Course Builder Bot

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Telegram](https://img.shields.io/badge/telegram-bot-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Telegram бот для автоматической генерации структуры IT-курсов с использованием GPT-4**

[Возможности](#-возможности) • [Установка](#-установка) • [Использование](#-использование) • [Документация](#-документация)

</div>

---

## 📖 Описание

AI Course Builder - это интеллектуальный Telegram бот, который помогает создавать структурированные IT-курсы с помощью искусственного интеллекта. Бот использует GPT-4 для генерации полноценных образовательных программ с модулями, уроками, лекциями, слайдами и детальными учебными материалами.

## ✨ Возможности

### 🎯 Создание курсов
- **Генерация структуры** - автоматическое создание курса по заданной теме
- **Гибкая настройка** - выбор уровня аудитории (Junior/Middle/Senior)
- **Модульная структура** - от 3 до 10 модулей с уроками

### 📚 Генерация контента
- **Лекции и слайды** (`/generate`) - детальные презентации для каждого урока
- **Детальные материалы** (`/generate_topics`) - углублённый контент по каждой теме:
  - Теоретические материалы
  - Практические примеры
  - Упражнения и задания
  - Вопросы для самопроверки
  - Дополнительные ресурсы

### ✏️ Редактирование
- **Полное редактирование** - изменение любой части курса
- **Перегенерация** - обновление лекций, слайдов и уроков
- **Интерактивная навигация** - удобный просмотр структуры

### 💾 Экспорт
Поддержка множества форматов:
- **JSON** - для программной обработки
- **HTML** - красивые веб-страницы
- **Markdown** - для Notion, Obsidian
- **TXT** - простой текстовый формат

## 🚀 Быстрый старт

### Требования
- Python 3.8+
- Telegram Bot Token
- OpenAI API Key (GPT-4)

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/yourusername/ai-course-builder-bot.git
cd ai-course-builder-bot
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте переменные окружения:**
```bash
cp env.example .env
```

Отредактируйте `.env`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Запустите бота:**
```bash
python course_bot.py
```

## 🔑 Получение токенов

### Telegram Bot Token
1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен

### OpenAI API Key
1. Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
2. Перейдите в [API Keys](https://platform.openai.com/api-keys)
3. Создайте новый ключ и скопируйте его

## 📱 Использование

### Основные команды

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/create` | Создать новый курс |
| `/view` | Просмотреть структуру курса |
| `/edit` | Редактировать курс |
| `/generate` | Сгенерировать лекции и слайды |
| `/generate_topics` | Создать детальные материалы |
| `/regenerate` | Перегенерировать лекции |
| `/regenerate_lesson` | Перегенерировать отдельный урок |
| `/export` | Экспортировать курс |
| `/help` | Справка по командам |

### Процесс создания курса

```
1. /create → Выбор уровня (Junior/Middle/Senior)
2. Ввод темы курса → "Python для веб-разработки"
3. Количество модулей → 3-10
4. Длительность → недели/часы
5. ✨ Получение структуры курса
6. /generate → Создание лекций и слайдов
7. /generate_topics → Детальные материалы по темам
8. /export → Сохранение в нужном формате
```

## 🏗️ Архитектура проекта

```
TGBotCreateCourse/
├── course_bot.py              # Главный файл запуска (~100 строк)
├── handlers/                  # Обработчики Telegram
│   ├── commands.py           # Команды бота
│   ├── callbacks.py          # Callback кнопки
│   ├── callback_helpers.py   # Вспомогательные функции
│   ├── callback_regeneration.py # Перегенерация
│   └── messages.py           # Текстовые сообщения
├── utils/                     # Утилиты
│   ├── session_manager.py    # Управление сессиями
│   └── formatters.py         # Форматирование
├── models.py                  # Pydantic модели
├── content_generator.py       # Генерация контента
├── exporters.py              # Экспорт в разные форматы
├── openai_client.py          # OpenAI клиент
├── prompts.py                # Промпты для AI
└── requirements.txt          # Зависимости
```

## 📊 Структура курса

```
Course
├── course_title
├── target_audience
├── duration_weeks/hours
└── modules[]
    ├── Module
    │   ├── module_title
    │   ├── module_goal
    │   └── lessons[]
    │       └── Lesson
    │           ├── lesson_title
    │           ├── lesson_goal
    │           ├── content_outline[]
    │           ├── format (tutorial/lecture/lab/quiz/project)
    │           ├── estimated_time_minutes
    │           ├── assessment
    │           └── detailed_content (TopicMaterial[])
    └── ModuleContent (generated)
        └── lectures[]
            └── Lecture
                └── slides[]
                    └── Slide
```

## 🛠️ Технологии

- **Python 3.8+** - основной язык
- **python-telegram-bot** - Telegram Bot API
- **OpenAI GPT-4** - генерация контента
- **Pydantic** - валидация данных
- **httpx** - HTTP клиент

## 🔧 Конфигурация

### Для корпоративных сетей

Если у вас проблемы с SSL или нужен прокси:

```env
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=http://your-proxy:port
```

Бот включает автоматические фиксы SSL для корпоративных сетей.

### Настройка промптов

Промпты можно настроить в `prompts.py` для изменения:
- Стиля генерации
- Педагогических стандартов
- Формата контента
- Уровня детализации

## 📚 Документация

- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт
- [PROJECT_README.md](PROJECT_README.md) - Структура проекта
- [CONTRIBUTING.md](CONTRIBUTING.md) - Как внести вклад
- [backup/](backup/) - Детальные гайды и история

## 🐛 Устранение неполадок

### Бот не запускается
```bash
# Проверьте .env файл
cat .env

# Проверьте зависимости
pip install -r requirements.txt
```

### Ошибки OpenAI API
- Проверьте баланс на [OpenAI Platform](https://platform.openai.com/usage)
- Убедитесь в правильности API ключа
- Проверьте доступ к GPT-4

### Проблемы с Telegram
- Проверьте токен бота
- Убедитесь, что бот не запущен в другом месте
- Проверьте интернет-соединение

## 🤝 Вклад в проект

Мы приветствуем ваш вклад! См. [CONTRIBUTING.md](CONTRIBUTING.md) для деталей.

1. Fork проекта
2. Создайте ветку (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. [LICENSE](LICENSE) для деталей.

## 👨‍💻 Автор

Created with ❤️ for education

## 🌟 Поддержите проект

Если проект вам помог - поставьте ⭐️

## 📞 Контакты

- 🐛 **Баги**: [GitHub Issues](../../issues)
- 💡 **Предложения**: [GitHub Discussions](../../discussions)
- 📧 **Email**: your.email@example.com

---

<div align="center">

**[⬆ Вернуться к началу](#-ai-course-builder-bot)**

Made with Python & GPT-4 🚀

</div>
