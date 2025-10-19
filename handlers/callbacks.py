"""Главный обработчик callback запросов"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import get_session_manager
from exporters import CourseExporter
from .callback_helpers import (
    handle_module_edit,
    generate_module_content,
    show_lecture_regenerate_menu,
    show_slides_list,
    show_lessons_for_regen,
    show_lesson_regen_menu,
    show_module_details,
    show_lesson_details,
    show_lessons_for_topic_gen,
    generate_lesson_topics
)
from .callback_regeneration import (
    regenerate_lesson_item,
    show_slide_regenerate_menu,
    regenerate_lecture,
    regenerate_slide,
    generate_module_goal
)

logger = logging.getLogger(__name__)
course_exporter = CourseExporter()


async def handle_callback(query_update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = query_update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    session_manager = get_session_manager()
    
    if not session_manager.has_session(user_id):
        await query.edit_message_text("❌ Сессия истекла. Используйте /start")
        return
    
    session = session_manager.get_session(user_id)
    
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
        await handle_module_edit(query, user_id, module_index, session)
    
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
        await generate_module_goal(query, user_id, module_index, session)
    
    elif data.startswith("gen_content_"):
        module_index = int(data.split("_")[2])
        await generate_module_content(query, user_id, module_index, session)
    
    # ВАЖНО: Более специфичные паттерны должны проверяться первыми!
    elif data.startswith("regen_lecture_full_"):
        lecture_index = int(data.split("_")[3])
        await regenerate_lecture(query, user_id, lecture_index, session, None)
    
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
        await show_lecture_regenerate_menu(query, user_id, lecture_index, session)
    
    elif data.startswith("select_slide_"):
        lecture_index = int(data.split("_")[2])
        await show_slides_list(query, user_id, lecture_index, session)
    
    elif data.startswith("regen_slide_full_"):
        parts = data.split("_")
        lecture_index = int(parts[3])
        slide_index = int(parts[4])
        await regenerate_slide(query, user_id, lecture_index, slide_index, session, None)
    
    elif data.startswith("start_regen_slide_"):
        parts = data.split("_")
        lecture_index = int(parts[3])
        slide_index = int(parts[4])
        custom_req = session.temp_data.get('custom_req')
        await regenerate_slide(query, user_id, lecture_index, slide_index, session, custom_req)
    
    elif data.startswith("start_regen_lecture_"):
        lecture_index = int(data.split("_")[3])
        custom_req = session.temp_data.get('custom_req')
        await regenerate_lecture(query, user_id, lecture_index, session, custom_req)
    
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
        await show_slide_regenerate_menu(query, user_id, lecture_index, slide_index, session)
    
    elif data.startswith("regen_lesson_module_"):
        module_index = int(data.split("_")[3])
        await show_lessons_for_regen(query, user_id, module_index, session)
    
    elif data.startswith("view_module_"):
        module_index = int(data.split("_")[2])
        await show_module_details(query, user_id, module_index, session)
    
    elif data.startswith("view_lesson_"):
        parts = data.split("_")
        module_index = int(parts[2])
        lesson_index = int(parts[3])
        await show_lesson_details(query, user_id, module_index, lesson_index, session)
    
    elif data.startswith("gen_topics_module_"):
        module_index = int(data.split("_")[3])
        await show_lessons_for_topic_gen(query, user_id, module_index, session)
    
    elif data.startswith("gen_topics_lesson_"):
        parts = data.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        await generate_lesson_topics(query, user_id, module_index, lesson_index, session)
    
    elif data.startswith("regen_lesson_item_"):
        parts = data.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        await show_lesson_regen_menu(query, user_id, module_index, lesson_index, session)
    
    elif data.startswith("regen_lesson_full_"):
        parts = data.split("_")
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        await regenerate_lesson_item(query, user_id, module_index, lesson_index, session, None)
    
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
        await regenerate_lesson_item(query, user_id, module_index, lesson_index, session, custom_req)
    
    # Навигация
    elif data == "back_to_lectures":
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
    
    # Экспорт контента модуля
    elif data.startswith("export_mcontent_"):
        parts = data.split("_")
        export_format = parts[2]
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
        
        await query.message.reply_document(
            document=content_str.encode('utf-8'),
            filename=filename,
            caption=f"{caption}\n\nЛекций: {len(module_content.lectures)} • Слайдов: {module_content.total_slides}"
        )
        
        await query.answer("✅ Файл отправлен!")
    
    # Экспорт детальных материалов урока
    elif data.startswith("export_topics_menu_"):
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
        parts = data.split("_")
        export_format = parts[2]
        module_index = int(parts[3])
        lesson_index = int(parts[4])
        
        course = session.current_course
        module = course.modules[module_index]
        lesson = module.lessons[lesson_index]
        
        if not lesson.detailed_content:
            await query.answer("❌ Детальный контент не сгенерирован!")
            return
        
        await query.answer("🔄 Создаю файл...")
        
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
    
    # Экспорт курса
    elif data.startswith("export_"):
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

