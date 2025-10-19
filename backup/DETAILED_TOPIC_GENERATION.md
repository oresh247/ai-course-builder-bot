# 📚 Генерация детальных учебных материалов по темам

## Обзор

**Третий уровень детализации** - генерация полноценных учебных материалов для каждой темы из плана урока.

## Структура контента

```
Курс
└── Модуль
    └── Урок
        └── План контента (content_outline)
            └── ТЕМА → Детальный учебный материал 📚
```

## Пример

### Урок: "Установка и настройка окружения"

**План контента:**
1. Установка Python: подробное руководство по установке Python на разных операционных системах
2. Настройка рабочего окружения: установка и настройка IDE
3. Установка и использование пакетного менеджера pip
4. Создание виртуального окружения
5. Установка и использование фреймворка Flask

### Для каждой темы генерируется:

#### 1. **Введение** (introduction)
- 2-3 абзаца
- Зачем это нужно
- Где применяется
- Что студент узнает

#### 2. **Теория** (theory)
- Подробное объяснение концепции
- 4-6 абзацев
- Простым языком с аналогиями

#### 3. **Практические примеры** (examples)
- 3-5 конкретных примеров
- От простого к сложному
- С объяснением каждого

#### 4. **Примеры кода** (code_snippets)
- 2-4 примера кода
- С подробными комментариями
- Рабочий, тестированный код

#### 5. **Ключевые моменты** (key_points)
- 5-7 важных пунктов
- Что обязательно нужно запомнить

#### 6. **Частые ошибки** (common_mistakes)
- 3-5 типичных ошибок новичков
- Как их избежать

#### 7. **Лучшие практики** (best_practices)
- 3-5 рекомендаций
- Как делать правильно

#### 8. **Упражнения** (practice_exercises)
- 3-5 заданий для практики
- Разного уровня сложности
- Конкретные и проверяемые

#### 9. **Вопросы для самопроверки** (quiz_questions)
- 5-7 вопросов
- Проверка понимания материала

#### 10. **Дополнительные ресурсы** (additional_resources)
- Ссылки на документацию
- Рекомендуемые статьи
- Видео-курсы

## Модели данных

### TopicMaterial
```python
class TopicMaterial(BaseModel):
    topic_title: str
    topic_number: int
    
    # Основной контент
    introduction: str
    theory: str
    examples: List[str]
    code_snippets: Optional[List[str]]
    
    # Дополнительные материалы
    key_points: List[str]
    common_mistakes: List[str]
    best_practices: List[str]
    
    # Задания и вопросы
    practice_exercises: List[str]
    quiz_questions: List[str]
    
    # Ресурсы
    additional_resources: Optional[List[str]]
    estimated_reading_time_minutes: int
```

### LessonContent
```python
class LessonContent(BaseModel):
    lesson_title: str
    lesson_goal: str
    lesson_number: int
    module_number: int
    
    topics: List[TopicMaterial]
    total_topics: int
    total_estimated_time_minutes: int
```

### Обновленный Lesson
```python
class Lesson(BaseModel):
    lesson_title: str
    lesson_goal: str
    content_outline: List[str]
    assessment: str
    format: str
    estimated_time_minutes: int
    
    # НОВОЕ: Опциональный детальный контент
    detailed_content: Optional[LessonContent] = None
```

## API

### Генератор контента

```python
class ContentGenerator:
    def generate_lesson_detailed_content(
        self, 
        lesson: Lesson,
        module_number: int,
        course_title: str,
        module_title: str,
        target_audience: str
    ) -> Optional[LessonContent]:
        """
        Генерирует детальный учебный материал 
        для каждой темы урока
        """
```

### Использование

```python
content_gen = ContentGenerator()

# Генерируем детальный контент для урока
lesson_content = content_gen.generate_lesson_detailed_content(
    lesson=lesson,
    module_number=1,
    course_title="Python для начинающих",
    module_title="Основы Python",
    target_audience="beginner"
)

# Доступ к материалам по темам
for topic in lesson_content.topics:
    print(f"Тема: {topic.topic_title}")
    print(f"Введение: {topic.introduction}")
    print(f"Теория: {topic.theory}")
    print(f"Примеры: {len(topic.examples)}")
    print(f"Код: {len(topic.code_snippets or [])}")
    print(f"Упражнения: {len(topic.practice_exercises)}")
```

## Промпт для AI

Система использует специальный промпт `TOPIC_MATERIAL_PROMPT_TEMPLATE`, который:

1. Передает контекст (курс, модуль, урок, аудитория)
2. Указывает конкретную тему для детализации
3. Требует создать полноценный учебный материал
4. Задает структуру ответа (JSON)

### Особенности промпта

- ✅ Учитывает уровень аудитории
- ✅ Требует практичность и примеры
- ✅ Запрашивает код с комментариями
- ✅ Просит указать частые ошибки
- ✅ Требует упражнения для закрепления

## Fallback стратегия

Если OpenAI не может сгенерировать контент:

1. **JSON mode** - попытка с `response_format: {"type": "json_object"}`
2. **Обычный режим** - попытка с обычным GPT-4
3. **Тестовый контент** - качественный placeholder с структурой

```python
if topic_material:
    topics.append(topic_material)
else:
    # Fallback: создаем базовый материал
    topics.append(self._get_test_topic_material(topic_number, topic_title))
```

## Преимущества

✅ **Детализация** - каждая тема раскрыта полностью
✅ **Самостоятельное изучение** - студент может учиться без преподавателя
✅ **Практичность** - много примеров и упражнений
✅ **Структурированность** - единый формат для всех тем
✅ **Проверяемость** - вопросы для самопроверки
✅ **Код** - рабочие примеры с комментариями

## Пример сгенерированного материала

### Тема: "Установка Python"

```json
{
  "topic_title": "Установка Python",
  "topic_number": 1,
  "introduction": "Python — один из самых популярных языков программирования...",
  "theory": "Установка Python — первый шаг к началу разработки...",
  "examples": [
    "Пример 1: Установка на Windows через официальный установщик",
    "Пример 2: Установка на macOS через Homebrew",
    "Пример 3: Установка на Linux через apt/yum"
  ],
  "code_snippets": [
    "# Проверка установки\npython --version\npython3 --version",
    "# Запуск интерактивной оболочки\npython\n>>> print('Hello, World!')"
  ],
  "key_points": [
    "Python 3.x - текущая актуальная версия",
    "Важно добавить Python в PATH",
    "pip устанавливается автоматически с Python",
    ...
  ],
  "common_mistakes": [
    "Ошибка 1: Забыли добавить Python в PATH при установке",
    "Ошибка 2: Установили Python 2.x вместо 3.x",
    ...
  ],
  "best_practices": [
    "Используйте виртуальные окружения для проектов",
    "Регулярно обновляйте pip и setuptools",
    ...
  ],
  "practice_exercises": [
    "Задание 1: Установите Python на свою ОС",
    "Задание 2: Проверьте версию Python и pip",
    "Задание 3: Создайте простой скрипт hello.py"
  ],
  "quiz_questions": [
    "Вопрос 1: Какая версия Python актуальна сейчас?",
    "Вопрос 2: Что такое PATH и зачем добавлять туда Python?",
    ...
  ],
  "estimated_reading_time_minutes": 25
}
```

## Использование в боте

### Команда (будет добавлена)

```
/generate_topics - Создать детальные материалы для урока
```

### Flow

1. Пользователь выбирает модуль
2. Выбирает урок из модуля
3. Бот генерирует детальный материал для **каждой темы** из `content_outline`
4. Результат сохраняется в `lesson.detailed_content`
5. Можно экспортировать в JSON/HTML/MD/TXT

## Экспорт

Детальный контент можно экспортировать:

- **JSON** - для программной обработки
- **HTML** - красивая веб-страница с навигацией
- **Markdown** - для документации
- **TXT** - простой текст

### Структура экспорта

```
Урок: Установка и настройка окружения
├── Тема 1: Установка Python
│   ├── Введение
│   ├── Теория
│   ├── Примеры
│   ├── Код
│   ├── Ключевые моменты
│   ├── Частые ошибки
│   ├── Лучшие практики
│   ├── Упражнения
│   └── Вопросы
├── Тема 2: Настройка IDE
│   └── ...
└── Тема 3: ...
```

## Производительность

- ⏱️ Генерация 1 темы: ~20-30 секунд
- ⏱️ Урок с 5 темами: ~2-3 минуты
- 💰 Стоимость: ~$0.05-0.10 за тему (GPT-4)

## Оптимизация

### Кэширование
- Сохранять сгенерированные материалы
- Не регенерировать без изменений

### Параллельность
- Можно генерировать темы параллельно
- Ускорение в 3-5 раз

### Fallback
- Тестовый контент при ошибках
- Graceful degradation

---

**Дата создания:** 19 октября 2025  
**Статус:** ✅ Реализовано (backend готов, команда в боте - следующий шаг)




