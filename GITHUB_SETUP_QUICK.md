# 🚀 Быстрая загрузка на GitHub

## ⚠️ ОШИБКА: Repository not found

Это значит, что репозиторий ещё не создан на GitHub.

## ✅ РЕШЕНИЕ (выберите один из вариантов):

### 🌐 Вариант 1: Через веб-интерфейс (проще)

1. **Откройте в браузере**: https://github.com/new

2. **Заполните форму:**
   - Repository name: `ai-course-builder-bot`
   - Description: `🤖 Telegram bot for AI-powered IT course generation using GPT-4`
   - Visibility: **Public** (или Private, если хотите)
   - ❌ **НЕ ДОБАВЛЯЙТЕ** README, .gitignore, license (они уже есть!)

3. **Нажмите**: "Create repository"

4. **Вернитесь в терминал** и выполните:
   ```bash
   git push -u origin main
   ```

### 💻 Вариант 2: Через командную строку (быстрее)

Если у вас установлен GitHub CLI:

```bash
# Создать публичный репозиторий
gh repo create ai-course-builder-bot --public --source=. --remote=origin --push

# Или приватный
gh repo create ai-course-builder-bot --private --source=. --remote=origin --push
```

### 🔧 Вариант 3: Изменить имя репозитория

Если вы уже создали репозиторий с другим именем:

```bash
# Удалить текущий remote
git remote remove origin

# Добавить правильный URL
git remote add origin https://github.com/ваш-username/ваш-репозиторий.git

# Загрузить
git push -u origin main
```

## 📋 Текущее состояние:

✅ Git инициализирован  
✅ Файлы добавлены и закоммичены  
✅ Remote настроен: `https://github.com/oresh247/ai-course-builder-bot.git`  
❌ Репозиторий не создан на GitHub

## 🎯 Что делать СЕЙЧАС:

1. Откройте: https://github.com/new
2. Создайте репозиторий `ai-course-builder-bot`
3. Вернитесь сюда и выполните:
   ```bash
   git push -u origin main
   ```

## ✅ После успешной загрузки:

Ваш проект будет доступен по адресу:
```
https://github.com/oresh247/ai-course-builder-bot
```

---

## 🆘 Если нужна помощь:

- [Создание репозитория на GitHub](https://docs.github.com/ru/get-started/quickstart/create-a-repo)
- [GitHub CLI](https://cli.github.com/)

