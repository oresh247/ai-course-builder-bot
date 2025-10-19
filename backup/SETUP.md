# Настройка AI Course Builder Bot

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка токенов

Откройте файл `.env` и замените значения токенов:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_actual_telegram_bot_token_here

# OpenAI Configuration  
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Получение токенов

#### Telegram Bot Token
1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите имя бота (например: "AI Course Builder")
   - Введите username бота (например: "ai_course_builder_bot")
4. Скопируйте полученный токен и вставьте в `.env`

#### OpenAI API Key
1. Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
2. Перейдите в раздел [API Keys](https://platform.openai.com/api-keys)
3. Нажмите "Create new secret key"
4. Скопируйте ключ и вставьте в `.env`

### 4. Тестирование
```bash
python test_bot.py
```

### 5. Запуск бота
```bash
python bot.py
```

## 🔧 Устранение проблем

### Проблема с SSL сертификатами
Если возникают ошибки SSL при установке зависимостей:
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Проблема с кодировкой в Windows
Если возникают ошибки с эмодзи, используйте:
```bash
chcp 65001
python bot.py
```

### Проблема с Pydantic
Если возникают ошибки с Pydantic, убедитесь что используется версия 1.10.13:
```bash
pip install pydantic==1.10.13
```

## 📱 Использование бота

После запуска найдите вашего бота в Telegram и отправьте:

- `/start` - начать работу
- `/create` - создать новый курс
- `/edit` - редактировать курс
- `/view` - просмотреть курс
- `/help` - справка

## 🛠 Разработка

### Структура проекта
```
TGBotCreateCourse/
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация
├── models.py           # Модели данных
├── openai_client.py    # OpenAI клиент
├── course_editor.py    # Редактор курсов
├── test_bot.py         # Тесты
├── requirements.txt    # Зависимости
├── .env               # Переменные окружения
└── README.md          # Документация
```

### Добавление новых функций
1. Создайте новую функцию в соответствующем модуле
2. Добавьте обработчик в `bot.py`
3. Обновите тесты в `test_bot.py`
4. Обновите документацию

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи бота
2. Убедитесь что токены настроены правильно
3. Проверьте подключение к интернету
4. Создайте Issue в репозитории

---

**Готово!** Ваш AI Course Builder Bot готов к работе! 🎉
