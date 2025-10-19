# ⚡ Быстрое развертывание на Render.com

## 🎯 За 5 минут до работающего бота!

### Шаг 1: Создайте репозиторий на GitHub ✅
Уже готово! Ваш remote: `https://github.com/oresh247/ai-course-builder-bot.git`

Осталось только создать репозиторий:
1. Откройте: https://github.com/new
2. Name: `ai-course-builder-bot`
3. Visibility: Public
4. ❌ НЕ добавляйте README, .gitignore (они есть!)
5. Create repository
6. Выполните: `git push -u origin main`

---

### Шаг 2: Регистрация на Render
1. Откройте: https://render.com/
2. **Sign Up** → выберите GitHub
3. **Authorize Render** для доступа к репозиториям

---

### Шаг 3: Создание Background Worker

1. **Dashboard** → кнопка **"New +"** → **"Background Worker"**

2. **Connect repository:**
   - Найдите `ai-course-builder-bot`
   - Нажмите **Connect**

3. **Заполните настройки:**
   ```
   Name: ai-course-builder-bot
   Region: Frankfurt (EU Central)  
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python course_bot.py
   Plan: Free
   ```

4. **Environment Variables** → **Add Environment Variable:**
   
   Переменная 1:
   ```
   Key: TELEGRAM_BOT_TOKEN
   Value: ваш_токен_от_botfather
   ```
   
   Переменная 2:
   ```
   Key: OPENAI_API_KEY
   Value: ваш_ключ_openai
   ```

5. **Scroll down** → **Create Background Worker**

---

### Шаг 4: Ожидание деплоя

- ⏳ Процесс займёт **1-2 минуты**
- Следите за логами в реальном времени
- Дождитесь сообщения: `✅ AI Course Builder запущен!`

---

### Шаг 5: Проверка

1. Откройте **Telegram**
2. Найдите вашего бота
3. Отправьте `/start`
4. Бот должен ответить! 🎉

---

## 🎉 Готово!

Ваш бот теперь работает **24/7** в облаке!

### 📊 Что дальше?

- Следите за логами в Render Dashboard
- При push в GitHub бот обновится автоматически
- На бесплатном плане бот "засыпает" после 15 мин неактивности
- Upgrade до Starter ($7/мес) для работы без простоев

---

## 🔗 Полезные ссылки

- **Render Dashboard**: https://dashboard.render.com/
- **Логи**: Dashboard → ваш сервис → Logs
- **Настройки**: Dashboard → ваш сервис → Settings

---

## 📝 Альтернативы

Не нравится Render? См. **HOSTING_GUIDE.md** для:
- Railway.app (от $5/мес)
- Heroku (от $7/мес)
- VPS (от $4/мес)

---

## 🆘 Проблемы?

### Бот не запускается
- Проверьте **Logs** в Render Dashboard
- Убедитесь, что переменные окружения заданы правильно
- Проверьте формат токенов (без пробелов!)

### Repository not found
- Сначала создайте репозиторий на GitHub
- Затем загрузите код: `git push -u origin main`
- Потом деплойте на Render

### Ошибки импорта
- Убедитесь, что `requirements.txt` содержит все зависимости
- Проверьте логи билда

---

## ✅ Чеклист

- [ ] Репозиторий создан на GitHub
- [ ] Код загружен (`git push`)
- [ ] Зарегистрированы на Render
- [ ] Background Worker создан
- [ ] Переменные окружения добавлены
- [ ] Деплой завершён успешно
- [ ] Бот отвечает в Telegram

---

**Время развертывания: ~5 минут** ⚡

**Стоимость: $0** 💰

**Сложность: ⭐ Легко** 🎯

