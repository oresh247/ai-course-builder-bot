"""Вспомогательные функции для обработки callback"""

import logging
from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models import UserSession, Lesson, Course
from openai_client import OpenAIClient
from content_generator import ContentGenerator
from exporters import CourseExporter
from utils import format_module_content_info, format_lesson_content_info, format_module_info, format_lesson_info
from prompts import (
    LESSON_REGENERATION_SYSTEM_PROMPT,
    LESSON_REGENERATION_PROMPT_TEMPLATE,
    format_content_outline,
    format_custom_requirements
)

logger = logging.getLogger(__name__)

# Инициализируем сервисы
openai_client = OpenAIClient()
content_generator = ContentGenerator()
course_exporter = CourseExporter()


async def handle_module_edit(query, user_id: int, module_index: int, session: UserSession):
    """Показывает меню редактирования модуля"""
    course = session.current_course
    module = course.modules[module_index]
    
    text = f"✏️ <b>Редактирование модуля {module_index + 1}</b>\n\n"
    text += f"<b>Название:</b> {module.module_title}\n\n"
    text += f"<b>Цель:</b> {module.module_goal}\n\n"
    text += f"<b>Уроков:</b> {len(module.lessons)}\n\n"
    text += "Что изменить?"
    
    keyboard = [
        [InlineKeyboardButton("📝 Название модуля", callback_data=f"edit_module_name_{module_index}")],
        [InlineKeyboardButton("🎯 Цель модуля", callback_data=f"edit_module_goal_{module_index}")],
        [InlineKeyboardButton("🤖 Сгенерировать цель с AI", callback_data=f"gen_module_goal_{module_index}")],
        [InlineKeyboardButton("🔙 Назад к списку модулей", callback_data="back_to_edit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def generate_module_content(query, user_id: int, module_index: int, session: UserSession):
    """Генерирует учебный контент для модуля"""
    course = session.current_course
    module = course.modules[module_index]
    
    await query.edit_message_text(
        f"🤖 <b>Генерация контента для модуля...</b>\n\n"
        f"Модуль: {module.module_title}\n"
        f"Уроков: {len(module.lessons)}\n\n"
        f"⏳ Это может занять 30-60 секунд...",
        parse_mode="HTML"
    )
    
    module_content = content_generator.generate_module_content(
        module=module,
        course_title=course.course_title,
        target_audience=course.target_audience
    )
    
    if module_content:
        session.current_module_content = module_content
        
        text = format_module_content_info(module_content)
        
        keyboard = [
            [InlineKeyboardButton("📥 Экспорт JSON", callback_data=f"export_mcontent_json_{module_index}")],
            [InlineKeyboardButton("🌐 Экспорт HTML (презентация)", callback_data=f"export_mcontent_html_{module_index}")],
            [InlineKeyboardButton("📝 Экспорт Markdown", callback_data=f"export_mcontent_md_{module_index}")],
            [InlineKeyboardButton("📃 Экспорт TXT", callback_data=f"export_mcontent_txt_{module_index}")],
            [InlineKeyboardButton("🔄 Сгенерировать заново", callback_data=f"gen_content_{module_index}")],
            [InlineKeyboardButton("🔙 К модулям", callback_data="back_to_edit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await query.edit_message_text(
            "❌ Ошибка генерации контента. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="back_to_edit")
            ]])
        )


async def show_lecture_regenerate_menu(query, user_id: int, lecture_index: int, session: UserSession):
    """Показывает меню перегенерации лекции"""
    module_content = session.current_module_content
    lecture = module_content.lectures[lecture_index]
    
    text = f"🔄 <b>Перегенерация лекции</b>\n\n"
    text += f"📖 {lecture.lecture_title}\n"
    text += f"📊 Слайдов: {len(lecture.slides)}\n"
    text += f"⏱️ Время: {lecture.duration_minutes} минут\n\n"
    text += "Выберите действие:"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Перегенерировать всю лекцию", callback_data=f"regen_lecture_full_{lecture_index}")],
        [InlineKeyboardButton("✍️ Перегенерировать с требованиями", callback_data=f"regen_lecture_custom_{lecture_index}")],
        [InlineKeyboardButton("📊 Перегенерировать слайд", callback_data=f"select_slide_{lecture_index}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_lectures")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def show_slides_list(query, user_id: int, lecture_index: int, session: UserSession):
    """Показывает список слайдов лекции для выбора"""
    module_content = session.current_module_content
    lecture = module_content.lectures[lecture_index]
    
    text = f"📊 <b>Слайды лекции:</b> {lecture.lecture_title}\n\n"
    text += "Выберите слайд для перегенерации:\n\n"
    
    keyboard = []
    for i, slide in enumerate(lecture.slides):
        text += f"{slide.slide_number}. {slide.title} ({slide.slide_type})\n"
        keyboard.append([InlineKeyboardButton(
            f"{slide.slide_number}. {slide.title[:35]}", 
            callback_data=f"regen_slide_{lecture_index}_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"regen_lecture_{lecture_index}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def show_lessons_for_regen(query, user_id: int, module_index: int, session: UserSession):
    """Показывает список уроков модуля для перегенерации"""
    course = session.current_course
    module = course.modules[module_index]
    
    text = f"🔄 <b>Перегенерация урока</b>\n\n"
    text += f"Модуль: {module.module_title}\n\n"
    text += "Выберите урок для перегенерации:\n\n"
    
    keyboard = []
    for i, lesson in enumerate(module.lessons):
        keyboard.append([InlineKeyboardButton(
            f"📝 {i+1}. {lesson.lesson_title} ({lesson.estimated_time_minutes} мин)",
            callback_data=f"regen_lesson_item_{module_index}_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def show_lesson_regen_menu(query, user_id: int, module_index: int, lesson_index: int, session: UserSession):
    """Показывает меню перегенерации урока"""
    course = session.current_course
    module = course.modules[module_index]
    lesson = module.lessons[lesson_index]
    
    text = f"🔄 <b>Перегенерация урока</b>\n\n"
    text += f"Модуль: {module.module_title}\n"
    text += f"Урок: {lesson.lesson_title}\n"
    text += f"Формат: {lesson.format}\n"
    text += f"Длительность: {lesson.estimated_time_minutes} мин\n\n"
    text += f"<b>Текущая цель:</b>\n{lesson.lesson_goal[:200]}...\n\n"
    text += "Выберите действие:"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Перегенерировать", callback_data=f"regen_lesson_full_{module_index}_{lesson_index}")],
        [InlineKeyboardButton("✍️ С дополнительными требованиями", callback_data=f"regen_lesson_custom_{module_index}_{lesson_index}")],
        [InlineKeyboardButton("🔙 Назад к урокам", callback_data=f"regen_lesson_module_{module_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def show_module_details(query, user_id: int, module_index: int, session: UserSession):
    """Показывает детали модуля с возможностью просмотра уроков"""
    course = session.current_course
    module = course.modules[module_index]
    
    text = format_module_info(module, module.module_number)
    
    keyboard = []
    for i, lesson in enumerate(module.lessons):
        has_detailed = "📖" if lesson.detailed_content else "📝"
        
        keyboard.append([InlineKeyboardButton(
            f"{has_detailed} {i+1}. {lesson.lesson_title[:35]}",
            callback_data=f"view_lesson_{module_index}_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 К курсу", callback_data="back_to_course")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def show_lesson_details(query, user_id: int, module_index: int, lesson_index: int, session: UserSession):
    """Показывает детали урока с возможностью экспорта детальных материалов"""
    course = session.current_course
    module = course.modules[module_index]
    lesson = module.lessons[lesson_index]
    
    text = format_lesson_info(lesson, module.module_title)
    
    keyboard = []
    
    if lesson.detailed_content:
        keyboard.append([InlineKeyboardButton(
            "📥 Экспортировать детальные материалы",
            callback_data=f"export_topics_menu_{module_index}_{lesson_index}"
        )])
    else:
        keyboard.append([InlineKeyboardButton(
            "🤖 Сгенерировать детальные материалы",
            callback_data=f"gen_topics_lesson_{module_index}_{lesson_index}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 К модулю", callback_data=f"view_module_{module_index}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def show_lessons_for_topic_gen(query, user_id: int, module_index: int, session: UserSession):
    """Показывает список уроков модуля для генерации детальных материалов"""
    course = session.current_course
    module = course.modules[module_index]
    
    text = f"📖 <b>Генерация детальных материалов</b>\n\n"
    text += f"Модуль: {module.module_title}\n\n"
    text += "Выберите урок для генерации детального контента по каждому пункту плана:\n\n"
    
    keyboard = []
    for i, lesson in enumerate(module.lessons):
        content_count = len(lesson.content_outline) if lesson.content_outline else 0
        keyboard.append([InlineKeyboardButton(
            f"📝 {i+1}. {lesson.lesson_title} ({content_count} тем)",
            callback_data=f"gen_topics_lesson_{module_index}_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def generate_lesson_topics(query, user_id: int, module_index: int, lesson_index: int, session: UserSession):
    """Генерирует детальные учебные материалы для всех тем урока"""
    course = session.current_course
    module = course.modules[module_index]
    lesson = module.lessons[lesson_index]
    
    if not lesson.content_outline:
        await query.edit_message_text(
            "❌ У урока нет плана содержания (content_outline).\n"
            "Сначала перегенерируйте урок с помощью /regenerate_lesson"
        )
        return
    
    await query.edit_message_text(
        f"🤖 <b>Генерация детальных материалов...</b>\n\n"
        f"Урок: {lesson.lesson_title}\n"
        f"Тем для раскрытия: {len(lesson.content_outline)}\n\n"
        f"⏳ Это может занять несколько минут...",
        parse_mode="HTML"
    )
    
    lesson_content = content_generator.generate_lesson_detailed_content(
        lesson=lesson,
        module_number=module.module_number,
        course_title=course.course_title,
        module_title=module.module_title,
        target_audience=course.target_audience
    )
    
    if lesson_content:
        lesson.detailed_content = lesson_content
        
        text = format_lesson_content_info(lesson_content, lesson.lesson_title)
        
        keyboard = [
            [InlineKeyboardButton("📥 Экспортировать материалы", callback_data=f"export_topics_menu_{module_index}_{lesson_index}")],
            [InlineKeyboardButton("🔄 Сгенерировать заново", callback_data=f"gen_topics_lesson_{module_index}_{lesson_index}")],
            [InlineKeyboardButton("📋 Выбрать другой урок", callback_data=f"gen_topics_module_{module_index}")],
            [InlineKeyboardButton("🔙 К курсу", callback_data="back_to_course")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await query.edit_message_text(
            "❌ Ошибка генерации детальных материалов. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data=f"gen_topics_module_{module_index}")
            ]])
        )

