# 🐛 Исправление ошибки парсинга callback данных

## Проблема

При нажатии на кнопку "С дополнительными требованиями" для перегенерации лекции возникала ошибка:

```
ValueError: invalid literal for int() with base 10: 'custom'
```

### Причина

В функции `handle_callback()` паттерны проверялись в неправильном порядке:

```python
# НЕПРАВИЛЬНО:
elif data.startswith("regen_lecture_"):
    lecture_index = int(data.split("_")[2])  # ❌ Пытается парсить 'custom' как int
    await _show_lecture_regenerate_menu(...)

elif data.startswith("regen_lecture_full_"):
    lecture_index = int(data.split("_")[3])
    await _regenerate_lecture(...)

elif data.startswith("regen_lecture_custom_"):
    lecture_index = int(data.split("_")[3])
    # ...
```

При нажатии кнопки с callback `regen_lecture_custom_0`:
1. Проверка `data.startswith("regen_lecture_")` возвращает `True`
2. Код пытается выполнить `int("custom")` → **ValueError**
3. Более специфичные проверки никогда не выполняются

## Решение

**Правило:** Более специфичные паттерны должны проверяться **ПЕРВЫМИ**!

```python
# ПРАВИЛЬНО:
# ВАЖНО: Более специфичные паттерны должны проверяться первыми!
elif data.startswith("regen_lecture_full_"):
    lecture_index = int(data.split("_")[3])
    await _regenerate_lecture(query, user_id, lecture_index, session, None)

elif data.startswith("regen_lecture_custom_"):
    lecture_index = int(data.split("_")[3])
    session.editing_mode = True
    session.editing_path = f"regen_lecture_custom_{lecture_index}"
    # ...

elif data.startswith("regen_lecture_"):
    lecture_index = int(data.split("_")[2])
    await _show_lecture_regenerate_menu(query, user_id, lecture_index, session)
```

### Почему это работает

При callback `regen_lecture_custom_0`:
1. ✅ `data.startswith("regen_lecture_full_")` → `False`
2. ✅ `data.startswith("regen_lecture_custom_")` → `True` → обрабатывается правильно
3. ✅ Общий паттерн `regen_lecture_` не проверяется

При callback `regen_lecture_0`:
1. ✅ `data.startswith("regen_lecture_full_")` → `False`
2. ✅ `data.startswith("regen_lecture_custom_")` → `False`
3. ✅ `data.startswith("regen_lecture_")` → `True` → обрабатывается правильно

## Исправленные паттерны

### ✅ Лекции (исправлено)
```python
regen_lecture_full_     # Более специфичный (проверяется первым)
regen_lecture_custom_   # Более специфичный (проверяется вторым)
regen_lecture_          # Общий (проверяется последним)
```

### ✅ Слайды (уже было правильно)
```python
regen_slide_full_       # Более специфичный
regen_slide_custom_     # Более специфичный
regen_slide_            # Общий
```

### ✅ Уроки (уже было правильно)
```python
regen_lesson_full_      # Более специфичный
regen_lesson_custom_    # Более специфичный
regen_lesson_item_      # Более специфичный
regen_lesson_module_    # Общий
```

## Файлы изменены

- `course_bot.py` - функция `handle_callback()` (строки 374-394)

## Результат

✅ Кнопка "С дополнительными требованиями" теперь работает корректно
✅ Бот запрашивает дополнительные требования перед перегенерацией
✅ Все callback паттерны обрабатываются правильно

---

**Дата исправления:** 19 октября 2025




