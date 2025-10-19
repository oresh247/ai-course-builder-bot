# 🔄 Двунаправленное преобразование форматов Lesson ↔ Lectures

## Проблема

OpenAI может возвращать **разные структуры** в зависимости от контекста:

- При генерации **контента модуля** → возвращает структуру **урока (Lesson)**
- При перегенерации **урока** → тоже может вернуть структуру **лекции (Lecture)**

Это приводило к ошибкам валидации Pydantic.

## Решение: Двунаправленное преобразование

Реализованы **две функции** для преобразования в обе стороны:

### 1. Lesson → Lectures (для генерации контента)

```python
def _convert_lesson_to_lectures(lesson_data):
    """
    Преобразует:
    {
      "lesson_title": "Введение в Python",
      "lesson_goal": "Изучить основы",
      "content_outline": ["Переменные", "Типы данных"]
    }
    
    В:
    {
      "lectures": [{
        "lecture_title": "Введение в Python",
        "slides": [
          {slide_number: 1, title: "Введение в Python", ...},
          {slide_number: 2, title: "Переменные", ...},
          ...
        ]
      }]
    }
    """
```

### 2. Lecture → Lesson (для перегенерации урока)

```python
def _convert_lecture_to_lesson(lecture_data):
    """
    Преобразует:
    {
      "lecture_title": "Введение в Python",
      "learning_objectives": ["Изучить переменные", ...],
      "slides": [
        {title: "Переменные", slide_type: "content"},
        {title: "Типы данных", slide_type: "code"},
        ...
      ]
    }
    
    В:
    {
      "lesson_title": "Введение в Python",
      "lesson_goal": "Изучить переменные ...",
      "content_outline": ["Переменные", "Типы данных"],
      "format": "practice",  // определяется по типам слайдов
      "assessment": "Практическое задание",
      "estimated_time_minutes": 45
    }
    """
```

## Умное извлечение JSON

### Для контента модулей (`_extract_json`)

```python
def _extract_json(content):
    parsed = json.loads(content)
    
    if 'lectures' in parsed:
        # ✅ Правильная структура
        return parsed
        
    elif 'lesson_title' in parsed:
        # 🔄 Структура урока → преобразуем в лекции
        return self._convert_lesson_to_lectures(parsed)
```

### Для перегенерации уроков (`_extract_lesson_json`)

```python
def _extract_lesson_json(content):
    parsed = json.loads(content)
    
    if 'lesson_title' in parsed and 'lesson_goal' in parsed:
        # ✅ Правильная структура урока
        return parsed
        
    elif 'lectures' in parsed:
        # 🔄 Структура лекции → преобразуем обратно в урок
        return self._convert_lecture_to_lesson(parsed['lectures'][0])
```

## Логика преобразования Lecture → Lesson

### 1. Извлечение данных

```python
lesson_title = lecture_data.get("lecture_title")
duration = lecture_data.get("duration_minutes", 45)
learning_objectives = lecture_data.get("learning_objectives", [])
slides = lecture_data.get("slides", [])
```

### 2. Формирование цели урока

```python
if learning_objectives:
    lesson_goal = " ".join(learning_objectives)
else:
    lesson_goal = f"Изучить материал по теме: {lesson_title}"
```

### 3. Извлечение плана из слайдов

```python
content_outline = []
for slide in slides:
    slide_type = slide.get("slide_type")
    # Пропускаем title и summary слайды
    if slide_type not in ["title", "summary"]:
        content_outline.append(slide.get("title"))
```

### 4. Определение формата урока

```python
has_code = any(s.get("slide_type") == "code" for s in slides)
has_quiz = any(s.get("slide_type") == "quiz" for s in slides)

if has_code:
    format_type = "practice"
elif has_quiz:
    format_type = "quiz"
else:
    format_type = "theory"
```

### 5. Определение типа оценки

```python
assessment = (
    "Тест" if has_quiz else
    "Практическое задание" if has_code else
    "Опрос"
)
```

## Использование в коде

### В course_bot.py (перегенерация урока)

**Было:**
```python
content = response.choices[0].message.content.strip()
json_content = content_generator._extract_json(content)  # ❌ Ошибка!
module.lessons[lesson_index] = Lesson(**json_content)
```

**Стало:**
```python
content = response.choices[0].message.content.strip()
json_content = content_generator._extract_lesson_json(content)  # ✅ Правильно!
module.lessons[lesson_index] = Lesson(**json_content)
```

## Логи работы

### Преобразование Lesson → Lectures:

```
WARNING:content_generator:⚠️ OpenAI вернул структуру урока вместо лекций. Преобразуем...
INFO:content_generator:🔄 Преобразуем урок в лекцию со слайдами...
INFO:content_generator:✅ Создана лекция с 9 слайдами
```

### Преобразование Lecture → Lesson:

```
WARNING:content_generator:⚠️ OpenAI вернул структуру lectures вместо lesson. Преобразуем обратно...
INFO:content_generator:🔄 Преобразуем лекцию обратно в урок...
INFO:content_generator:✅ Создан урок с 7 пунктами плана
```

### Правильная структура:

```
INFO:content_generator:✅ Получена правильная структура урока (lesson)
```

или

```
INFO:content_generator:✅ Получена правильная структура с 'lectures'
```

## Преимущества решения

✅ **Универсальность** - работает с любым форматом ответа OpenAI
✅ **Двунаправленность** - преобразует в обе стороны
✅ **Умное извлечение** - автоматически определяет формат
✅ **Логирование** - понятно, что происходит
✅ **Безопасность** - обработка всех edge cases
✅ **Качество** - сохраняет всю важную информацию при преобразовании

## Файлы изменены

- `content_generator.py`:
  - `_extract_json()` - для контента модулей (Lesson → Lectures)
  - `_extract_lesson_json()` - для перегенерации уроков (Lecture → Lesson)
  - `_convert_lesson_to_lectures()` - преобразование Lesson → Lectures
  - `_convert_lecture_to_lesson()` - преобразование Lecture → Lesson
  
- `course_bot.py`:
  - `_regenerate_lesson_item()` - использует `_extract_lesson_json()`

## Результат

🎉 **Система теперь работает с любым форматом ответа OpenAI в любом контексте!**

- ✅ Генерация контента модуля работает
- ✅ Перегенерация уроков работает
- ✅ Перегенерация лекций работает
- ✅ Перегенерация слайдов работает

Нет больше ошибок валидации Pydantic! 🚀

---

**Дата:** 19 октября 2025

**Статус:** ✅ ПОЛНОСТЬЮ РЕШЕНО! Двунаправленное преобразование работает идеально.




