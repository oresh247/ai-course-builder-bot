"""Обработчики команд бота"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import get_session_manager, format_course_info

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    user_id = update.effective_user.id
    session_manager = get_session_manager()
    session_manager.get_session(user_id)
    
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
    session_manager = get_session_manager()
    session = session_manager.get_session(user_id)
    
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
    session_manager = get_session_manager()
    
    if not session_manager.has_session(user_id):
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
    session = session_manager.get_session(user_id)
    if not session.current_course:
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
    course = session.current_course
    text = format_course_info(course)
    
    keyboard = []
    for i, module in enumerate(course.modules):
        keyboard.append([InlineKeyboardButton(
            f"👁️ {i+1}. Детали модуля: {module.module_title[:30]}",
            callback_data=f"view_module_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def edit_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Редактирование курса"""
    user_id = update.effective_user.id
    session_manager = get_session_manager()
    
    if not session_manager.has_session(user_id):
        await update.message.reply_text("❌ У вас нет курса для редактирования. Используйте /create")
        return
    
    session = session_manager.get_session(user_id)
    if not session.current_course:
        await update.message.reply_text("❌ У вас нет курса для редактирования. Используйте /create")
        return
    
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
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def generate_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация контента для модуля"""
    user_id = update.effective_user.id
    session_manager = get_session_manager()
    
    if not session_manager.has_session(user_id):
        await update.message.reply_text("❌ У вас нет курса. Сначала создайте курс с помощью /create")
        return
    
    session = session_manager.get_session(user_id)
    if not session.current_course:
        await update.message.reply_text("❌ У вас нет курса. Сначала создайте курс с помощью /create")
        return
    
    course = session.current_course
    
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
    session_manager = get_session_manager()
    
    if not session_manager.has_session(user_id):
        await update.message.reply_text(
            "❌ У вас нет сгенерированного контента.\n"
            "Сначала используйте /generate для создания контента модуля"
        )
        return
    
    session = session_manager.get_session(user_id)
    if not session.current_module_content:
        await update.message.reply_text(
            "❌ У вас нет сгенерированного контента.\n"
            "Сначала используйте /generate для создания контента модуля"
        )
        return
    
    module_content = session.current_module_content
    
    text = f"🔄 <b>Перегенерация контента</b>\n\n"
    text += f"Модуль: {module_content.module_title}\n\n"
    text += "Выберите что перегенерировать:\n\n"
    
    keyboard = []
    
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
    session_manager = get_session_manager()
    
    if not session_manager.has_session(user_id):
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
    session = session_manager.get_session(user_id)
    if not session.current_course:
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
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
    session_manager = get_session_manager()
    
    if not session_manager.has_session(user_id):
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
    session = session_manager.get_session(user_id)
    if not session.current_course:
        await update.message.reply_text("❌ У вас нет курса. Используйте /create")
        return
    
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
    session_manager = get_session_manager()
    
    if not session_manager.has_session(user_id):
        await update.message.reply_text("❌ У вас нет курса для экспорта")
        return
    
    session = session_manager.get_session(user_id)
    if not session.current_course:
        await update.message.reply_text("❌ У вас нет курса для экспорта")
        return
    
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

