# ⚡ Правильная команда запуска для Render

## ❌ НЕПРАВИЛЬНО (для веб-приложений):
```bash
gunicorn course_bot:app
```

## ✅ ПРАВИЛЬНО (для Telegram бота):
```bash
python course_bot.py
```

или

```bash
python -u course_bot.py
```

---

## 🎯 Где изменить на Render

### Если создаёте новый сервис:

При заполнении формы найдите поле **"Start Command"** и введите:
```
python course_bot.py
```

### Если сервис уже создан:

1. **Dashboard** → выберите ваш сервис
2. **Settings** (слева в меню)
3. Найдите **"Start Command"**
4. Измените на: `python course_bot.py`
5. **Save Changes**
6. Сервис автоматически передеплоится

---

## 📝 Полная конфигурация для Render

```
┌─────────────────────────────────────────┐
│ Service Type: Background Worker    ✅   │
├─────────────────────────────────────────┤
│ Name: ai-course-builder-bot             │
│ Region: Frankfurt                       │
│ Branch: main                            │
├─────────────────────────────────────────┤
│ Build Command:                          │
│ pip install -r requirements.txt         │
├─────────────────────────────────────────┤
│ Start Command:                          │
│ python course_bot.py              ✅    │
└─────────────────────────────────────────┘
```

---

## 🔍 Почему НЕ gunicorn?

### Gunicorn нужен для:
- Flask приложений
- Django приложений
- FastAPI приложений
- Других WSGI/ASGI веб-приложений

### Telegram бот:
- ❌ НЕ веб-приложение
- ❌ НЕ отвечает на HTTP запросы
- ✅ Работает через Telegram API (polling)
- ✅ Запускается как обычный Python скрипт

---

## 📋 Правильные команды для разных типов проектов

| Тип проекта | Команда запуска |
|-------------|-----------------|
| **Telegram Bot** | `python bot.py` ✅ |
| **Flask App** | `gunicorn app:app` |
| **Django App** | `gunicorn project.wsgi:application` |
| **FastAPI** | `uvicorn main:app` |
| **Discord Bot** | `python bot.py` |

---

## 🎬 Как исправить на Render (пошагово)

### Шаг 1: Откройте Settings

```
Dashboard → ai-course-builder-bot → Settings
```

### Шаг 2: Найдите Start Command

Прокрутите вниз до секции **"Build & Deploy"**

Вы увидите:
```
┌─────────────────────────────────────┐
│ Start Command                       │
│ ┌─────────────────────────────────┐ │
│ │ gunicorn course_bot:app     ❌  │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Шаг 3: Измените команду

Кликните в поле и измените на:
```
┌─────────────────────────────────────┐
│ Start Command                       │
│ ┌─────────────────────────────────┐ │
│ │ python course_bot.py        ✅  │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Шаг 4: Сохраните

Нажмите **"Save Changes"**

### Шаг 5: Ручной деплой

Settings → **Manual Deploy** → **"Deploy latest commit"**

### Шаг 6: Проверьте логи

**Logs** → должно быть:
```
==> Running 'python course_bot.py'
✅ AI Course Builder запущен!
INFO:telegram.ext.Application:Application started
```

✅ **Работает!**

---

## 🔧 Альтернативные команды

### Вариант 1 (базовый):
```bash
python course_bot.py
```

### Вариант 2 (с небуферизованным выводом):
```bash
python -u course_bot.py
```
Флаг `-u` полезен для логов в реальном времени.

### Вариант 3 (без создания .pyc файлов):
```bash
python -B course_bot.py
```

### Вариант 4 (полный):
```bash
python -u -B course_bot.py
```

**Рекомендую:** `python course_bot.py` (самый простой)

---

## ⚙️ Если используете render.yaml

Убедитесь, что в `render.yaml` указано:

```yaml
services:
  - type: worker              # ✅ worker, НЕ web!
    name: ai-course-builder-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python course_bot.py  # ✅ Правильная команда
```

После изменения `render.yaml`:
```bash
git add render.yaml
git commit -m "Fix: change start command for Telegram bot"
git push
```

Render автоматически подхватит изменения.

---

## 🎯 Проверка типа сервиса

### Как узнать, какой тип у вас?

1. **Dashboard** → выберите сервис
2. Посмотрите в **заголовок** или **Settings**

**Должно быть:**
```
ai-course-builder-bot (Background Worker) ✅
```

**Если видите:**
```
ai-course-builder-bot (Web Service) ❌
```

→ Удалите и пересоздайте как Background Worker!

---

## 📞 Когда обращаться в поддержку

Если после всех исправлений всё ещё ошибка:

1. **Render Community**: https://community.render.com/
2. **Support**: help@render.com (для платных планов)
3. **Docs**: https://render.com/docs/background-workers

---

## ✅ Финальный чеклист

Перед деплоем убедитесь:

- [ ] Service Type = **Background Worker**
- [ ] Start Command = `python course_bot.py`
- [ ] Build Command = `pip install -r requirements.txt`
- [ ] Environment Variables добавлены
- [ ] НЕТ gunicorn в команде запуска
- [ ] `requirements.txt` содержит все зависимости

---

**Теперь всё должно работать! 🚀**

