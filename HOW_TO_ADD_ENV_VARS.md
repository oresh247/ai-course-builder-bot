# 🔑 Как добавить переменные окружения (Environment Variables)

## 📍 На Render.com (Рекомендуется)

### Вариант 1: При создании сервиса

1. **Создаёте Background Worker** на Render
2. **Прокрутите вниз** до секции "Environment Variables"
3. **Нажмите "Add Environment Variable"**

4. **Добавьте первую переменную:**
   ```
   Key:   TELEGRAM_BOT_TOKEN
   Value: 8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk
   ```
   ✅ Нажмите **Save**

5. **Снова нажмите "Add Environment Variable"**

6. **Добавьте вторую переменную:**
   ```
   Key:   OPENAI_API_KEY
   Value: ваш_ключ_от_openai
   ```
   ✅ Нажмите **Save**

7. **Scroll down** → **Create Background Worker**

### Вариант 2: После создания сервиса

1. **Откройте Dashboard** → выберите ваш сервис
2. **Слева выберите "Environment"**
3. **Add Environment Variable** → вводите Key и Value
4. **Save Changes**
5. Сервис автоматически перезапустится

---

## 📍 На Railway.app

### При создании проекта:

1. **Deploy from GitHub** → выберите репозиторий
2. **Автоматически откроется дашборд**
3. **Вкладка "Variables"** (слева)
4. **New Variable** → Add Variable:
   ```
   Variable: TELEGRAM_BOT_TOKEN
   Value: 8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk
   ```
   ✅ **Add**

5. **New Variable** → Add Variable:
   ```
   Variable: OPENAI_API_KEY
   Value: ваш_ключ_openai
   ```
   ✅ **Add**

6. **Deploy** автоматически запустится

---

## 📍 На Heroku

### Через веб-интерфейс:

1. **Dashboard** → выберите приложение
2. **Settings** → **Config Vars**
3. **Reveal Config Vars**
4. **Нажмите "Add":**
   ```
   KEY:   TELEGRAM_BOT_TOKEN
   VALUE: 8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk
   ```

5. **Снова "Add":**
   ```
   KEY:   OPENAI_API_KEY
   VALUE: ваш_ключ_openai
   ```

### Через командную строку:

```bash
heroku config:set TELEGRAM_BOT_TOKEN="8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk"
heroku config:set OPENAI_API_KEY="ваш_ключ_openai"

# Проверить
heroku config
```

---

## 📍 На VPS (Linux)

### Вариант 1: В .env файле

```bash
# Подключитесь к серверу
ssh root@your-server-ip

# Перейдите в папку проекта
cd ~/ai-course-builder-bot

# Создайте .env файл
nano .env
```

**Вставьте:**
```env
TELEGRAM_BOT_TOKEN=8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk
OPENAI_API_KEY=ваш_ключ_openai
```

**Сохраните:**
- Нажмите `Ctrl+X`
- Нажмите `Y`
- Нажмите `Enter`

### Вариант 2: В systemd service файле

```bash
sudo nano /etc/systemd/system/course-bot.service
```

**Добавьте в секцию [Service]:**
```ini
[Service]
Environment="TELEGRAM_BOT_TOKEN=8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk"
Environment="OPENAI_API_KEY=ваш_ключ_openai"
```

**Перезапустите:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart course-bot
```

---

## 📍 Локально (для тестирования)

### Windows:

**PowerShell:**
```powershell
$env:TELEGRAM_BOT_TOKEN="8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk"
$env:OPENAI_API_KEY="ваш_ключ_openai"
python course_bot.py
```

**CMD:**
```cmd
set TELEGRAM_BOT_TOKEN=8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk
set OPENAI_API_KEY=ваш_ключ_openai
python course_bot.py
```

**Или используйте .env файл:**
```bash
# Создайте файл .env в корне проекта
# И запустите бота - он автоматически прочитает .env
python course_bot.py
```

### Linux/Mac:

```bash
export TELEGRAM_BOT_TOKEN="8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk"
export OPENAI_API_KEY="ваш_ключ_openai"
python course_bot.py
```

---

## 🔑 Где взять токены?

### TELEGRAM_BOT_TOKEN

1. Откройте Telegram
2. Найдите **[@BotFather](https://t.me/botfather)**
3. Отправьте `/newbot`
4. Введите название бота
5. Введите username бота (должен заканчиваться на `bot`)
6. **Скопируйте токен**, который вам пришлёт BotFather

**Пример токена:**
```
8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk
```

### OPENAI_API_KEY

1. Зарегистрируйтесь на **[OpenAI Platform](https://platform.openai.com/)**
2. Перейдите в **[API Keys](https://platform.openai.com/api-keys)**
3. Нажмите **"Create new secret key"**
4. Дайте название (например: "Course Builder Bot")
5. **Скопируйте ключ** (он показывается только 1 раз!)

**Пример ключа:**
```
sk-proj-abc123xyz456...
```

---

## 🎯 Пошаговая инструкция для Render (с картинками)

### Шаг 1: Откройте настройки

После создания Background Worker вы увидите страницу настроек.

**Прокрутите вниз** до секции **"Environment Variables"**

### Шаг 2: Первая переменная

Вы увидите:
```
┌─────────────────────────────────────┐
│  Environment Variables              │
├─────────────────────────────────────┤
│                                     │
│  [Add Environment Variable]         │
│                                     │
└─────────────────────────────────────┘
```

**Нажмите кнопку** "Add Environment Variable"

### Шаг 3: Заполните поля

Появятся два поля:

```
┌─────────────────────────────────────┐
│  Key: [_________________]           │
│                                     │
│  Value: [___________________]       │
│                                     │
│  [ ] Generate Value                 │
│                                     │
│  [Save]    [Cancel]                 │
└─────────────────────────────────────┘
```

**Заполните:**
- **Key:** `TELEGRAM_BOT_TOKEN`
- **Value:** `8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk`

**Нажмите** "Save"

### Шаг 4: Вторая переменная

**Снова нажмите** "Add Environment Variable"

**Заполните:**
- **Key:** `OPENAI_API_KEY`
- **Value:** `sk-proj-abc123xyz456...` (ваш ключ)

**Нажмите** "Save"

### Шаг 5: Проверка

Теперь вы должны видеть:

```
Environment Variables:
├─ TELEGRAM_BOT_TOKEN = 8235655699:AAHy3...  [Edit] [Delete]
└─ OPENAI_API_KEY     = sk-proj-abc...       [Edit] [Delete]
```

✅ **Готово!** Переменные добавлены.

---

## 🔐 Безопасность

### ⚠️ ВАЖНО:

1. **НИКОГДА** не публикуйте токены в коде!
2. **НИКОГДА** не коммитьте `.env` в Git!
3. **Используйте** переменные окружения платформы
4. **Храните** резервные копии токенов в безопасном месте

### ✅ Правильно:
```python
# course_bot.py
import os
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ✅ Из переменных окружения
```

### ❌ Неправильно:
```python
# course_bot.py
TOKEN = "8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk"  # ❌ Хардкод в коде!
```

---

## 🧪 Проверка переменных

### На Render/Railway/Heroku:

**Проверьте логи** - при старте бота вы должны увидеть:
```
INFO:openai_client:Используем прокси для OpenAI API
✅ AI Course Builder запущен!
```

**Если видите ошибку:**
```
❌ TELEGRAM_BOT_TOKEN не найден в .env
```
→ Переменная не установлена или неправильное имя!

### Локально (Windows):

```powershell
# Проверить, установлена ли переменная
echo $env:TELEGRAM_BOT_TOKEN
echo $env:OPENAI_API_KEY

# Если пусто - установите
$env:TELEGRAM_BOT_TOKEN="ваш_токен"
$env:OPENAI_API_KEY="ваш_ключ"
```

### Локально (Linux/Mac):

```bash
# Проверить
echo $TELEGRAM_BOT_TOKEN
echo $OPENAI_API_KEY

# Установить
export TELEGRAM_BOT_TOKEN="ваш_токен"
export OPENAI_API_KEY="ваш_ключ"
```

---

## 📝 Чеклист

После добавления переменных:

- [ ] `TELEGRAM_BOT_TOKEN` добавлен
- [ ] `OPENAI_API_KEY` добавлен
- [ ] Значения без пробелов в начале/конце
- [ ] Токен Telegram содержит `:` (двоеточие)
- [ ] Ключ OpenAI начинается с `sk-`
- [ ] Сервис перезапущен (если нужно)
- [ ] Проверены логи - нет ошибок
- [ ] Бот отвечает в Telegram

---

## 🆘 Частые ошибки

### Ошибка: "TELEGRAM_BOT_TOKEN не найден"

**Причины:**
1. Переменная не добавлена
2. Опечатка в имени (`BOT_TOKEN` вместо `TELEGRAM_BOT_TOKEN`)
3. Лишние пробелы в значении

**Решение:**
- Проверьте точное имя переменной
- Убедитесь, что значение сохранено
- Перезапустите сервис

### Ошибка: "Invalid token format"

**Причина:**
- Неправильный формат токена

**Решение:**
- Токен должен выглядеть как: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`
- Получите новый токен у @BotFather

### Ошибка: "OpenAI API key invalid"

**Причина:**
- Неправильный или истёкший ключ

**Решение:**
- Проверьте ключ на https://platform.openai.com/api-keys
- Создайте новый ключ, если нужно
- Проверьте баланс аккаунта

---

## 💡 Полезные советы

### 1. Копирование токенов

**Правильно:**
- Выделите весь токен
- Ctrl+C для копирования
- Вставьте в поле Value
- **НЕ добавляйте** пробелы или кавычки

**Неправильно:**
```
"8235655699:AAHy3..." ❌ Кавычки
 8235655699:AAHy3...  ❌ Пробелы
```

### 2. Безопасное хранение

Сохраните токены в:
- Password manager (1Password, LastPass)
- Зашифрованный файл
- Secure notes в облаке

### 3. Обновление токенов

Если скомпрометированы:
1. Получите новые токены
2. Обновите на хостинге
3. Сервис автоматически перезапустится

---

## 🎬 Видео-инструкция (текстовая)

### Render.com - пошагово:

```
1. Открыть https://render.com/
   └─ Sign Up через GitHub

2. Dashboard → New + → Background Worker
   └─ Connect repository: ai-course-builder-bot

3. Заполнить форму:
   Name: ai-course-builder-bot
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python course_bot.py
   
4. Scroll down → Environment Variables
   └─ Add Environment Variable (кнопка)
   
5. Первая переменная:
   ┌──────────────────────────────┐
   │ Key:   TELEGRAM_BOT_TOKEN    │
   │ Value: 8235655699:AAHy3L...  │
   └──────────────────────────────┘
   └─ Save
   
6. Add Environment Variable (снова)
   
7. Вторая переменная:
   ┌──────────────────────────────┐
   │ Key:   OPENAI_API_KEY        │
   │ Value: sk-proj-abc123...     │
   └──────────────────────────────┘
   └─ Save

8. Scroll down → Create Background Worker
   └─ Ждать 1-2 минуты

9. Logs → должно быть:
   ✅ AI Course Builder запущен!

10. Telegram → ваш бот → /start
    └─ Бот отвечает! 🎉
```

---

## 📸 Как это выглядит

### Render.com - Environment Variables секция:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Environment Variables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  TELEGRAM_BOT_TOKEN
  ├─ Value: •••••••••••••••••••
  └─ [Edit] [Delete]

  OPENAI_API_KEY  
  ├─ Value: •••••••••••••••••••
  └─ [Edit] [Delete]

  [+ Add Environment Variable]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ✅ Готово!

После добавления переменных окружения ваш бот сможет:
1. ✅ Подключиться к Telegram API
2. ✅ Использовать OpenAI для генерации
3. ✅ Работать 24/7 в облаке

---

## 🔗 Полезные ссылки

- **Render Env Vars**: https://render.com/docs/environment-variables
- **Railway Env Vars**: https://docs.railway.app/develop/variables
- **Heroku Config Vars**: https://devcenter.heroku.com/articles/config-vars

---

**Всё ещё не получается?** Проверьте QUICK_DEPLOY.md для полной инструкции! 📖

