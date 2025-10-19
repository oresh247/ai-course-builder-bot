"""Обработчики перегенерации контента"""

import logging
from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from models import UserSession, Lesson, Slide, Lecture
from openai_client import OpenAIClient
from content_generator import ContentGenerator
from prompts import (
    LESSON_REGENERATION_SYSTEM_PROMPT,
    LESSON_REGENERATION_PROMPT_TEMPLATE,
    format_content_outline,
    format_custom_requirements
)

logger = logging.getLogger(__name__)

# Глобальные переменные для сервисов (ленивая инициализация)
_openai_client = None
_content_generator = None


def get_openai_client():
    """Получает или создаёт экземпляр OpenAIClient"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client


def get_content_generator():
    """Получает или создаёт экземпляр ContentGenerator"""
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGenerator()
    return _content_generator


async def regenerate_lesson_item(query, user_id: int, module_index: int, lesson_index: int, 
                                 session: UserSession, custom_requirements: Optional[str]):
    """Перегенерирует отдельный урок"""
    course = session.current_course
    module = course.modules[module_index]
    lesson = module.lessons[lesson_index]
    
    await query.edit_message_text(
        f"🤖 <b>Перегенерация урока...</b>\n\n"
        f"Урок: {lesson.lesson_title}\n\n"
        f"⏳ Подождите 20-30 секунд...",
        parse_mode="HTML"
    )
    
    prompt = LESSON_REGENERATION_PROMPT_TEMPLATE.format(
        course_title=course.course_title,
        target_audience=course.target_audience,
        module_title=module.module_title,
        module_goal=module.module_goal,
        lesson_title=lesson.lesson_title,
        lesson_format=lesson.format,
        lesson_duration=lesson.estimated_time_minutes,
        lesson_goal=lesson.lesson_goal,
        content_outline=format_content_outline(lesson.content_outline),
        custom_requirements=format_custom_requirements(custom_requirements)
    )

    try:
        openai_client = get_openai_client()
        content_generator = get_content_generator()
        
        response = openai_client.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": LESSON_REGENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        json_content = content_generator._extract_lesson_json(content)
        
        if json_content:
            module.lessons[lesson_index] = Lesson(**json_content)
            
            text = f"✅ <b>Урок перегенерирован!</b>\n\n"
            text += f"<b>Название:</b> {json_content['lesson_title']}\n"
            text += f"<b>Формат:</b> {json_content['format']}\n"
            text += f"<b>Длительность:</b> {json_content['estimated_time_minutes']} мин\n\n"
            text += f"<b>Новая цель:</b>\n{json_content['lesson_goal']}\n\n"
            text += f"<b>План контента:</b>\n"
            for item in json_content['content_outline'][:5]:
                text += f"• {item}\n"
            
            keyboard = [
                [InlineKeyboardButton("👁️ К урокам модуля", callback_data=f"regen_lesson_module_{module_index}")],
                [InlineKeyboardButton("🔄 Перегенерировать заново", callback_data=f"regen_lesson_full_{module_index}_{lesson_index}")],
                [InlineKeyboardButton("📥 Экспортировать курс", callback_data="export_json")],
                [InlineKeyboardButton("✏️ Редактировать курс", callback_data="back_to_edit")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ Ошибка перегенерации урока")
            
    except Exception as e:
        logger.error(f"Ошибка перегенерации урока: {e}")
        await query.edit_message_text(f"❌ Ошибка: {e}")


async def show_slide_regenerate_menu(query, user_id: int, lecture_index: int, slide_index: int, session: UserSession):
    """Показывает меню перегенерации слайда"""
    module_content = session.current_module_content
    lecture = module_content.lectures[lecture_index]
    slide = lecture.slides[slide_index]
    
    text = f"🔄 <b>Перегенерация слайда</b>\n\n"
    text += f"Лекция: {lecture.lecture_title}\n"
    text += f"Слайд #{slide.slide_number}: {slide.title}\n"
    text += f"Тип: {slide.slide_type}\n\n"
    text += f"<b>Текущий контент:</b>\n{slide.content[:200]}...\n\n"
    text += "Выберите действие:"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Перегенерировать", callback_data=f"regen_slide_full_{lecture_index}_{slide_index}")],
        [InlineKeyboardButton("✍️ С дополнительными требованиями", callback_data=f"regen_slide_custom_{lecture_index}_{slide_index}")],
        [InlineKeyboardButton("🔙 Назад к лекции", callback_data=f"regen_lecture_{lecture_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def regenerate_lecture(query, user_id: int, lecture_index: int, session: UserSession, custom_requirements: Optional[str]):
    """Перегенерирует лекцию"""
    module_content = session.current_module_content
    lecture = module_content.lectures[lecture_index]
    course = session.current_course
    
    await query.edit_message_text(
        f"🤖 <b>Перегенерация лекции...</b>\n\n"
        f"Лекция: {lecture.lecture_title}\n\n"
        f"⏳ Это может занять 30-60 секунд...",
        parse_mode="HTML"
    )
    
    prompt = f"""Перегенерируй ДЕТАЛЬНУЮ лекцию для IT-курса в формате слайдов.

КУРС: {course.course_title}
АУДИТОРИЯ: {course.target_audience}
МОДУЛЬ: {module_content.module_title}
ЛЕКЦИЯ: {lecture.lecture_title}
ТЕКУЩЕЕ КОЛИЧЕСТВО СЛАЙДОВ: {len(lecture.slides)}

"""
    
    if custom_requirements:
        prompt += f"ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ:\n{custom_requirements}\n\n"
    
    prompt += f"""ЗАДАЧА: Создай улучшенную версию лекции с 8-12 слайдами.

ТИПЫ СЛАЙДОВ:
- title: Заглавный
- content: Теория (3-5 пунктов)
- code: Примеры кода
- diagram: Схемы (описание)
- quiz: Вопросы
- summary: Итоги

ФОРМАТ ОТВЕТА: строго JSON
{{
  "lecture_title": "{lecture.lecture_title}",
  "module_number": {module_content.module_number},
  "module_title": "{module_content.module_title}",
  "duration_minutes": 45,
  "learning_objectives": ["цель 1", "цель 2"],
  "key_takeaways": ["вывод 1", "вывод 2"],
  "slides": [
    {{
      "slide_number": 1,
      "title": "...",
      "content": "...",
      "slide_type": "title",
      "code_example": null,
      "notes": "заметки"
    }}
  ]
}}"""

    try:
        openai_client = get_openai_client()
        content_generator = get_content_generator()
        
        response = openai_client.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — эксперт по созданию образовательного контента. Создаёшь детальные лекции со слайдами. Отвечаешь строго в JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        json_content = content_generator._extract_json(content)
        
        if json_content:
            module_content.lectures[lecture_index] = Lecture(**json_content)
            
            text = f"✅ <b>Лекция перегенерирована!</b>\n\n"
            text += f"📖 {lecture.lecture_title}\n"
            text += f"📊 Слайдов: {len(json_content['slides'])}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("👁️ Просмотреть слайды", callback_data=f"view_slides_{lecture_index}")],
                [InlineKeyboardButton("🔄 Перегенерировать заново", callback_data=f"regen_lecture_full_{lecture_index}")],
                [InlineKeyboardButton("📥 Экспортировать", callback_data=f"export_lecture_{lecture_index}")],
                [InlineKeyboardButton("🔙 К лекциям", callback_data="back_to_lectures")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ Ошибка перегенерации. Попробуйте позже.")
            
    except Exception as e:
        logger.error(f"Ошибка перегенерации лекции: {e}")
        await query.edit_message_text(f"❌ Ошибка: {e}")


async def regenerate_slide(query, user_id: int, lecture_index: int, slide_index: int, 
                           session: UserSession, custom_requirements: Optional[str]):
    """Перегенерирует отдельный слайд"""
    module_content = session.current_module_content
    lecture = module_content.lectures[lecture_index]
    slide = lecture.slides[slide_index]
    course = session.current_course
    
    await query.edit_message_text(
        f"🤖 <b>Перегенерация слайда...</b>\n\n"
        f"Слайд #{slide.slide_number}: {slide.title}\n\n"
        f"⏳ Подождите немного...",
        parse_mode="HTML"
    )
    
    prompt = f"""Перегенерируй ОДИН слайд для IT-лекции.

КОНТЕКСТ:
Курс: {course.course_title}
Аудитория: {course.target_audience}
Модуль: {module_content.module_title}
Лекция: {lecture.lecture_title}
Слайд #{slide.slide_number}: {slide.title}
Текущий тип: {slide.slide_type}

ТЕКУЩИЙ КОНТЕНТ СЛАЙДА:
{slide.content}
"""
    
    if custom_requirements:
        prompt += f"\nДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ:\n{custom_requirements}\n"
    
    prompt += f"""
ЗАДАЧА: Создай улучшенную версию этого слайда.

ТИПЫ СЛАЙДОВ:
- title: Заглавный
- content: Теория (3-5 пунктов)
- code: Примеры кода (обязательно добавь code_example)
- diagram: Схемы (описание визуализации)
- quiz: Вопросы для проверки
- summary: Итоги

ФОРМАТ ОТВЕТА: строго JSON
{{
  "slide_number": {slide.slide_number},
  "title": "заголовок слайда",
  "content": "содержание слайда (3-5 пунктов через \\n)",
  "slide_type": "{slide.slide_type}",
  "code_example": "код если нужен или null",
  "notes": "заметки для преподавателя"
}}

ВАЖНО: Верни ТОЛЬКО JSON, без комментариев!"""

    try:
        openai_client = get_openai_client()
        content_generator = get_content_generator()
        
        response = openai_client.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — эксперт по созданию образовательных слайдов. Отвечаешь строго в JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        content = response.choices[0].message.content.strip()
        json_content = content_generator._extract_json(content)
        
        if json_content:
            lecture.slides[slide_index] = Slide(**json_content)
            
            text = f"✅ <b>Слайд перегенерирован!</b>\n\n"
            text += f"Слайд #{json_content['slide_number']}: {json_content['title']}\n"
            text += f"Тип: {json_content['slide_type']}\n\n"
            text += f"<b>Новый контент:</b>\n{json_content['content'][:200]}...\n\n"
            
            keyboard = [
                [InlineKeyboardButton("👁️ К списку слайдов", callback_data=f"select_slide_{lecture_index}")],
                [InlineKeyboardButton("🔄 Перегенерировать заново", callback_data=f"regen_slide_full_{lecture_index}_{slide_index}")],
                [InlineKeyboardButton("📥 Экспортировать лекцию", callback_data=f"export_mcontent_html_0")],
                [InlineKeyboardButton("🔙 К лекциям", callback_data="back_to_lectures")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ Ошибка перегенерации слайда")
            
    except Exception as e:
        logger.error(f"Ошибка перегенерации слайда: {e}")
        await query.edit_message_text(f"❌ Ошибка: {e}")


async def generate_module_goal(query, user_id: int, module_index: int, session: UserSession):
    """Генерирует цель модуля с помощью AI"""
    course = session.current_course
    module = course.modules[module_index]
    
    await query.edit_message_text("🤖 Генерирую цель модуля с помощью AI...")
    
    prompt = f"""Создай педагогически корректную цель для модуля IT-курса.

Название курса: {course.course_title}
Уровень: {course.target_audience}
Название модуля: {module.module_title}

Требования к цели:
- Конкретная и измеримая
- Соответствует таксономии Блума
- Формулировка от 1-2 предложений
- На русском языке

Верни ТОЛЬКО текст цели, без дополнительных пояснений."""

    try:
        openai_client = get_openai_client()
        
        response = openai_client.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — эксперт по педагогическому дизайну IT-курсов."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        new_goal = response.choices[0].message.content.strip()
        module.module_goal = new_goal
        
        text = f"✅ <b>Цель модуля обновлена!</b>\n\n"
        text += f"<b>Модуль:</b> {module.module_title}\n\n"
        text += f"<b>Новая цель:</b> {new_goal}\n\n"
        text += "Что дальше?"
        
        keyboard = [
            [InlineKeyboardButton("✏️ Редактировать вручную", callback_data=f"edit_module_goal_{module_index}")],
            [InlineKeyboardButton("🔄 Сгенерировать заново", callback_data=f"gen_module_goal_{module_index}")],
            [InlineKeyboardButton("🔙 Назад к модулю", callback_data=f"edit_mod_{module_index}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка генерации цели: {e}")
        await query.edit_message_text(
            f"❌ Ошибка генерации цели: {e}\n\nПопробуйте редактировать вручную.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data=f"edit_mod_{module_index}")
            ]])
        )

