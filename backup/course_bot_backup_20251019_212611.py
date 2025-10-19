# ---------- SSL FIX для корпоративных сетей ----------
import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# ----------------------------------------------------

import logging
import json
from typing import Optional
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import httpx

from models import Course, Module, Lesson, UserSession, DifficultyLevel, ModuleContent, Lecture, Slide
from openai_client import OpenAIClient
from exporters import CourseExporter
from content_generator import ContentGenerator
from prompts import (
    LESSON_REGENERATION_SYSTEM_PROMPT,
    LESSON_REGENERATION_PROMPT_TEMPLATE,
    LECTURE_REGENERATION_SYSTEM_PROMPT,
    LECTURE_REGENERATION_PROMPT_TEMPLATE,
    SLIDE_REGENERATION_SYSTEM_PROMPT,
    SLIDE_REGENERATION_PROMPT_TEMPLATE,
    format_content_outline,
    format_custom_requirements
)

# ---------- ЗАГРУЗКА ----------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ---------- ЛОГИРОВАНИЕ ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- ХРАНИЛИЩЕ СЕССИЙ ----------
user_sessions = {}

# ---------- ИНИЦИАЛИЗАЦИЯ ----------
openai_client = OpenAIClient()
course_exporter = CourseExporter()
content_generator = ContentGenerator()


# ---------- ОБРАБОТЧИКИ КОМАНД ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id=user_id)
    
    logger.info(f"/start от {update.effective_user.first_name}")
    await update.message.reply_text(
        "🤖 <b>AI Course Builder</b>\n\n"
        "Привет! Я помогу создать структуру IT-курса с помощью ИИ.\n\n"
        "<b>Основные команды:</b>\n"
        "/create - создать новый курс\n"
        "/view - просмотреть курс\n"
        "/edit - редактировать модули\n\n"
        "<b>Генерация контента:</b>\n"
        "/generate - создать лекции и слайды\n"
        "/regenerate - перегенерировать лекции/слайды\n"
        "/regenerate_lesson - перегенерировать уроки\n"
        "/generate_topics - детальные материалы по темам\n\n"
        "<b>Экспорт:</b>\n"
        "/export - экспортировать курс (JSON/HTML/MD/TXT)\n\n"
        "/help - подробная справка",
        parse_mode="HTML"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    await update.message.reply_text(
        "📚 <b>Справка по командам</b>\n\n"
        "<b>/create</b> - Создать новый курс\n"
        "Бот попросит указать:\n"
        "• Тему курса\n"
        "• Уровень (junior/middle/senior)\n"
        "• Количество модулей (3-10)\n"
        "• Длительность\n\n"
        "<b>/view</b> - Просмотреть структуру курса\n\n"
        "<b>/edit</b> - Редактировать:\n"
        "• Название и описание\n"
        "• Модули и уроки\n"
        "• Цели и оценки\n\n"
        "<b>/generate</b> - Сгенерировать детальный контент (лекции, слайды)\n\n"
        "<b>/regenerate</b> - Перегенерировать лекции и слайды\n\n"
        "<b>/regenerate_lesson</b> - Перегенерировать отдельный урок модуля\n\n"
        "<b>/generate_topics</b> - Сгенерировать детальные учебные материалы по каждому пункту плана урока\n\n"
        "<b>/export</b> - Экспортировать в JSON/HTML/Markdown/TXT\n\n"
        "<b>Пример:</b>\n"
        "Создай курс по Python для junior",
        parse_mode="HTML"
    )


async def create_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания курса"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id=user_id)
    
    session = user_sessions[user_id]
    session.editing_mode = True
    session.editing_path = "awaiting_level"
    
    keyboard = [
        [InlineKeyboardButton("Junior", callback_data="level_junior")],
        [InlineKeyboardButton("Middle", callback_data="level_middle")],
        [InlineKeyboardButton("Senior", callback_data="level_senior")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 <b>Создание курса</b>\n\nВыберите уровень аудитории:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def view_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр курса"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].current_course:
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
    course = user_sessions[user_id].current_course
    text = f"🎓 <b>{course.course_title}</b>\n\n"
    text += f"👥 <b>Аудитория:</b> {course.target_audience}\n"
    
    if course.duration_weeks:
        text += f"⏱️ <b>Длительность:</b> {course.duration_weeks} недель\n"
    if course.duration_hours:
        text += f"📚 <b>Часов:</b> {course.duration_hours}\n"
    
    text += f"\n<b>Модули ({len(course.modules)}):</b>\n\n"
    
    keyboard = []
    for i, module in enumerate(course.modules, 1):
        text += f"<b>{i}. {module.module_title}</b>\n"
        text += f"<i>{module.module_goal}</i>\n"
        text += f"Уроков: {len(module.lessons)}\n\n"
        
        # Добавляем кнопку для просмотра деталей модуля
        keyboard.append([InlineKeyboardButton(
            f"👁️ {i}. Детали модуля: {module.module_title[:30]}",
            callback_data=f"view_module_{i-1}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def edit_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Редактирование курса"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].current_course:
        await update.message.reply_text("❌ У вас нет курса для редактирования. Используйте /create")
        return
    
    course = user_sessions[user_id].current_course
    
    # Показываем меню редактирования модулей
    text = f"✏️ <b>Редактирование курса:</b> {course.course_title}\n\n"
    text += "Выберите модуль для редактирования:\n\n"
    
    keyboard = []
    for i, module in enumerate(course.modules):
        text += f"{i+1}. {module.module_title}\n"
        keyboard.append([InlineKeyboardButton(
            f"{i+1}. {module.module_title[:40]}", 
            callback_data=f"edit_mod_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад к курсу", callback_data="back_to_course")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def generate_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация контента для модуля"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].current_course:
        await update.message.reply_text("❌ У вас нет курса. Сначала создайте курс с помощью /create")
        return
    
    course = user_sessions[user_id].current_course
    
    # Показываем список модулей для генерации контента
    text = f"📝 <b>Генерация учебного контента</b>\n\n"
    text += f"Курс: {course.course_title}\n\n"
    text += "Выберите модуль для генерации лекций и слайдов:\n\n"
    
    keyboard = []
    for i, module in enumerate(course.modules):
        text += f"{i+1}. {module.module_title}\n"
        keyboard.append([InlineKeyboardButton(
            f"📚 {i+1}. {module.module_title[:35]}", 
            callback_data=f"gen_content_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def regenerate_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перегенерация лекций и слайдов"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].current_module_content:
        await update.message.reply_text(
            "❌ У вас нет сгенерированного контента.\n"
            "Сначала используйте /generate для создания контента модуля"
        )
        return
    
    module_content = user_sessions[user_id].current_module_content
    
    # Показываем список лекций для перегенерации
    text = f"🔄 <b>Перегенерация контента</b>\n\n"
    text += f"Модуль: {module_content.module_title}\n\n"
    text += "Выберите что перегенерировать:\n\n"
    
    keyboard = []
    
    # Добавляем лекции
    for i, lecture in enumerate(module_content.lectures):
        text += f"📖 {i+1}. {lecture.lecture_title} ({len(lecture.slides)} слайдов)\n"
        keyboard.append([InlineKeyboardButton(
            f"📖 {i+1}. {lecture.lecture_title[:30]}", 
            callback_data=f"regen_lecture_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def regenerate_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перегенерация отдельного урока из модуля курса"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].current_course:
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
    session = user_sessions[user_id]
    course = session.current_course
    
    text = f"🔄 <b>Перегенерация урока</b>\n\n"
    text += f"Курс: {course.course_title}\n\n"
    text += "Выберите модуль:\n\n"
    
    keyboard = []
    for i, module in enumerate(course.modules):
        keyboard.append([InlineKeyboardButton(
            f"📦 {module.module_title} ({len(module.lessons)} уроков)",
            callback_data=f"regen_lesson_module_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def generate_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация детальных учебных материалов по плану содержания урока"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].current_course:
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
    session = user_sessions[user_id]
    course = session.current_course
    
    text = f"📖 <b>Генерация детальных материалов</b>\n\n"
    text += f"Курс: {course.course_title}\n\n"
    text += "Выберите модуль для генерации детального контента:\n\n"
    
    keyboard = []
    for i, module in enumerate(course.modules):
        keyboard.append([InlineKeyboardButton(
            f"📚 {module.module_title} ({len(module.lessons)} уроков)",
            callback_data=f"gen_topics_module_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def export_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экспорт курса - выбор формата"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].current_course:
        await update.message.reply_text("❌ У вас нет курса для экспорта")
        return
    
    # Показываем меню выбора формата
    keyboard = [
        [InlineKeyboardButton("📄 JSON - для программ", callback_data="export_json")],
        [InlineKeyboardButton("🌐 HTML - красивая веб-страница", callback_data="export_html")],
        [InlineKeyboardButton("📝 Markdown - для редакторов", callback_data="export_md")],
        [InlineKeyboardButton("📃 TXT - простой текст", callback_data="export_txt")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📦 <b>Выберите формат экспорта:</b>\n\n"
        "• <b>JSON</b> - для импорта в другие программы\n"
        "• <b>HTML</b> - красивая веб-страница для просмотра\n"
        "• <b>Markdown</b> - для редактирования в Notion, Obsidian\n"
        "• <b>TXT</b> - простой текстовый файл",
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def handle_callback(query_update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = query_update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_sessions:
        await query.edit_message_text("❌ Сессия истекла. Используйте /start")
        return
    
    session = user_sessions[user_id]
    
    # Обработка выбора уровня
    if data.startswith("level_"):
        level = data.split("_")[1]
        if not hasattr(session, 'temp_data'):
            session.temp_data = {}
        session.temp_data['level'] = level
        session.editing_path = "awaiting_topic"
        
        await query.edit_message_text(
            f"✅ Уровень: <b>{level.title()}</b>\n\n"
            "Введите тему курса (например: 'Python для веб-разработки'):",
            parse_mode="HTML"
        )
    
    # Обработка выбора количества модулей
    elif data.startswith("modules_"):
        module_count = int(data.split("_")[1])
        session.temp_data['module_count'] = module_count
        session.editing_path = "awaiting_weeks"
        
        await query.edit_message_text(
            f"📚 Модулей: <b>{module_count}</b>\n\n"
            "Введите длительность курса в неделях (например: 6):",
            parse_mode="HTML"
        )
    
    # Обработка редактирования модулей
    elif data.startswith("edit_mod_"):
        module_index = int(data.split("_")[2])
        await _handle_module_edit(query, user_id, module_index, session)
    
    elif data.startswith("edit_module_name_"):
        module_index = int(data.split("_")[3])
        session.editing_mode = True
        session.editing_path = f"edit_module_name_{module_index}"
        await query.edit_message_text("✏️ Введите новое название модуля:")
    
    elif data.startswith("edit_module_goal_"):
        module_index = int(data.split("_")[3])
        session.editing_mode = True
        session.editing_path = f"edit_module_goal_{module_index}"
        await query.edit_message_text("✏️ Введите новую цель модуля:")
    
    elif data.startswith("gen_module_goal_"):
        module_index = int(data.split("_")[3])
        await _generate_module_goal(query, user_id, module_index, session)
    
    elif data.startswith("gen_content_"):
        module_index = int(data.split("_")[2])
        await _generate_module_content(query, user_id, module_index, session)
    
    # ВАЖНО: Более специфичные паттерны должны проверяться первыми!
    elif data.startswith("regen_lecture_full_"):
        lecture_index = int(data.split("_")[3])
        await _regenerate_lecture(query, user_id, lecture_index, session, None)
    
    elif data.startswith("regen_lecture_custom_"):
        lecture_index = int(data.split("_")[3])
        session.editing_mode = True
        session.editing_path = f"regen_lecture_custom_{lecture_index}"
        await query.edit_message_text(
            "✍️ Введите дополнительные требования к лекции:\n\n"
            "Например:\n"
            "• Добавить больше практических примеров\n"
            "• Упростить для начинающих\n"
            "• Добавить сравнение с другими технологиями\n"
            "• Больше визуальных схем"
        )
    
    elif data.startswith("regen_lecture_"):
        lecture_index = int(data.split("_")[2])
        await _show_lecture_regenerate_menu(query, user_id, lecture_index, session)
    
    elif data.startswith("select_slide_"):
        lecture_index = int(data.split("_")[2])
        await _show_slides_list(query, user_id, lecture_index, session)
    
    elif data.startswith("regen_slide_full_"):
        parts = data.split("_")
        lecture_index = int(parts[3])
        slide_index = int(parts[4])
        await _regenerate_slide(query, user_id, lecture_index, slide_index, session, None)
    
    elif data.startswith("start_regen_slide_"):
        parts = data.split("_")
        lecture_index = int(parts[3])
        slide_index = int(parts[4])
        custom_req = session.temp_data.get('custom_req')
        await _regenerate_slide(query, user_id, lecture_index, slide_index, session, custom_req)
    
    elif data.startswith("start_regen_lecture_"):
        lecture_index = int(data.split("_")[3])
        custom_req = session.temp_data.get('custom_req')
        await _regenerate_lecture(query, user_id, lecture_index, session, custom_req)
    
    elif data.startswith("regen_slide_custom_"):
        parts = data.split("_")
        lecture_index = int(parts[3])
        slide_index = int(parts[4])
        session.editing_mode = True
        session.editing_path = f"regen_slide_custom_{lecture_index}_{slide_index}"
        await query.edit_message_text(
            "✍️ Введите дополнительные требования к слайду:\n\n"
            "Например:\n"
            "• Добавить пример кода\n"
            "• Упростить формулировки\n"
            "• Добавить визуальное описание\n"
            "• Больше деталей и пояснений"
        )
    
    elif data.startswith("regen_slide_"):
        parts = data.split("_")
        lecture_index = int(parts[2])
        slide_index = int(parts[3])
        await _show_slide_regenerate_menu(query, user_id, lecture_index, slide_index, session)
    
    elif data.startswith("regen_lesson_module_"):
        module_index = int(data.split("_")[3])
        await _show_lessons_for_regen(query, user_id, module_index, session)
    
    elif data.startswith("view_module_"):
        module_index = int(data.split("_")[2])
        await _show_module_details(query, user_id, module_index, session)
    
    elif data.startswith("view_lesson_"):
        parts = data.split("_")
        module_index = int(parts[2])
        lesson_index = int(parts[3])
        await _show_lesson_details(query, user_id, module_index, lesson_index, session)
    
    elif data.startswith("gen_topics_module_"):
        module_index = int(data.split("_")[3])
        await _show_lessons_for_topic_gen(query, user_id, module_index, session)
    
    elif data.startswith("gen_topics_lesson_"):
        parts = data.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        await _generate_lesson_topics(query, user_id, module_index, lesson_index, session)
    
    elif data.startswith("regen_lesson_item_"):
        parts = data.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        await _show_lesson_regen_menu(query, user_id, module_index, lesson_index, session)
    
    elif data.startswith("regen_lesson_full_"):
        parts = data.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        await _regenerate_lesson_item(query, user_id, module_index, lesson_index, session, None)
    
    elif data.startswith("regen_lesson_custom_"):
        parts = data.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        session.editing_mode = True
        session.editing_path = f"regen_lesson_custom_{module_index}_{lesson_index}"
        await query.edit_message_text(
            "✍️ Введите дополнительные требования к уроку:\n\n"
            "Например:\n"
            "• Добавить практические примеры\n"
            "• Упростить для новичков\n"
            "• Больше теории\n"
            "• Добавить домашнее задание"
        )
    
    elif data.startswith("start_regen_lesson_item_"):
        parts = data.split("_")
        module_index = int(parts[4])
        lesson_index = int(parts[5])
        custom_req = session.temp_data.get('custom_req')
        await _regenerate_lesson_item(query, user_id, module_index, lesson_index, session, custom_req)
    
    elif data == "back_to_lectures":
        # Возврат к списку лекций
        module_content = session.current_module_content
        text = f"🔄 <b>Перегенерация контента</b>\n\n"
        text += f"Модуль: {module_content.module_title}\n\n"
        text += "Выберите лекцию:\n\n"
        
        keyboard = []
        for i, lecture in enumerate(module_content.lectures):
            text += f"📖 {i+1}. {lecture.lecture_title}\n"
            keyboard.append([InlineKeyboardButton(
                f"📖 {i+1}. {lecture.lecture_title[:30]}", 
                callback_data=f"regen_lecture_{i}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
    
    elif data == "back_to_edit":
        # Возвращаемся к списку модулей
        course = session.current_course
        text = f"✏️ <b>Редактирование курса:</b> {course.course_title}\n\n"
        text += "Выберите модуль для редактирования:\n\n"
        
        keyboard = []
        for i, module in enumerate(course.modules):
            text += f"{i+1}. {module.module_title}\n"
            keyboard.append([InlineKeyboardButton(
                f"{i+1}. {module.module_title[:40]}", 
                callback_data=f"edit_mod_{i}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад к курсу", callback_data="back_to_course")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
    
    elif data == "export_now":
        # Показываем меню выбора формата экспорта
        keyboard = [
            [InlineKeyboardButton("📄 JSON", callback_data="export_json")],
            [InlineKeyboardButton("🌐 HTML", callback_data="export_html")],
            [InlineKeyboardButton("📝 Markdown", callback_data="export_md")],
            [InlineKeyboardButton("📃 TXT", callback_data="export_txt")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📦 <b>Выберите формат экспорта:</b>",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    
    elif data.startswith("export_mcontent_"):
        # Экспорт контента модуля
        parts = data.split("_")
        export_format = parts[2]  # json, html, md, txt
        module_index = int(parts[3])
        
        module_content = session.current_module_content
        
        if not module_content:
            await query.answer("❌ Контент не сгенерирован!")
            return
        
        await query.answer("🔄 Создаю файл...")
        
        if export_format == "json":
            content_str = course_exporter.export_module_content_to_json(module_content)
            filename = f"{module_content.module_title.replace(' ', '_')}_lectures.json"
            caption = "📄 Контент модуля в JSON"
        
        elif export_format == "html":
            content_str = course_exporter.export_module_content_to_html(module_content)
            filename = f"{module_content.module_title.replace(' ', '_')}_lectures.html"
            caption = "🌐 Презентация лекций - откройте в браузере"
        
        elif export_format == "md":
            content_str = course_exporter.export_module_content_to_markdown(module_content)
            filename = f"{module_content.module_title.replace(' ', '_')}_lectures.md"
            caption = "📝 Лекции в Markdown"
        
        elif export_format == "txt":
            content_str = course_exporter.export_module_content_to_txt(module_content)
            filename = f"{module_content.module_title.replace(' ', '_')}_lectures.txt"
            caption = "📃 Лекции в TXT"
        
        # Отправляем файл
        await query.message.reply_document(
            document=content_str.encode('utf-8'),
            filename=filename,
            caption=f"{caption}\n\nЛекций: {len(module_content.lectures)} • Слайдов: {module_content.total_slides}"
        )
        
        await query.answer("✅ Файл отправлен!")
    
    elif data.startswith("export_topics_menu_"):
        # Показываем меню выбора формата для экспорта детальных материалов
        parts = data.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        
        course = session.current_course
        module = course.modules[module_index]
        lesson = module.lessons[lesson_index]
        
        if not lesson.detailed_content:
            await query.answer("❌ Детальный контент не сгенерирован!")
            return
        
        keyboard = [
            [InlineKeyboardButton("📄 JSON - для программ", callback_data=f"export_topics_json_{module_index}_{lesson_index}")],
            [InlineKeyboardButton("🌐 HTML - красивая страница", callback_data=f"export_topics_html_{module_index}_{lesson_index}")],
            [InlineKeyboardButton("📝 Markdown - для редакторов", callback_data=f"export_topics_md_{module_index}_{lesson_index}")],
            [InlineKeyboardButton("📃 TXT - простой текст", callback_data=f"export_topics_txt_{module_index}_{lesson_index}")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"gen_topics_module_{module_index}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📦 <b>Выберите формат экспорта детальных материалов</b>\n\n"
            f"Урок: {lesson.lesson_title}\n"
            f"Тем: {len(lesson.detailed_content.topics)}\n"
            f"Время изучения: ~{lesson.detailed_content.total_estimated_time_minutes} мин\n\n"
            f"• <b>JSON</b> - для импорта в другие программы\n"
            f"• <b>HTML</b> - красивая веб-страница для изучения\n"
            f"• <b>Markdown</b> - для редактирования в Notion, Obsidian\n"
            f"• <b>TXT</b> - простой текстовый файл",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    
    elif data.startswith("export_topics_"):
        # Экспорт детальных материалов урока в выбранном формате
        parts = data.split("_")
        export_format = parts[2]  # json, html, md, txt
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        
        course = session.current_course
        module = course.modules[module_index]
        lesson = module.lessons[lesson_index]
        
        if not lesson.detailed_content:
            await query.answer("❌ Детальный контент не сгенерирован!")
            return
        
        await query.answer("🔄 Создаю файл...")
        
        # Экспортируем в выбранный формат
        if export_format == "json":
            content_str = course_exporter.export_lesson_content_to_json(lesson.detailed_content)
            filename = f"{lesson.lesson_title.replace(' ', '_')}_detailed.json"
            caption = "📄 Детальные материалы в JSON"
        
        elif export_format == "html":
            content_str = course_exporter.export_lesson_content_to_html(lesson.detailed_content)
            filename = f"{lesson.lesson_title.replace(' ', '_')}_detailed.html"
            caption = "🌐 Детальные материалы - откройте в браузере"
        
        elif export_format == "md":
            content_str = course_exporter.export_lesson_content_to_markdown(lesson.detailed_content)
            filename = f"{lesson.lesson_title.replace(' ', '_')}_detailed.md"
            caption = "📝 Детальные материалы в Markdown"
        
        elif export_format == "txt":
            content_str = course_exporter.export_lesson_content_to_txt(lesson.detailed_content)
            filename = f"{lesson.lesson_title.replace(' ', '_')}_detailed.txt"
            caption = "📃 Детальные материалы в TXT"
        
        # Отправляем файл
        await query.message.reply_document(
            document=content_str.encode('utf-8'),
            filename=filename,
            caption=f"{caption}\n\nТем: {len(lesson.detailed_content.topics)} | ~{lesson.detailed_content.total_estimated_time_minutes} минут"
        )
        
        await query.edit_message_text(
            f"✅ <b>Файл отправлен!</b>\n\n"
            f"Формат: {export_format.upper()}\n"
            f"Файл: {filename}",
            parse_mode="HTML"
        )
        
        await query.answer("✅ Материалы отправлены!")
    
    elif data.startswith("export_"):
        # Обработка экспорта курса в разных форматах
        export_format = data.split("_")[1]
        course = session.current_course
        
        await query.answer("🔄 Генерирую файл...")
        
        if export_format == "json":
            content = course_exporter.export_to_json(course)
            filename = f"{course.course_title.replace(' ', '_')}.json"
            caption = "📄 Курс в JSON формате"
        
        elif export_format == "html":
            content = course_exporter.export_to_html(course)
            filename = f"{course.course_title.replace(' ', '_')}.html"
            caption = "🌐 Курс в HTML формате - откройте в браузере"
        
        elif export_format == "md":
            content = course_exporter.export_to_markdown(course)
            filename = f"{course.course_title.replace(' ', '_')}.md"
            caption = "📝 Курс в Markdown формате"
        
        elif export_format == "txt":
            content = course_exporter.export_to_txt(course)
            filename = f"{course.course_title.replace(' ', '_')}.txt"
            caption = "📃 Курс в TXT формате"
        
        # Отправляем файл
        await query.message.reply_document(
            document=content.encode('utf-8'),
            filename=filename,
            caption=caption
        )
        
        await query.edit_message_text(
            f"✅ <b>Файл отправлен!</b>\n\n"
            f"Формат: {export_format.upper()}\n"
            f"Файл: {filename}",
            parse_mode="HTML"
        )
    
    elif data == "back_to_course":
        course = session.current_course
        text = f"🎓 <b>{course.course_title}</b>\n\n"
        text += f"👥 <b>Аудитория:</b> {course.target_audience}\n"
        if course.duration_weeks:
            text += f"⏱️ <b>Длительность:</b> {course.duration_weeks} недель\n"
        text += f"\n📚 <b>Модулей:</b> {len(course.modules)}\n\n"
        text += "Используйте:\n/view - просмотр\n/edit - редактирование\n/export - экспорт"
        await query.edit_message_text(text, parse_mode="HTML")


async def _handle_module_edit(query, user_id: int, module_index: int, session: UserSession):
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


async def _generate_module_content(query, user_id: int, module_index: int, session: UserSession):
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
    
    # Генерируем контент
    module_content = content_generator.generate_module_content(
        module=module,
        course_title=course.course_title,
        target_audience=course.target_audience
    )
    
    if module_content:
        # Сохраняем контент в сессию
        session.current_module_content = module_content
        
        text = f"✅ <b>Контент модуля сгенерирован!</b>\n\n"
        text += f"📚 <b>Модуль:</b> {module_content.module_title}\n"
        text += f"📖 <b>Лекций:</b> {len(module_content.lectures)}\n"
        text += f"📊 <b>Слайдов:</b> {module_content.total_slides}\n"
        text += f"⏱️ <b>Время:</b> {module_content.estimated_duration_minutes} минут\n\n"
        
        # Краткий обзор лекций
        for i, lecture in enumerate(module_content.lectures, 1):
            text += f"{i}. {lecture.lecture_title} ({len(lecture.slides)} слайдов)\n"
        
        text += "\n<b>Что дальше?</b>"
        
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


async def _show_lecture_regenerate_menu(query, user_id: int, lecture_index: int, session: UserSession):
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


async def _show_slides_list(query, user_id: int, lecture_index: int, session: UserSession):
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


async def _show_lessons_for_regen(query, user_id: int, module_index: int, session: UserSession):
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


async def _show_lesson_regen_menu(query, user_id: int, module_index: int, lesson_index: int, session: UserSession):
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


async def _regenerate_lesson_item(query, user_id: int, module_index: int, lesson_index: int, session: UserSession, custom_requirements: Optional[str]):
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
    
    # Формируем промпт для перегенерации урока используя шаблон
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
            # Обновляем урок
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


async def _show_slide_regenerate_menu(query, user_id: int, lecture_index: int, slide_index: int, session: UserSession):
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


async def _regenerate_lecture(query, user_id: int, lecture_index: int, session: UserSession, custom_requirements: Optional[str]):
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
    
    # Формируем промпт
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
            # Обновляем лекцию
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


async def _regenerate_slide(query, user_id: int, lecture_index: int, slide_index: int, session: UserSession, custom_requirements: Optional[str]):
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
    
    # Формируем промпт для перегенерации слайда
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
            # Обновляем слайд
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


async def _generate_module_goal(query, user_id: int, module_index: int, session: UserSession):
    """Генерирует цель модуля с помощью AI"""
    course = session.current_course
    module = course.modules[module_index]
    
    await query.edit_message_text("🤖 Генерирую цель модуля с помощью AI...")
    
    # Формируем промпт для генерации цели
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


async def _show_module_details(query, user_id: int, module_index: int, session: UserSession):
    """Показывает детали модуля с возможностью просмотра уроков"""
    course = session.current_course
    module = course.modules[module_index]
    
    text = f"📚 <b>Модуль {module.module_number}: {module.module_title}</b>\n\n"
    text += f"<b>Цель:</b> {module.module_goal}\n\n"
    text += f"<b>Уроки ({len(module.lessons)}):</b>\n\n"
    
    keyboard = []
    for i, lesson in enumerate(module.lessons):
        # Проверяем, есть ли детальные материалы
        has_detailed = "📖" if lesson.detailed_content else "📝"
        content_count = len(lesson.content_outline) if lesson.content_outline else 0
        
        text += f"{has_detailed} {i+1}. {lesson.lesson_title} ({lesson.estimated_time_minutes} мин)\n"
        
        keyboard.append([InlineKeyboardButton(
            f"{has_detailed} {i+1}. {lesson.lesson_title[:35]}",
            callback_data=f"view_lesson_{module_index}_{i}"
        )])
    
    text += f"\n<b>Легенда:</b>\n"
    text += "📖 - есть детальные материалы\n"
    text += "📝 - только структура урока\n"
    
    keyboard.append([InlineKeyboardButton("🔙 К курсу", callback_data="back_to_course")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def _show_lesson_details(query, user_id: int, module_index: int, lesson_index: int, session: UserSession):
    """Показывает детали урока с возможностью экспорта детальных материалов"""
    course = session.current_course
    module = course.modules[module_index]
    lesson = module.lessons[lesson_index]
    
    text = f"📝 <b>Урок: {lesson.lesson_title}</b>\n\n"
    text += f"<b>Модуль:</b> {module.module_title}\n"
    text += f"<b>Формат:</b> {lesson.format}\n"
    text += f"<b>Длительность:</b> {lesson.estimated_time_minutes} минут\n"
    text += f"<b>Оценка:</b> {lesson.assessment}\n\n"
    text += f"<b>Цель урока:</b>\n{lesson.lesson_goal}\n\n"
    
    if lesson.content_outline:
        text += f"<b>План содержания ({len(lesson.content_outline)} тем):</b>\n"
        for i, topic in enumerate(lesson.content_outline[:5], 1):
            text += f"{i}. {topic}\n"
        if len(lesson.content_outline) > 5:
            text += f"... и ещё {len(lesson.content_outline) - 5} тем\n"
        text += "\n"
    
    keyboard = []
    
    # Если есть детальные материалы - показываем кнопку экспорта
    if lesson.detailed_content:
        text += f"✅ <b>Детальные материалы сгенерированы!</b>\n"
        text += f"Тем раскрыто: {len(lesson.detailed_content.topics)}\n"
        text += f"Время изучения: ~{lesson.detailed_content.total_estimated_time_minutes} мин\n\n"
        
        keyboard.append([InlineKeyboardButton(
            "📥 Экспортировать детальные материалы",
            callback_data=f"export_topics_menu_{module_index}_{lesson_index}"
        )])
    else:
        text += "ℹ️ <i>Детальные материалы не сгенерированы</i>\n\n"
        keyboard.append([InlineKeyboardButton(
            "🤖 Сгенерировать детальные материалы",
            callback_data=f"gen_topics_lesson_{module_index}_{lesson_index}"
        )])
    
    # Кнопки навигации
    keyboard.append([InlineKeyboardButton("🔙 К модулю", callback_data=f"view_module_{module_index}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def _show_lessons_for_topic_gen(query, user_id: int, module_index: int, session: UserSession):
    """Показывает список уроков модуля для генерации детальных материалов"""
    course = session.current_course
    module = course.modules[module_index]
    
    text = f"📖 <b>Генерация детальных материалов</b>\n\n"
    text += f"Модуль: {module.module_title}\n\n"
    text += "Выберите урок для генерации детального контента по каждому пункту плана:\n\n"
    
    keyboard = []
    for i, lesson in enumerate(module.lessons):
        # Показываем количество пунктов в плане
        content_count = len(lesson.content_outline) if lesson.content_outline else 0
        keyboard.append([InlineKeyboardButton(
            f"📝 {i+1}. {lesson.lesson_title} ({content_count} тем)",
            callback_data=f"gen_topics_lesson_{module_index}_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def _generate_lesson_topics(query, user_id: int, module_index: int, lesson_index: int, session: UserSession):
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
    
    # Генерируем детальный контент
    lesson_content = content_generator.generate_lesson_detailed_content(
        lesson=lesson,
        module_number=module.module_number,
        course_title=course.course_title,
        module_title=module.module_title,
        target_audience=course.target_audience
    )
    
    if lesson_content:
        # Сохраняем детальный контент в урок
        lesson.detailed_content = lesson_content
        
        text = f"✅ <b>Детальные материалы сгенерированы!</b>\n\n"
        text += f"📚 <b>Урок:</b> {lesson.lesson_title}\n"
        text += f"📖 <b>Тем раскрыто:</b> {len(lesson_content.topics)}\n\n"
        
        # Показываем краткий обзор тем
        text += "<b>Темы:</b>\n"
        for i, topic_material in enumerate(lesson_content.topics[:5], 1):
            text += f"{i}. {topic_material.topic_title}\n"
            text += f"   • {len(topic_material.examples)} примеров\n"
            text += f"   • {len(topic_material.quiz_questions)} вопросов\n"
        
        if len(lesson_content.topics) > 5:
            text += f"... и ещё {len(lesson_content.topics) - 5} тем\n"
        
        text += "\n<b>Что дальше?</b>"
        
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    text = update.message.text.lower()
    
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id=user_id)
    
    session = user_sessions[user_id]
    
    # Проверяем, не запрос ли это на создание курса
    if not session.editing_mode:
        if any(word in text for word in ['создай курс', 'сделай курс', 'курс по', 'создать курс']):
            # Автоматически запускаем создание курса
            await create_course(update, context)
            return
        else:
            await update.message.reply_text(
                "Используйте команды:\n"
                "/create - создать курс\n"
                "/view - просмотреть курс\n"
                "/help - справка\n\n"
                "Или напишите: 'Создай курс по Python для начинающих'"
            )
            return
    
    # Обработка кастомной перегенерации слайда
    if session.editing_path and session.editing_path.startswith("regen_slide_custom_"):
        parts = session.editing_path.split("_")
        lecture_index = int(parts[3])
        slide_index = int(parts[4])
        custom_requirements = update.message.text
        session.editing_mode = False
        session.editing_path = None
        
        await update.message.reply_text(
            f"✅ <b>Требования получены!</b>\n\n"
            f"🤖 Перегенерирую слайд с учётом:\n{custom_requirements}\n\n"
            f"⏳ Подождите 10-20 секунд...",
            parse_mode="HTML"
        )
        
        # Сохраняем требования для передачи в callback
        session.temp_data['custom_req'] = custom_requirements
        session.temp_data['regen_type'] = 'slide'
        session.temp_data['lecture_idx'] = lecture_index
        session.temp_data['slide_idx'] = slide_index
        
        # Создаем временную кнопку для запуска перегенерации
        keyboard = [[InlineKeyboardButton("▶️ Начать перегенерацию", callback_data=f"start_regen_slide_{lecture_index}_{slide_index}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Нажмите для запуска:", reply_markup=reply_markup)
    
    # Обработка кастомной перегенерации урока (Lesson)
    elif session.editing_path and session.editing_path.startswith("regen_lesson_custom_"):
        parts = session.editing_path.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        custom_requirements = update.message.text
        session.editing_mode = False
        session.editing_path = None
        
        await update.message.reply_text(
            f"✅ <b>Требования получены!</b>\n\n"
            f"🤖 Перегенерирую урок с учётом:\n{custom_requirements}\n\n"
            f"⏳ Подождите 20-30 секунд...",
            parse_mode="HTML"
        )
        
        # Сохраняем требования
        session.temp_data['custom_req'] = custom_requirements
        session.temp_data['regen_type'] = 'lesson'
        session.temp_data['module_idx'] = module_index
        session.temp_data['lesson_idx'] = lesson_index
        
        # Создаем кнопку для запуска
        keyboard = [[InlineKeyboardButton("▶️ Начать перегенерацию", callback_data=f"start_regen_lesson_item_{module_index}_{lesson_index}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Нажмите для запуска:", reply_markup=reply_markup)
    
    # Обработка кастомной перегенерации лекции
    elif session.editing_path and session.editing_path.startswith("regen_lecture_custom_"):
        lecture_index = int(session.editing_path.split("_")[3])
        custom_requirements = update.message.text
        session.editing_mode = False
        session.editing_path = None
        
        await update.message.reply_text(
            f"✅ <b>Требования получены!</b>\n\n"
            f"🤖 Перегенерирую лекцию с учётом:\n{custom_requirements[:200]}...\n\n"
            f"⏳ Это займёт 30-60 секунд...",
            parse_mode="HTML"
        )
        
        # Сохраняем требования
        session.temp_data['custom_req'] = custom_requirements
        session.temp_data['regen_type'] = 'lecture'
        session.temp_data['lecture_idx'] = lecture_index
        
        # Создаем кнопку для запуска
        keyboard = [[InlineKeyboardButton("▶️ Начать перегенерацию", callback_data=f"start_regen_lecture_{lecture_index}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Нажмите для запуска:", reply_markup=reply_markup)
    
    # Обработка редактирования названия модуля
    elif session.editing_path and session.editing_path.startswith("edit_module_name_"):
        module_index = int(session.editing_path.split("_")[3])
        course = session.current_course
        course.modules[module_index].module_title = update.message.text
        session.editing_mode = False
        session.editing_path = None
        
        await update.message.reply_text(
            f"✅ Название модуля обновлено!\n\n"
            f"<b>Новое название:</b> {update.message.text}",
            parse_mode="HTML"
        )
        
        # Расширенное меню опций
        keyboard = [
            [InlineKeyboardButton("✏️ Редактировать этот модуль", callback_data=f"edit_mod_{module_index}")],
            [InlineKeyboardButton("🤖 Сгенерировать цель с AI", callback_data=f"gen_module_goal_{module_index}")],
            [InlineKeyboardButton("📋 Список модулей", callback_data="back_to_edit")],
            [InlineKeyboardButton("👁️ Просмотреть курс", callback_data="back_to_course")],
            [InlineKeyboardButton("📄 Экспортировать JSON", callback_data="export_now")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
    
    # Обработка редактирования цели модуля
    elif session.editing_path and session.editing_path.startswith("edit_module_goal_"):
        module_index = int(session.editing_path.split("_")[3])
        course = session.current_course
        course.modules[module_index].module_goal = update.message.text
        session.editing_mode = False
        session.editing_path = None
        
        await update.message.reply_text(
            f"✅ Цель модуля обновлена!\n\n"
            f"<b>Новая цель:</b> {update.message.text}",
            parse_mode="HTML"
        )
        
        # Расширенное меню опций
        keyboard = [
            [InlineKeyboardButton("✏️ Редактировать этот модуль", callback_data=f"edit_mod_{module_index}")],
            [InlineKeyboardButton("📝 Изменить название", callback_data=f"edit_module_name_{module_index}")],
            [InlineKeyboardButton("📋 Список модулей", callback_data="back_to_edit")],
            [InlineKeyboardButton("👁️ Просмотреть курс", callback_data="back_to_course")],
            [InlineKeyboardButton("📄 Экспортировать JSON", callback_data="export_now")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
    
    # Обработка ввода темы
    elif session.editing_path == "awaiting_topic":
        session.temp_data['topic'] = update.message.text
        session.editing_path = "awaiting_modules"
        
        keyboard = []
        for i in range(3, 11):
            keyboard.append([InlineKeyboardButton(f"{i} модулей", callback_data=f"modules_{i}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ Тема: <b>{text}</b>\n\nВыберите количество модулей:",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    
    # Обработка ввода недель
    elif session.editing_path == "awaiting_weeks":
        try:
            weeks = int(text)
            session.temp_data['duration_weeks'] = weeks
            session.editing_path = "awaiting_hours"
            
            await update.message.reply_text(
                f"✅ Длительность: {weeks} недель\n\n"
                "Введите количество часов в неделю (например: 5):"
            )
        except ValueError:
            await update.message.reply_text("❌ Введите число недель:")
    
    # Обработка ввода часов и генерация курса
    elif session.editing_path == "awaiting_hours":
        try:
            hours = int(text)
            session.temp_data['hours_per_week'] = hours
            
            await update.message.reply_text("🔄 Генерирую курс... Подождите немного...")
            
            # Генерируем курс
            course_data = openai_client.generate_course_structure(
                topic=session.temp_data['topic'],
                audience_level=session.temp_data['level'],
                module_count=session.temp_data['module_count'],
                duration_weeks=session.temp_data['duration_weeks'],
                hours_per_week=hours
            )
            
            if course_data:
                try:
                    course = Course(**course_data)
                    session.current_course = course
                    session.editing_mode = False
                    
                    # Показываем результат
                    text = f"✅ <b>Курс создан!</b>\n\n"
                    text += f"🎓 <b>{course.course_title}</b>\n\n"
                    text += f"👥 {course.target_audience}\n"
                    text += f"⏱️ {course.duration_weeks} недель\n"
                    text += f"📚 Модулей: {len(course.modules)}\n\n"
                    text += "Используйте:\n"
                    text += "/view - просмотреть структуру\n"
                    text += "/edit - редактировать модули\n"
                    text += "/generate - создать лекции и слайды\n"
                    text += "/export - скачать курс"
                    
                    await update.message.reply_text(text, parse_mode="HTML")
                    
                except Exception as e:
                    logger.error(f"Ошибка создания курса: {e}")
                    await update.message.reply_text("❌ Ошибка при создании курса")
            else:
                await update.message.reply_text("❌ Не удалось сгенерировать курс")
                
        except ValueError:
            await update.message.reply_text("❌ Введите число часов:")


# ---------- ЗАПУСК ----------
def main():
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env")
        return

    # Патчим httpx.AsyncClient для отключения SSL
    original_init = httpx.AsyncClient.__init__
    
    def patched_init(self, *args, **kwargs):
        kwargs['verify'] = False
        original_init(self, *args, **kwargs)
    
    httpx.AsyncClient.__init__ = patched_init
    
    # Создаём приложение без JobQueue (для совместимости с Python 3.13)
    app = ApplicationBuilder().token(TOKEN).job_queue(None).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("create", create_course))
    app.add_handler(CommandHandler("view", view_course))
    app.add_handler(CommandHandler("edit", edit_course))
    app.add_handler(CommandHandler("generate", generate_content))
    app.add_handler(CommandHandler("regenerate", regenerate_content))
    app.add_handler(CommandHandler("regenerate_lesson", regenerate_lesson))
    app.add_handler(CommandHandler("generate_topics", generate_topics))
    app.add_handler(CommandHandler("export", export_course))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ AI Course Builder запущен! Нажмите Ctrl+C для остановки.")
    app.run_polling(stop_signals=None, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

