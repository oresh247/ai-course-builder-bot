# 🔧 Решение проблем с Render.com

## ❌ Ошибка: `gunicorn: command not found`

### 🔍 Причина:
Render автоматически определил ваш проект как **Web Service** вместо **Background Worker**.

### ✅ Решение:

#### Вариант 1: Удалите и пересоздайте правильно

1. **Dashboard** → ваш сервис → **Settings** → прокрутите вниз
2. **Delete Service** → подтвердите удаление
3. **New +** → **"Background Worker"** (НЕ "Web Service"!)
4. Выберите репозиторий
5. Убедитесь, что:
   - **Type**: `Background Worker` ✅
   - **Start Command**: `python course_bot.py` ✅

#### Вариант 2: Исправьте существующий сервис

1. **Dashboard** → ваш сервис → **Settings**
2. Найдите **"Service Type"**
3. Измените на **"Background Worker"**
4. **Start Command**: измените на `python course_bot.py`
5. **Manual Deploy** → "Deploy latest commit"

---

## 🎯 Правильная настройка на Render

### ✅ Что должно быть:

```
┌─────────────────────────────────────────┐
│ Service Type: Background Worker    ✅   │
│ (НЕ Web Service!)                       │
├─────────────────────────────────────────┤
│ Name: ai-course-builder-bot             │
│ Runtime: Python 3                       │
│ Region: Frankfurt (EU Central)          │
│ Branch: main                            │
├─────────────────────────────────────────┤
│ Build Command:                          │
│ pip install -r requirements.txt         │
├─────────────────────────────────────────┤
│ Start Command:                          │
│ python course_bot.py                    │
│ (НЕ gunicorn!)                     ✅   │
└─────────────────────────────────────────┘
```

### ❌ Что НЕ должно быть:

```
Service Type: Web Service              ❌
Start Command: gunicorn course_bot:app ❌
Health Check Path: /                   ❌
```

---

## 🚀 Пошаговая инструкция (ПРАВИЛЬНАЯ)

### 1. Dashboard → New +

Нажмите синюю кнопку **"New +"** в правом верхнем углу

### 2. Выберите тип сервиса

**ВАЖНО:** Выберите **"Background Worker"**

```
┌────────────────────────────────────┐
│  What do you want to deploy?       │
├────────────────────────────────────┤
│  ○ Web Service                     │
│  ● Background Worker          ✅   │
│  ○ Private Service                 │
│  ○ Cron Job                        │
│  ○ Static Site                     │
└────────────────────────────────────┘
```

### 3. Connect Repository

- Connect GitHub account (если ещё не подключен)
- Найдите `ai-course-builder-bot`
- Нажмите **"Connect"**

### 4. Заполните настройки

```
Name: ai-course-builder-bot
Region: Frankfurt (EU Central)
Branch: main
Runtime: Python 3

Build Command:
pip install -r requirements.txt

Start Command:
python course_bot.py
```

### 5. Environment Variables

**Прокрутите вниз** до секции "Environment Variables"

**Add Environment Variable:**

Переменная 1:
```
Key:   TELEGRAM_BOT_TOKEN
Value: 8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk
```

**Add Environment Variable** (ещё раз):

Переменная 2:
```
Key:   OPENAI_API_KEY
Value: ваш_ключ_openai
```

### 6. Create Background Worker

Нажмите большую синюю кнопку внизу:
**"Create Background Worker"**

### 7. Проверка

**Логи должны показать:**
```
==> Installing dependencies
pip install -r requirements.txt
...
Successfully installed python-telegram-bot...

==> Running 'python course_bot.py'
INFO:openai_client:Используем прокси для OpenAI API
✅ AI Course Builder запущен!
INFO:telegram.ext.Application:Application started
```

✅ **Если видите это - всё работает!**

---

## 🐛 Другие частые ошибки

### Ошибка: "Module not found"

**Причина:** Не все зависимости установлены

**Решение:**
```bash
# Проверьте requirements.txt
# Должны быть:
python-telegram-bot>=20.0
openai>=1.0.0
python-dotenv
pydantic
httpx
```

### Ошибка: "TELEGRAM_BOT_TOKEN не найден"

**Причина:** Переменная окружения не добавлена

**Решение:**
1. Settings → Environment
2. Add Environment Variable
3. Проверьте имя: `TELEGRAM_BOT_TOKEN` (точно так!)

### Ошибка: "Application is stopping"

**Причина:** Бот запускается как Web Service

**Решение:** Пересоздайте как Background Worker

---

## 📋 Чеклист правильной настройки

При создании на Render проверьте:

- [ ] Тип сервиса: **Background Worker** (НЕ Web Service!)
- [ ] Runtime: **Python 3**
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python course_bot.py` (БЕЗ gunicorn!)
- [ ] Environment Variables добавлены:
  - [ ] `TELEGRAM_BOT_TOKEN`
  - [ ] `OPENAI_API_KEY`
- [ ] Region выбран (любой)
- [ ] Branch: `main`

---

## 🆘 Если ничего не помогает

### Шаг 1: Удалите сервис
1. Settings → Delete Service

### Шаг 2: Очистите кэш браузера
2. Ctrl+Shift+Delete → Очистить кэш

### Шаг 3: Создайте заново
3. **New +** → **Background Worker** (не Web Service!)
4. Следуйте инструкции выше

### Шаг 4: Проверьте файлы

Убедитесь, что в корне проекта нет:
- ❌ `app.py`
- ❌ `wsgi.py`
- ❌ `application.py`

Эти файлы могут ввести Render в заблуждение.

---

## 📞 Поддержка Render

- **Docs**: https://render.com/docs
- **Community**: https://community.render.com/
- **Status**: https://status.render.com/

---

## ✅ Правильные логи

После успешного деплоя вы должны видеть:

```
Oct 19 10:00:00 PM  ==> Cloning from https://github.com/...
Oct 19 10:00:05 PM  ==> Downloading cache...
Oct 19 10:00:10 PM  ==> Installing dependencies
Oct 19 10:00:15 PM  ==> pip install -r requirements.txt
Oct 19 10:00:30 PM  Successfully installed python-telegram-bot-20.7
Oct 19 10:00:30 PM  ==> Build successful!
Oct 19 10:00:31 PM  ==> Deploying...
Oct 19 10:00:35 PM  ==> Running 'python course_bot.py'
Oct 19 10:00:37 PM  INFO:openai_client:Используем прокси для OpenAI API
Oct 19 10:00:38 PM  ✅ AI Course Builder запущен!
Oct 19 10:00:39 PM  INFO:telegram.ext.Application:Application started
```

✅ Бот работает!

---

## 🎯 Альтернатива: Railway.app

Если с Render не получается, попробуйте Railway - там проще:

1. https://railway.app/
2. **New Project** → **Deploy from GitHub repo**
3. Выбрать репозиторий
4. **Variables** → добавить токены
5. **Deploy** - и всё!

Railway автоматически определяет правильную команду запуска.

---

**Читайте также:**
- `QUICK_DEPLOY.md` - быстрый деплой
- `HOSTING_COMPARISON.md` - сравнение платформ

