"""Обработчик текстовых сообщений"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models import Course
from utils import get_session_manager
from openai_client import OpenAIClient

logger = logging.getLogger(__name__)

# Глобальная переменная для клиента (ленивая инициализация)
_openai_client = None


def get_openai_client():
    """Получает или создаёт экземпляр OpenAIClient"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    text = update.message.text.lower()
    
    session_manager = get_session_manager()
    session = session_manager.get_session(user_id)
    
    # Проверяем, не запрос ли это на создание курса
    if not session.editing_mode:
        if any(word in text for word in ['создай курс', 'сделай курс', 'курс по', 'создать курс']):
            # Автоматически запускаем создание курса
            from .commands import create_course
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
        
        session.temp_data['custom_req'] = custom_requirements
        session.temp_data['regen_type'] = 'slide'
        session.temp_data['lecture_idx'] = lecture_index
        session.temp_data['slide_idx'] = slide_index
        
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
        
        session.temp_data['custom_req'] = custom_requirements
        session.temp_data['regen_type'] = 'lesson'
        session.temp_data['module_idx'] = module_index
        session.temp_data['lesson_idx'] = lesson_index
        
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
        
        session.temp_data['custom_req'] = custom_requirements
        session.temp_data['regen_type'] = 'lecture'
        session.temp_data['lecture_idx'] = lecture_index
        
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
            openai_client = get_openai_client()
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

