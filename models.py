from pydantic import BaseModel
from typing import List, Optional, Union
from enum import Enum

class DifficultyLevel(str, Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"

class LessonFormat(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    LAB = "lab"
    QUIZ = "quiz"
    PROJECT = "project"

class TopicMaterial(BaseModel):
    """Детальный учебный материал по отдельной теме из плана урока"""
    topic_title: str  # Название темы из content_outline
    topic_number: int  # Порядковый номер темы в уроке
    
    # Основной контент
    introduction: str  # Введение в тему (2-3 абзаца)
    theory: str  # Теоретический материал (подробное объяснение)
    examples: List[str]  # Практические примеры (3-5 примеров)
    code_snippets: Optional[List[str]] = None  # Примеры кода (если применимо)
    
    # Дополнительные материалы
    key_points: List[str]  # Ключевые моменты (5-7 пунктов)
    common_mistakes: List[str]  # Частые ошибки (3-5 пунктов)
    best_practices: List[str]  # Лучшие практики (3-5 пунктов)
    
    # Задания и вопросы
    practice_exercises: List[str]  # Упражнения для практики (3-5 заданий)
    quiz_questions: List[str]  # Вопросы для самопроверки (5-7 вопросов)
    
    # Ссылки и ресурсы
    additional_resources: Optional[List[str]] = None  # Дополнительные ресурсы
    estimated_reading_time_minutes: int  # Примерное время изучения


class LessonContent(BaseModel):
    """Полный контент урока с детализацией каждой темы"""
    lesson_title: str
    lesson_goal: str
    lesson_number: int
    module_number: int
    
    topics: List[TopicMaterial]  # Детальные материалы по каждой теме
    
    total_topics: int
    total_estimated_time_minutes: int


class Lesson(BaseModel):
    lesson_title: str
    lesson_goal: str
    content_outline: List[str]
    assessment: str
    format: Union[LessonFormat, str]  # Разрешаем строки для гибкости
    estimated_time_minutes: int
    
    # Опциональный детальный контент
    detailed_content: Optional[LessonContent] = None

class Module(BaseModel):
    module_number: int
    module_title: str
    module_goal: str
    lessons: List[Lesson]

class Course(BaseModel):
    course_title: str
    target_audience: str
    duration_hours: Optional[int] = None
    duration_weeks: Optional[int] = None
    modules: List[Module]

class Slide(BaseModel):
    """Слайд лекции"""
    slide_number: int
    title: str
    content: str  # Основной текст слайда
    slide_type: str  # title, content, code, diagram, quiz, summary
    code_example: Optional[str] = None  # Пример кода (если есть)
    notes: Optional[str] = None  # Заметки для преподавателя


class Lecture(BaseModel):
    """Лекция по модулю"""
    lecture_title: str
    module_number: int
    module_title: str
    duration_minutes: int
    slides: List[Slide]
    learning_objectives: List[str]  # Цели обучения
    key_takeaways: List[str]  # Ключевые выводы


class ModuleContent(BaseModel):
    """Полный контент модуля"""
    module_number: int
    module_title: str
    lectures: List[Lecture]
    total_slides: int
    estimated_duration_minutes: int


class UserSession(BaseModel):
    user_id: int
    current_course: Optional[Course] = None
    current_module_content: Optional[ModuleContent] = None  # Контент модуля
    editing_mode: bool = False
    editing_path: Optional[str] = None  # JSON path for editing
    temp_data: dict = {}  # Временные данные для создания курса
    
    class Config:
        arbitrary_types_allowed = True
