# 📤 Загрузка проекта на GitHub

Подробная инструкция по размещению проекта AI Course Builder Bot на GitHub.

## 📋 Предварительная подготовка

### ✅ Что уже готово:

- ✅ `.gitignore` - исключает ненужные файлы
- ✅ `env.example` - пример конфигурации (без секретов)
- ✅ `LICENSE` - лицензия MIT
- ✅ `README.md` - документация проекта
- ✅ `CONTRIBUTING.md` - руководство для контрибьюторов
- ✅ `requirements.txt` - зависимости Python

### ⚠️ Что НЕ будет загружено:

- ❌ `.env` - ваши токены и ключи (защищены .gitignore)
- ❌ `__pycache__/` - кэш Python
- ❌ `.venv/` - виртуальное окружение
- ❌ `.cursor/` - файлы IDE

## 🚀 Шаг 1: Инициализация Git

Если Git ещё не инициализирован:

```bash
git init
```

## 📦 Шаг 2: Добавление файлов

```bash
# Добавить все файлы проекта
git add .

# Или добавить конкретные файлы
git add course_bot.py handlers/ utils/ models.py
git add requirements.txt README.md LICENSE .gitignore
```

## ✍️ Шаг 3: Первый commit

```bash
git commit -m "🎉 Initial commit: AI Course Builder Bot

Features:
- ✨ Генерация структуры IT-курсов с GPT-4
- 📚 Создание лекций, слайдов и детальных материалов
- ✏️ Редактирование и перегенерация контента
- 💾 Экспорт в JSON/HTML/Markdown/TXT
- 🏗️ Модульная архитектура проекта"
```

## 🌐 Шаг 4: Создание репозитория на GitHub

### Вариант A: Через веб-интерфейс

1. Откройте [github.com/new](https://github.com/new)
2. Заполните:
   - **Repository name**: `ai-course-builder-bot`
   - **Description**: `🤖 Telegram bot for AI-powered IT course generation using GPT-4`
   - **Visibility**: `Public` или `Private`
   - **Не** добавляйте README, .gitignore, license (они уже есть!)
3. Нажмите **Create repository**

### Вариант B: Через GitHub CLI

```bash
gh repo create ai-course-builder-bot --public --source=. --remote=origin --push
```

## 🔗 Шаг 5: Подключение удалённого репозитория

Скопируйте команды с GitHub (после создания репозитория):

```bash
git remote add origin https://github.com/ваш-username/ai-course-builder-bot.git
git branch -M main
```

## 📤 Шаг 6: Загрузка на GitHub

```bash
git push -u origin main
```

## 🎨 Шаг 7: Настройка репозитория (опционально)

### Topics (теги)
Добавьте topics для лучшей находимости:
- `telegram-bot`
- `openai`
- `gpt-4`
- `python`
- `education`
- `course-generator`
- `ai`
- `chatgpt`

### О проекте
В разделе "About":
- Добавьте короткое описание
- Укажите веб-сайт (если есть)
- Включите темы

### GitHub Pages (опционально)
Если хотите разместить документацию:
1. Settings → Pages
2. Source: `main` branch, `/docs` folder
3. Создайте папку `docs/` с HTML документацией

## 📊 Шаг 8: Создание Releases

### Первый релиз

```bash
git tag -a v1.0.0 -m "🎉 First release: AI Course Builder Bot v1.0.0

Features:
- Course structure generation
- Lectures & slides creation  
- Detailed topic materials
- Multi-format export (JSON/HTML/MD/TXT)
- Full editing capabilities
- Modular architecture"

git push origin v1.0.0
```

На GitHub:
1. Перейдите в **Releases**
2. Нажмите **Create a new release**
3. Выберите тег `v1.0.0`
4. Заполните описание
5. Опубликуйте релиз

## 🔐 Безопасность

### Проверьте, что не загружаются секреты:

```bash
# Проверить, что .env в .gitignore
cat .gitignore | grep .env

# Проверить, какие файлы будут загружены
git status

# Если случайно добавили .env - удалите:
git rm --cached .env
git commit -m "Remove .env from tracking"
```

### Если .env уже был загружен:

1. Удалите файл из истории:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

2. **НЕМЕДЛЕННО** смените все токены и ключи!

3. Force push:
```bash
git push origin --force --all
```

## 📝 Шаг 9: Добавление бейджей

Добавьте в README.md бейджи (они уже есть):

```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Stars](https://img.shields.io/github/stars/username/repo)
```

## 🔄 Регулярные обновления

### Пуш изменений:

```bash
git add .
git commit -m "✨ Add new feature"
git push
```

### Создание веток:

```bash
git checkout -b feature/new-feature
# внесите изменения
git add .
git commit -m "✨ Add new feature"
git push -u origin feature/new-feature
# создайте Pull Request на GitHub
```

## 📋 Чеклист перед загрузкой

- [ ] `.env` файл в `.gitignore`
- [ ] Токены и ключи НЕ в коде
- [ ] `env.example` создан
- [ ] `README.md` обновлён
- [ ] `LICENSE` добавлен
- [ ] `requirements.txt` актуален
- [ ] `.gitignore` настроен
- [ ] Код прокомментирован
- [ ] Бот работает локально
- [ ] Документация полная

## 🎯 После загрузки

1. Проверьте README на GitHub
2. Добавьте описание и topics
3. Создайте Issues для известных багов
4. Настройте GitHub Actions (CI/CD) - опционально
5. Добавьте Wiki с подробной документацией
6. Создайте Discussions для сообщества

## 🆘 Решение проблем

### Ошибка: Permission denied
```bash
# Проверьте SSH ключ
ssh -T git@github.com

# Или используйте HTTPS
git remote set-url origin https://github.com/username/repo.git
```

### Ошибка: ! [rejected]
```bash
# Если нужно принудительно загрузить
git push -f origin main  # ОСТОРОЖНО!
```

### Большие файлы
```bash
# Если файл > 100MB, добавьте в .gitignore
echo "large_file.bin" >> .gitignore
git rm --cached large_file.bin
```

## 📚 Полезные ссылки

- [GitHub Docs](https://docs.github.com/)
- [Git Book](https://git-scm.com/book/ru/v2)
- [GitHub CLI](https://cli.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## ✅ Готово!

Ваш проект теперь на GitHub! 🎉

URL проекта: `https://github.com/ваш-username/ai-course-builder-bot`

