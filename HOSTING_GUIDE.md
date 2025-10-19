# 🌐 Хостинг для AI Course Builder Bot

Подробное руководство по развертыванию Telegram бота на различных платформах.

## 🎯 Рекомендуемые платформы

### 🥇 1. Render.com (ЛУЧШИЙ ВЫБОР для новичков)

**Почему Render:**
- ✅ **Бесплатный план** (750 часов/месяц)
- ✅ Простое развертывание из GitHub
- ✅ Автоматические деплои
- ✅ HTTPS из коробки
- ✅ Логи в реальном времени
- ⚠️ "Засыпает" после 15 мин неактивности (на бесплатном плане)

**Стоимость:**
- Free: $0/месяц (750 часов)
- Starter: $7/месяц (без засыпания)

### 🥈 2. Railway.app

**Почему Railway:**
- ✅ $5 бесплатных кредитов каждый месяц
- ✅ Очень простой интерфейс
- ✅ Деплой из GitHub одной кнопкой
- ✅ Автоматические переменные окружения
- ✅ Не засыпает

**Стоимость:**
- $5 бесплатно/месяц
- Pay-as-you-go: ~$10-20/месяц

### 🥉 3. Heroku

**Почему Heroku:**
- ✅ Проверенная платформа
- ✅ Отличная документация
- ✅ Большое сообщество
- ❌ НЕТ бесплатного плана (с 2022)

**Стоимость:**
- Eco: $5/месяц (засыпает)
- Basic: $7/месяц

### 💰 4. VDS/VPS (для опытных)

**Провайдеры:**
- **DigitalOcean** - от $6/месяц
- **Hetzner** - от €4/месяц
- **Selectel (RU)** - от 200₽/месяц
- **Timeweb (RU)** - от 150₽/месяц

**Преимущества:**
- ✅ Полный контроль
- ✅ Можно запустить несколько ботов
- ✅ Дешевле при масштабировании

**Недостатки:**
- ❌ Нужно настраивать самому
- ❌ Требуются знания Linux

---

## 🚀 Развертывание на Render.com (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Подготовка репозитория

1. **Загрузите проект на GitHub** (см. DEPLOY_TO_GITHUB.md)

2. **Создайте файл `render.yaml`** (уже готов, см. ниже)

### Шаг 2: Настройка Render

1. **Зарегистрируйтесь:** https://render.com/

2. **Нажмите** "New +" → "Background Worker"

3. **Подключите GitHub репозиторий:**
   - Connect account → GitHub
   - Выберите ваш репозиторий

4. **Настройте сервис:**
   - **Name**: `ai-course-builder-bot`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python course_bot.py`

5. **Добавьте переменные окружения:**
   - `TELEGRAM_BOT_TOKEN` = ваш токен
   - `OPENAI_API_KEY` = ваш ключ
   - (опционально) `HTTP_PROXY`, `HTTPS_PROXY`

6. **Создайте сервис** → "Create Background Worker"

### 🎉 Готово! Бот работает 24/7

---

## 🚂 Развертывание на Railway.app

### Шаг 1: Создание проекта

1. **Зарегистрируйтесь:** https://railway.app/

2. **New Project** → "Deploy from GitHub repo"

3. **Выберите репозиторий** `ai-course-builder-bot`

4. **Настройте переменные:**
   - Variables → Add Variable
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`

5. **Настройте команду запуска:**
   - Settings → Start Command: `python course_bot.py`

### 🎉 Бот развернут!

---

## 💜 Развертывание на Heroku

### Подготовка

1. **Создайте `Procfile`:**
```
worker: python course_bot.py
```

2. **Создайте `runtime.txt`:**
```
python-3.11.7
```

### Развертывание

```bash
# Установите Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Войдите
heroku login

# Создайте приложение
heroku create ai-course-builder-bot

# Установите переменные
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set OPENAI_API_KEY=your_key

# Деплой
git push heroku main

# Запустите worker
heroku ps:scale worker=1

# Проверьте логи
heroku logs --tail
```

---

## 🖥️ Развертывание на VPS (Ubuntu)

### Шаг 1: Подключение к серверу

```bash
ssh root@your-server-ip
```

### Шаг 2: Установка зависимостей

```bash
# Обновить систему
apt update && apt upgrade -y

# Установить Python и pip
apt install python3 python3-pip python3-venv git -y

# Установить tmux (для фонового запуска)
apt install tmux -y
```

### Шаг 3: Клонирование проекта

```bash
# Перейти в домашнюю директорию
cd ~

# Клонировать репозиторий
git clone https://github.com/oresh247/ai-course-builder-bot.git
cd ai-course-builder-bot

# Создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### Шаг 4: Настройка .env

```bash
# Создать .env файл
nano .env
```

Вставьте:
```env
TELEGRAM_BOT_TOKEN=ваш_токен
OPENAI_API_KEY=ваш_ключ
```

Сохраните: `Ctrl+X`, `Y`, `Enter`

### Шаг 5: Запуск бота

**Вариант A: С помощью tmux (рекомендуется)**

```bash
# Создать сессию tmux
tmux new -s bot

# Активировать venv
source .venv/bin/activate

# Запустить бота
python course_bot.py

# Отключиться от сессии: Ctrl+B, затем D
# Вернуться: tmux attach -t bot
```

**Вариант B: С помощью systemd (автозапуск)**

```bash
# Создать service файл
sudo nano /etc/systemd/system/course-bot.service
```

Содержимое:
```ini
[Unit]
Description=AI Course Builder Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ai-course-builder-bot
Environment="PATH=/root/ai-course-builder-bot/.venv/bin"
ExecStart=/root/ai-course-builder-bot/.venv/bin/python course_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable course-bot

# Запустить бота
sudo systemctl start course-bot

# Проверить статус
sudo systemctl status course-bot

# Посмотреть логи
sudo journalctl -u course-bot -f
```

### Шаг 6: Обновление бота

```bash
cd ~/ai-course-builder-bot
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart course-bot
```

---

## 📊 Сравнение платформ

| Платформа | Цена | Сложность | Автодеплой | Логи | Рекомендация |
|-----------|------|-----------|------------|------|--------------|
| **Render** | Free-$7 | ⭐ Легко | ✅ | ✅ | 🥇 Для начинающих |
| **Railway** | $5-$20 | ⭐ Легко | ✅ | ✅ | 🥈 Хороший баланс |
| **Heroku** | $5-$7 | ⭐⭐ Средне | ✅ | ✅ | Проверенный вариант |
| **VPS** | $4-$10 | ⭐⭐⭐ Сложно | ❌ | ⚠️ | Для опытных |

## 🔧 Дополнительные файлы для хостинга

### Для Render.com - `render.yaml`

```yaml
services:
  - type: worker
    name: ai-course-builder-bot
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python course_bot.py
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.7
```

### Для Heroku - `Procfile`

```
worker: python course_bot.py
```

### Для Railway - `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python course_bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🔐 Безопасность на хостинге

### ⚠️ ВАЖНО:

1. **НЕ коммитьте .env** в репозиторий!
2. Используйте **переменные окружения** платформы
3. Регулярно **обновляйте зависимости**
4. Включите **двухфакторную аутентификацию** на GitHub
5. **Ограничьте права** API ключей

### Настройка переменных окружения:

**Render/Railway/Heroku:**
- Зайдите в настройки сервиса
- Добавьте Environment Variables
- НЕ ставьте галочку "Sync from GitHub"

---

## 📈 Мониторинг и логи

### Render
```
Dashboard → Logs (в реальном времени)
```

### Railway
```
Deployment → Logs
```

### Heroku
```bash
heroku logs --tail
```

### VPS
```bash
# systemd
sudo journalctl -u course-bot -f

# tmux
tmux attach -t bot
```

---

## 💰 Оценка стоимости

### Для бота с ~100 пользователей/день:

| Платформа | Месяц | Год |
|-----------|-------|-----|
| **Render Free** | $0 | $0 |
| **Render Starter** | $7 | $84 |
| **Railway** | $10-15 | $120-180 |
| **Heroku Basic** | $7 | $84 |
| **VPS (Hetzner)** | €4 (~$4.5) | ~$54 |

### 💡 Рекомендация по бюджету:

- **$0** → Render Free (с ограничениями)
- **$5-10/мес** → Railway или VPS
- **Профессионально** → VPS + мониторинг

---

## 🚀 Быстрый старт: Render.com (5 минут)

### 1. Создайте файлы для Render:

Файл уже готов - см. раздел "Дополнительные файлы" ниже.

### 2. Откройте Render:

https://dashboard.render.com/

### 3. New Background Worker:

- Repository: ваш GitHub репозиторий
- Name: `ai-course-builder-bot`
- Start Command: `python course_bot.py`

### 4. Добавьте переменные:

Environment → Add Environment Variable:
- `TELEGRAM_BOT_TOKEN` = ваш_токен
- `OPENAI_API_KEY` = ваш_ключ

### 5. Deploy!

Нажмите "Create Background Worker"

### ✅ Бот работает 24/7!

---

## 🔄 Автоматические обновления

### Настройка CI/CD:

1. **Push в GitHub** → Автоматически деплоится на Render/Railway
2. Можно настроить **деплой только из main** ветки
3. Просмотр **логов деплоя** в реальном времени

### GitHub Actions (опционально):

Создайте `.github/workflows/deploy.yml` для дополнительных проверок перед деплоем.

---

## 🐛 Решение проблем

### Бот не отвечает после деплоя

```bash
# Проверьте логи
# Render: Dashboard → Logs
# Убедитесь, что нет ошибок импорта
```

### Ошибки OpenAI API

```bash
# Проверьте переменные окружения
# Убедитесь, что OPENAI_API_KEY правильно установлен
```

### Проблемы с прокси

Если хостинг блокирует OpenAI:
- Используйте VPS в нужной стране
- Настройте прокси через переменные `HTTP_PROXY`, `HTTPS_PROXY`

---

## 📊 Мониторинг

### Бесплатные инструменты:

1. **UptimeRobot** - проверка доступности
   - https://uptimerobot.com/
   - Отправляет уведомления при падении

2. **Better Uptime** - мониторинг
   - https://betteruptime.com/
   - 10 мониторов бесплатно

3. **Sentry** - отслеживание ошибок
   - https://sentry.io/
   - 5K событий/месяц бесплатно

---

## 🎓 Пошаговая инструкция для Render (детально)

### 1. Подготовка GitHub

✅ Проект уже готов с `.gitignore`, `requirements.txt`

### 2. Регистрация на Render

1. Откройте: https://render.com/
2. Sign Up → GitHub
3. Authorize Render

### 3. Создание Background Worker

1. Dashboard → "New +" → "Background Worker"
2. Connect repository: `ai-course-builder-bot`
3. Name: `ai-course-builder-bot`
4. Region: `Frankfurt (EU Central)` или ближайший
5. Branch: `main`
6. Runtime: `Python 3`
7. Build Command: `pip install -r requirements.txt`
8. Start Command: `python course_bot.py`

### 4. Настройка Environment

1. Scroll down → "Environment Variables"
2. Add Environment Variable:
   ```
   Key: TELEGRAM_BOT_TOKEN
   Value: 8235655699:AAHy3LF1_61y4l2I1MZNEB8HGZArWIJJEvk
   ```
3. Add Environment Variable:
   ```
   Key: OPENAI_API_KEY
   Value: ваш_ключ_openai
   ```

### 5. Deploy

1. Scroll down → "Create Background Worker"
2. Дождитесь завершения (1-2 минуты)
3. Проверьте Logs

### 6. Проверка

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Бот должен ответить!

---

## 📦 Дополнительные файлы для деплоя

### `render.yaml` (поместить в корень)

```yaml
services:
  - type: worker
    name: ai-course-builder-bot
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python course_bot.py
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.7
```

### `Procfile` (для Heroku)

```
worker: python course_bot.py
```

### `runtime.txt` (для Heroku)

```
python-3.11.7
```

### `.dockerignore` (если используете Docker)

```
.venv/
__pycache__/
*.pyc
.env
.git/
.gitignore
*.md
backup/
```

---

## 🎯 Финальные рекомендации

### Для новичков:
1. **Render.com** → Бесплатно, просто, надёжно
2. Следуйте инструкции выше
3. Всё работает за 5 минут

### Для продакшена:
1. **Railway.app** → $10-15/мес, стабильно
2. Или **VPS** → больше контроля

### Для разработки:
1. Локальный запуск → `python course_bot.py`
2. Ngrok для тестирования webhook (опционально)

---

## 📞 Поддержка

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app/
- **Heroku Docs**: https://devcenter.heroku.com/

---

## ✅ Чеклист перед деплоем

- [ ] Проект загружен на GitHub
- [ ] `.env` в `.gitignore`
- [ ] `requirements.txt` актуален
- [ ] Бот работает локально
- [ ] Токены готовы
- [ ] Выбрана платформа
- [ ] Переменные окружения настроены
- [ ] Команда запуска указана

---

## 🎉 После успешного деплоя

1. Проверьте логи
2. Протестируйте все команды
3. Настройте мониторинг (UptimeRobot)
4. Добавьте ссылку в README
5. Наслаждайтесь! 🚀

