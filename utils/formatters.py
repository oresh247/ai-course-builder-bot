"""Форматирование сообщений для Telegram"""

from typing import List
from models import Course, Module, Lesson, ModuleContent, LessonContent


def format_course_info(course: Course) -> str:
    """Форматирует информацию о курсе"""
    text = f"🎓 <b>{course.course_title}</b>\n\n"
    text += f"👥 <b>Аудитория:</b> {course.target_audience}\n"
    
    if course.duration_weeks:
        text += f"⏱️ <b>Длительность:</b> {course.duration_weeks} недель\n"
    if course.duration_hours:
        text += f"📚 <b>Часов:</b> {course.duration_hours}\n"
    
    text += f"\n<b>Модули ({len(course.modules)}):</b>\n\n"
    
    for i, module in enumerate(course.modules, 1):
        text += f"<b>{i}. {module.module_title}</b>\n"
        text += f"<i>{module.module_goal}</i>\n"
        text += f"Уроков: {len(module.lessons)}\n\n"
    
    return text


def format_module_info(module: Module, module_number: int) -> str:
    """Форматирует информацию о модуле"""
    text = f"📚 <b>Модуль {module_number}: {module.module_title}</b>\n\n"
    text += f"<b>Цель:</b> {module.module_goal}\n\n"
    text += f"<b>Уроки ({len(module.lessons)}):</b>\n\n"
    
    for i, lesson in enumerate(module.lessons, 1):
        has_detailed = "📖" if lesson.detailed_content else "📝"
        text += f"{has_detailed} {i}. {lesson.lesson_title} ({lesson.estimated_time_minutes} мин)\n"
    
    text += f"\n<b>Легенда:</b>\n"
    text += "📖 - есть детальные материалы\n"
    text += "📝 - только структура урока\n"
    
    return text


def format_lesson_info(lesson: Lesson, module_title: str) -> str:
    """Форматирует информацию о уроке"""
    text = f"📝 <b>Урок: {lesson.lesson_title}</b>\n\n"
    text += f"<b>Модуль:</b> {module_title}\n"
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
    
    if lesson.detailed_content:
        text += f"✅ <b>Детальные материалы сгенерированы!</b>\n"
        text += f"Тем раскрыто: {len(lesson.detailed_content.topics)}\n"
        text += f"Время изучения: ~{lesson.detailed_content.total_estimated_time_minutes} мин\n\n"
    else:
        text += "ℹ️ <i>Детальные материалы не сгенерированы</i>\n\n"
    
    return text


def format_module_content_info(module_content: ModuleContent) -> str:
    """Форматирует информацию о сгенерированном контенте модуля"""
    text = f"✅ <b>Контент модуля сгенерирован!</b>\n\n"
    text += f"📚 <b>Модуль:</b> {module_content.module_title}\n"
    text += f"📖 <b>Лекций:</b> {len(module_content.lectures)}\n"
    text += f"📊 <b>Слайдов:</b> {module_content.total_slides}\n"
    text += f"⏱️ <b>Время:</b> {module_content.estimated_duration_minutes} минут\n\n"
    
    for i, lecture in enumerate(module_content.lectures, 1):
        text += f"{i}. {lecture.lecture_title} ({len(lecture.slides)} слайдов)\n"
    
    text += "\n<b>Что дальше?</b>"
    
    return text


def format_lesson_content_info(lesson_content: LessonContent, lesson_title: str) -> str:
    """Форматирует информацию о детальных материалах урока"""
    text = f"✅ <b>Детальные материалы сгенерированы!</b>\n\n"
    text += f"📚 <b>Урок:</b> {lesson_title}\n"
    text += f"📖 <b>Тем раскрыто:</b> {len(lesson_content.topics)}\n\n"
    
    text += "<b>Темы:</b>\n"
    for i, topic_material in enumerate(lesson_content.topics[:5], 1):
        text += f"{i}. {topic_material.topic_title}\n"
        text += f"   • {len(topic_material.examples)} примеров\n"
        text += f"   • {len(topic_material.quiz_questions)} вопросов\n"
    
    if len(lesson_content.topics) > 5:
        text += f"... и ещё {len(lesson_content.topics) - 5} тем\n"
    
    text += "\n<b>Что дальше?</b>"
    
    return text


def truncate_text(text: str, max_length: int = 200) -> str:
    """Обрезает текст до указанной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

