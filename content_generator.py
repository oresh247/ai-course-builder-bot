"""
Генератор учебного контента для модулей курса
"""
import logging
import json
from typing import Optional, Dict, Any, List
from models import Module, Lecture, Slide, ModuleContent, Lesson, LessonContent, TopicMaterial
from openai_client import OpenAIClient
from prompts import (
    MODULE_CONTENT_SYSTEM_PROMPT,
    MODULE_CONTENT_PROMPT_TEMPLATE,
    TOPIC_MATERIAL_SYSTEM_PROMPT,
    TOPIC_MATERIAL_PROMPT_TEMPLATE,
    format_lessons_list
)

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Класс для генерации учебного контента модулей"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    def generate_module_content(self, module: Module, course_title: str, 
                               target_audience: str) -> Optional[ModuleContent]:
        """
        Генерирует полный контент для модуля включая лекции и слайды
        
        Пробует несколько методов:
        1. Function Calling - самый надежный
        2. JSON mode - простой и быстрый
        3. Обычный текст - fallback
        4. Тестовый контент - если все не сработало
        """
        logger.info(f"Генерируем контент для модуля: {module.module_title}")
        
        # Попытка 1: Function Calling (самый надежный способ)
        result = self._try_function_calling(module, course_title, target_audience)
        if result:
            return result
        
        # Попытка 2: JSON mode
        result = self._try_json_mode(module, course_title, target_audience)
        if result:
            return result
        
        # Попытка 3: Обычный текстовый режим
        result = self._try_text_mode(module, course_title, target_audience)
        if result:
            return result
        
        # Fallback: Тестовый контент
        logger.warning("📌 Все методы генерации провалились, используем тестовый контент")
        return self._get_test_module_content(module)
    
    def _try_function_calling(self, module: Module, course_title: str, 
                             target_audience: str) -> Optional[ModuleContent]:
        """Попытка генерации через Function Calling"""
        try:
            logger.info("🔧 Пробуем Function Calling...")
            
            # Определяем функцию для создания лекций
            tools = [{
                "type": "function",
                "function": {
                    "name": "create_module_lectures",
                    "description": "Создает детальные лекции со слайдами для учебного модуля",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lectures": {
                                "type": "array",
                                "description": "Массив лекций для модуля",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "lecture_title": {"type": "string"},
                                        "duration_minutes": {"type": "integer"},
                                        "learning_objectives": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "key_takeaways": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "slides": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "slide_number": {"type": "integer"},
                                                    "title": {"type": "string"},
                                                    "content": {"type": "string"},
                                                    "slide_type": {"type": "string"},
                                                    "code_example": {"type": ["string", "null"]},
                                                    "notes": {"type": "string"}
                                                },
                                                "required": ["slide_number", "title", "content", "slide_type", "notes"]
                                            }
                                        }
                                    },
                                    "required": ["lecture_title", "duration_minutes", "learning_objectives", "key_takeaways", "slides"]
                                }
                            }
                        },
                        "required": ["lectures"]
                    }
                }
            }]
            
            from prompts import MODULE_CONTENT_PROMPT_TEMPLATE, MODULE_CONTENT_SYSTEM_PROMPT, format_lessons_list
            
            prompt = MODULE_CONTENT_PROMPT_TEMPLATE.format(
                course_title=course_title,
                target_audience=target_audience,
                module_number=module.module_number,
                module_title=module.module_title,
                module_goal=module.module_goal,
                lessons_list=format_lessons_list(module.lessons),
                num_lessons=len(module.lessons)
            )
            
            response = self.openai_client.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": MODULE_CONTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "create_module_lectures"}},
                temperature=0.3
            )
            
            # Извлекаем аргументы функции
            tool_call = response.choices[0].message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            
            # Формируем полный JSON
            json_content = {
                "module_number": module.module_number,
                "module_title": module.module_title,
                "lectures": function_args["lectures"]
            }
            
            # Добавляем обязательные поля для каждой лекции
            for lecture in json_content["lectures"]:
                lecture["module_number"] = module.module_number
                lecture["module_title"] = module.module_title
            
            # Рассчитываем статистику
            total_slides = sum(len(lecture["slides"]) for lecture in json_content["lectures"])
            total_duration = sum(lecture["duration_minutes"] for lecture in json_content["lectures"])
            
            json_content["total_slides"] = total_slides
            json_content["estimated_duration_minutes"] = total_duration
            
            module_content = ModuleContent(**json_content)
            logger.info(f"✅ Function Calling успешно: {len(module_content.lectures)} лекций, {total_slides} слайдов")
            return module_content
            
        except Exception as e:
            logger.warning(f"❌ Function Calling не сработал: {e}")
            return None
    
    def _try_json_mode(self, module: Module, course_title: str, 
                       target_audience: str) -> Optional[ModuleContent]:
        """Попытка генерации через JSON mode"""
        try:
            logger.info("🔧 Пробуем JSON mode...")
            
            from prompts import MODULE_CONTENT_PROMPT_TEMPLATE, MODULE_CONTENT_SYSTEM_PROMPT, format_lessons_list
            
            prompt = MODULE_CONTENT_PROMPT_TEMPLATE.format(
                course_title=course_title,
                target_audience=target_audience,
                module_number=module.module_number,
                module_title=module.module_title,
                module_goal=module.module_goal,
                lessons_list=format_lessons_list(module.lessons),
                num_lessons=len(module.lessons)
            )
            
            response = self.openai_client.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": MODULE_CONTENT_SYSTEM_PROMPT + "\n\nВЫВОД ТОЛЬКО В JSON ФОРМАТЕ!"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=8000
            )
            
            content = response.choices[0].message.content.strip()
            json_content = self._extract_json(content)
            
            if json_content and "lectures" in json_content:
                total_slides = sum(len(lecture.get("slides", [])) for lecture in json_content["lectures"])
                total_duration = sum(lecture.get("duration_minutes", 0) for lecture in json_content["lectures"])
                
                json_content["total_slides"] = total_slides
                json_content["estimated_duration_minutes"] = total_duration
                
                module_content = ModuleContent(**json_content)
                logger.info(f"✅ JSON mode успешно: {len(module_content.lectures)} лекций, {total_slides} слайдов")
                return module_content
            else:
                logger.warning("❌ JSON mode вернул неправильную структуру")
                return None
                
        except Exception as e:
            logger.warning(f"❌ JSON mode не сработал: {e}")
            return None
    
    def _try_text_mode(self, module: Module, course_title: str, 
                       target_audience: str) -> Optional[ModuleContent]:
        """Попытка генерации в обычном текстовом режиме"""
        try:
            logger.info("🔧 Пробуем обычный текстовый режим...")
            
            from prompts import MODULE_CONTENT_PROMPT_TEMPLATE, MODULE_CONTENT_SYSTEM_PROMPT, format_lessons_list
            
            prompt = MODULE_CONTENT_PROMPT_TEMPLATE.format(
                course_title=course_title,
                target_audience=target_audience,
                module_number=module.module_number,
                module_title=module.module_title,
                module_goal=module.module_goal,
                lessons_list=format_lessons_list(module.lessons),
                num_lessons=len(module.lessons)
            )
            
            response = self.openai_client.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": MODULE_CONTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=8000
            )
            
            content = response.choices[0].message.content.strip()
            json_content = self._extract_json(content)
            
            if json_content and "lectures" in json_content:
                total_slides = sum(len(lecture.get("slides", [])) for lecture in json_content["lectures"])
                total_duration = sum(lecture.get("duration_minutes", 0) for lecture in json_content["lectures"])
                
                json_content["total_slides"] = total_slides
                json_content["estimated_duration_minutes"] = total_duration
                
                module_content = ModuleContent(**json_content)
                logger.info(f"✅ Текстовый режим успешно: {len(module_content.lectures)} лекций, {total_slides} слайдов")
                return module_content
            else:
                logger.warning("❌ Текстовый режим вернул неправильную структуру")
                return None
                
        except Exception as e:
            logger.warning(f"❌ Текстовый режим не сработал: {e}")
            return None
    
    def _extract_json(self, content: str) -> Optional[Dict[str, Any]]:
        """Извлекает JSON из ответа и преобразует в нужный формат"""
        try:
            # Удаляем markdown блоки если есть
            content = content.replace('```json', '').replace('```', '')
            content = content.strip()
            
            # Ищем JSON блок
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                logger.error("JSON блок не найден в ответе")
                return None
            
            json_str = content[start_idx:end_idx]
            
            # Проверяем, что JSON не обрезан
            if not json_str.endswith('}'):
                logger.error("JSON обрезан или невалиден")
                return None
            
            # Пытаемся распарсить
            parsed = json.loads(json_str)
            
            # КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Проверяем, какая структура пришла
            if 'lectures' in parsed and isinstance(parsed['lectures'], list):
                # ✅ Правильная структура - возвращаем как есть
                logger.info("✅ Получена правильная структура с 'lectures'")
                if len(parsed['lectures']) == 0:
                    logger.error("В JSON нет лекций (пустой список)")
                    return None
                return parsed
                
            elif 'lesson_title' in parsed:
                # 🔄 OpenAI вернул структуру УРОКА - преобразуем в ЛЕКЦИЮ!
                logger.warning("⚠️ OpenAI вернул структуру урока вместо лекций. Преобразуем...")
                return self._convert_lesson_to_lectures(parsed)
            
            else:
                logger.error(f"❌ Неизвестная структура JSON. Доступные ключи: {list(parsed.keys())}")
                logger.debug(f"Полный JSON: {parsed}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.debug(f"Проблемный JSON: {content[:500]}...")
            return None
    
    def _extract_lesson_json(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает JSON из ответа для урока (Lesson)
        Если OpenAI вернул lectures - преобразуем обратно в lesson
        """
        try:
            # Удаляем markdown блоки если есть
            content = content.replace('```json', '').replace('```', '')
            content = content.strip()
            
            # Ищем JSON блок
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                logger.error("JSON блок не найден в ответе")
                return None
            
            json_str = content[start_idx:end_idx]
            parsed = json.loads(json_str)
            
            # Если пришла правильная структура lesson - возвращаем как есть
            if 'lesson_title' in parsed and 'lesson_goal' in parsed:
                logger.info("✅ Получена правильная структура урока (lesson)")
                return parsed
            
            # Если пришла структура lectures - берем первую лекцию и преобразуем в lesson
            elif 'lectures' in parsed and len(parsed['lectures']) > 0:
                logger.warning("⚠️ OpenAI вернул структуру lectures вместо lesson. Преобразуем обратно...")
                return self._convert_lecture_to_lesson(parsed['lectures'][0])
            
            else:
                logger.error(f"❌ Неизвестная структура JSON для урока. Ключи: {list(parsed.keys())}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка извлечения JSON урока: {e}")
            return None
    
    def _convert_lecture_to_lesson(self, lecture_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Преобразует структуру лекции (lecture) обратно в структуру урока (lesson)
        
        Получаем:
        {
          "lecture_title": "...",
          "slides": [...]
        }
        
        Преобразуем в:
        {
          "lesson_title": "...",
          "lesson_goal": "...",
          "content_outline": [...]
        }
        """
        try:
            logger.info("🔄 Преобразуем лекцию обратно в урок...")
            
            # Извлекаем данные из лекции
            lesson_title = lecture_data.get("lecture_title", "Урок без названия")
            duration = lecture_data.get("duration_minutes", 45)
            learning_objectives = lecture_data.get("learning_objectives", [])
            slides = lecture_data.get("slides", [])
            
            # Формируем цель урока из learning_objectives
            if learning_objectives:
                lesson_goal = " ".join(learning_objectives)
            else:
                lesson_goal = f"Изучить материал по теме: {lesson_title}"
            
            # Формируем план контента из слайдов
            content_outline = []
            for slide in slides:
                slide_type = slide.get("slide_type", "content")
                # Пропускаем title и summary слайды
                if slide_type not in ["title", "summary"]:
                    content_outline.append(slide.get("title", "Пункт плана"))
            
            # Если слайдов не было или все были title/summary, создаем базовый план
            if not content_outline:
                content_outline = [
                    "Теоретические основы",
                    "Практические примеры",
                    "Упражнения для закрепления"
                ]
            
            # Определяем формат на основе типов слайдов
            has_code = any(s.get("slide_type") == "code" for s in slides)
            has_quiz = any(s.get("slide_type") == "quiz" for s in slides)
            
            if has_code:
                format_type = "practice"
            elif has_quiz:
                format_type = "quiz"
            else:
                format_type = "theory"
            
            lesson = {
                "lesson_title": lesson_title,
                "lesson_goal": lesson_goal,
                "estimated_time_minutes": duration,
                "format": format_type,
                "assessment": "Тест" if has_quiz else "Практическое задание" if has_code else "Опрос",
                "content_outline": content_outline
            }
            
            logger.info(f"✅ Создан урок с {len(content_outline)} пунктами плана")
            return lesson
            
        except Exception as e:
            logger.error(f"❌ Ошибка преобразования лекции в урок: {e}")
            return None
    
    def _extract_topic_json(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает JSON из ответа для TopicMaterial
        Специальный метод для извлечения учебных материалов по теме
        """
        try:
            # Удаляем markdown блоки если есть
            content = content.replace('```json', '').replace('```', '')
            content = content.strip()
            
            # Ищем JSON блок
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                logger.error("JSON блок не найден в ответе")
                return None
            
            json_str = content[start_idx:end_idx]
            
            # Проверяем, что JSON не обрезан
            if not json_str.endswith('}'):
                logger.error("JSON обрезан или невалиден")
                return None
            
            # Пытаемся распарсить
            parsed = json.loads(json_str)
            
            # Проверяем, что это структура TopicMaterial
            required_fields = ['topic_title', 'topic_number', 'introduction', 'theory', 
                             'examples', 'key_points', 'common_mistakes', 'best_practices',
                             'practice_exercises', 'quiz_questions', 'estimated_reading_time_minutes']
            
            # Проверяем наличие ключевых полей
            missing_fields = [field for field in required_fields if field not in parsed]
            
            if missing_fields:
                logger.warning(f"⚠️ Отсутствуют поля: {missing_fields}")
                # Добавляем значения по умолчанию для отсутствующих необязательных полей
                if 'code_snippets' not in parsed:
                    parsed['code_snippets'] = []
                if 'additional_resources' not in parsed:
                    parsed['additional_resources'] = []
                
                # Если отсутствуют обязательные поля - возвращаем None
                critical_missing = [f for f in missing_fields if f in ['topic_title', 'topic_number', 'introduction', 'theory']]
                if critical_missing:
                    logger.error(f"❌ Отсутствуют критические поля: {critical_missing}")
                    return None
            
            logger.info("✅ Извлечен JSON для TopicMaterial")
            return parsed
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON для топика: {e}")
            logger.debug(f"Проблемный JSON: {content[:500]}...")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при извлечении topic JSON: {e}")
            return None
    
    def _convert_lesson_to_lectures(self, lesson_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Преобразует структуру урока (lesson) в структуру лекций (lectures)
        
        OpenAI возвращает:
        {
          "lesson_title": "...",
          "lesson_goal": "...",
          "content_outline": [...]
        }
        
        Преобразуем в:
        {
          "lectures": [
            {
              "lecture_title": "...",
              "slides": [...]
            }
          ]
        }
        """
        try:
            logger.info("🔄 Преобразуем урок в лекцию со слайдами...")
            
            # Создаем лекцию на основе урока
            lecture = {
                "lecture_title": lesson_data.get("lesson_title", "Лекция без названия"),
                "duration_minutes": lesson_data.get("estimated_time_minutes", 45),
                "learning_objectives": [
                    lesson_data.get("lesson_goal", "Изучить основные концепции"),
                    "Применить знания на практике",
                    "Закрепить материал через примеры"
                ],
                "key_takeaways": [],
                "slides": []
            }
            
            # Генерируем слайды из content_outline
            content_outline = lesson_data.get("content_outline", [])
            
            # Слайд 1: Заглавный
            lecture["slides"].append({
                "slide_number": 1,
                "title": lecture["lecture_title"],
                "content": lesson_data.get("lesson_goal", "Изучим основные концепции темы"),
                "slide_type": "title",
                "code_example": None,
                "notes": "Начните с представления темы и целей урока"
            })
            
            # Слайды 2-N: Контент из outline
            for i, topic in enumerate(content_outline, start=2):
                slide_type = "content"
                code_example = None
                
                # Определяем тип слайда по содержанию
                if "код" in topic.lower() or "пример" in topic.lower():
                    slide_type = "code"
                    code_example = f"# Пример кода для: {topic}\n# TODO: Реализовать"
                elif "диаграмм" in topic.lower() or "схем" in topic.lower():
                    slide_type = "diagram"
                
                lecture["slides"].append({
                    "slide_number": i,
                    "title": topic,
                    "content": f"Детальное рассмотрение темы:\n• {topic}\n• Практические примеры\n• Ключевые моменты",
                    "slide_type": slide_type,
                    "code_example": code_example,
                    "notes": f"Подробно объясните: {topic}"
                })
            
            # Последний слайд: Итоги
            lecture["slides"].append({
                "slide_number": len(lecture["slides"]) + 1,
                "title": "Итоги",
                "content": f"✅ Изучили: {lecture['lecture_title']}\n✅ Рассмотрели ключевые концепции\n✅ Готовы к практике",
                "slide_type": "summary",
                "code_example": None,
                "notes": "Подведите итоги и ответьте на вопросы"
            })
            
            # Заполняем key_takeaways
            lecture["key_takeaways"] = [
                f"Понимание: {lecture['lecture_title']}",
                "Практическое применение полученных знаний",
                "Готовность к следующим темам"
            ]
            
            # Возвращаем в правильной структуре
            logger.info(f"✅ Создана лекция с {len(lecture['slides'])} слайдами")
            return {
                "lectures": [lecture]
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка преобразования урока в лекцию: {e}")
            return None
    
    def _get_test_module_content(self, module: Module) -> ModuleContent:
        """Возвращает тестовый контент для демонстрации"""
        lectures = []
        
        for i, lesson in enumerate(module.lessons, 1):
            slides = [
                Slide(
                    slide_number=1,
                    title=f"{lesson.lesson_title}",
                    content=f"Добро пожаловать на урок по {lesson.lesson_title}",
                    slide_type="title",
                    notes="Приветствие и введение в тему"
                ),
                Slide(
                    slide_number=2,
                    title="Цели урока",
                    content=f"• {lesson.lesson_goal}\n• Практическое применение\n• Закрепление материала",
                    slide_type="content",
                    notes="Расскажите о целях урока"
                ),
                Slide(
                    slide_number=3,
                    title="Теоретическая часть",
                    content="• Основные концепции\n• Важные термины\n• Принципы работы",
                    slide_type="content",
                    notes="Объясните теорию с примерами"
                ),
                Slide(
                    slide_number=4,
                    title="Пример кода",
                    content="Рассмотрим практический пример",
                    slide_type="code",
                    code_example="# Пример кода\nprint('Hello, World!')",
                    notes="Разберите код построчно"
                ),
                Slide(
                    slide_number=5,
                    title="Итоги",
                    content=f"• Изучили {lesson.lesson_title}\n• Разобрали примеры\n• Готовы к практике",
                    slide_type="summary",
                    notes="Подведите итоги урока"
                )
            ]
            
            lecture = Lecture(
                lecture_title=lesson.lesson_title,
                module_number=module.module_number,
                module_title=module.module_title,
                duration_minutes=lesson.estimated_time_minutes,
                slides=slides,
                learning_objectives=[lesson.lesson_goal],
                key_takeaways=[f"Основы {lesson.lesson_title}"]
            )
            
            lectures.append(lecture)
        
        return ModuleContent(
            module_number=module.module_number,
            module_title=module.module_title,
            lectures=lectures,
            total_slides=sum(len(lecture.slides) for lecture in lectures),
            estimated_duration_minutes=sum(lecture.duration_minutes for lecture in lectures)
        )
    
    def generate_lesson_detailed_content(self, lesson: Lesson, module_number: int, 
                                        course_title: str, module_title: str,
                                        target_audience: str) -> Optional[LessonContent]:
        """
        Генерирует детальный учебный материал для каждой темы урока
        
        Args:
            lesson: Урок с планом контента
            module_number: Номер модуля
            course_title: Название курса
            module_title: Название модуля
            target_audience: Целевая аудитория
            
        Returns:
            LessonContent с детальными материалами по каждой теме
        """
        logger.info(f"Генерируем детальный контент для урока: {lesson.lesson_title}")
        logger.info(f"Темы для детализации: {len(lesson.content_outline)}")
        
        topics = []
        
        # Генерируем материал для каждой темы из плана
        for topic_number, topic_title in enumerate(lesson.content_outline, start=1):
            logger.info(f"Генерируем материал для темы {topic_number}/{len(lesson.content_outline)}: {topic_title}")
            
            topic_material = self._generate_topic_material(
                topic_number=topic_number,
                topic_title=topic_title,
                lesson=lesson,
                module_number=module_number,
                course_title=course_title,
                module_title=module_title,
                target_audience=target_audience
            )
            
            if topic_material:
                topics.append(topic_material)
            else:
                # Fallback: создаем базовый материал
                topics.append(self._get_test_topic_material(topic_number, topic_title))
        
        if not topics:
            logger.error("Не удалось сгенерировать ни одного материала по темам")
            return None
        
        total_time = sum(topic.estimated_reading_time_minutes for topic in topics)
        
        lesson_content = LessonContent(
            lesson_title=lesson.lesson_title,
            lesson_goal=lesson.lesson_goal,
            lesson_number=1,  # TODO: можно передавать извне
            module_number=module_number,
            topics=topics,
            total_topics=len(topics),
            total_estimated_time_minutes=total_time
        )
        
        logger.info(f"✅ Детальный контент создан: {len(topics)} тем, ~{total_time} мин")
        return lesson_content
    
    def _generate_topic_material(self, topic_number: int, topic_title: str,
                                lesson: Lesson, module_number: int,
                                course_title: str, module_title: str,
                                target_audience: str) -> Optional[TopicMaterial]:
        """Генерирует детальный материал для одной темы"""
        try:
            # Формируем промпт
            prompt = TOPIC_MATERIAL_PROMPT_TEMPLATE.format(
                course_title=course_title,
                target_audience=target_audience,
                module_title=module_title,
                lesson_title=lesson.lesson_title,
                lesson_goal=lesson.lesson_goal,
                topic_number=topic_number,
                topic_title=topic_title
            )
            
            # Пробуем разные методы
            response = None
            
            # Попытка 1: JSON mode
            try:
                response = self.openai_client.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": TOPIC_MATERIAL_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=4000  # Увеличиваем для детального контента
                )
                logger.info("✅ Используем JSON mode для генерации темы")
            except Exception as e:
                logger.warning(f"JSON mode не сработал: {e}")
                # Попытка 2: Обычный режим
                response = self.openai_client.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": TOPIC_MATERIAL_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
            
            if not response:
                return None
            
            content = response.choices[0].message.content.strip()
            
            # Извлекаем JSON специальным методом для TopicMaterial
            json_content = self._extract_topic_json(content)
            
            if not json_content:
                logger.warning(f"Не удалось извлечь JSON для темы: {topic_title}")
                return None
            
            # Создаем объект TopicMaterial
            topic_material = TopicMaterial(**json_content)
            logger.info(f"✅ Материал создан: {len(topic_material.examples)} примеров, {len(topic_material.quiz_questions)} вопросов")
            return topic_material
            
        except Exception as e:
            logger.error(f"Ошибка генерации материала для темы '{topic_title}': {e}")
            return None
    
    def _get_test_topic_material(self, topic_number: int, topic_title: str) -> TopicMaterial:
        """Возвращает тестовый учебный материал по теме"""
        return TopicMaterial(
            topic_title=topic_title,
            topic_number=topic_number,
            introduction=f"""
            {topic_title} — это фундаментальная концепция, которую необходимо понимать каждому разработчику. 
            
            В этом разделе мы подробно рассмотрим все аспекты темы, начиная с основ и заканчивая продвинутыми техниками. Вы узнаете не только теоретические основы, но и получите практические навыки применения знаний в реальных проектах.
            
            Материал структурирован таким образом, чтобы обеспечить постепенное погружение в тему — от простых концепций к более сложным. Каждый раздел сопровождается примерами кода и практическими упражнениями.
            """,
            theory=f"""
            Давайте начнем с базовых концепций {topic_title}.
            
            Основная идея заключается в том, что эта технология/концепция позволяет решать определенный класс задач более эффективно. Исторически эта тема развивалась в ответ на конкретные потребности разработчиков.
            
            Ключевые принципы работы базируются на нескольких фундаментальных концепциях. Во-первых, важно понимать архитектуру и структуру. Во-вторых, необходимо знать, как различные компоненты взаимодействуют между собой.
            
            Практическое применение этих знаний позволяет создавать более надежные, масштабируемые и поддерживаемые решения. Это особенно важно в контексте современной разработки, где требования к качеству кода постоянно растут.
            
            Понимание внутренних механизмов работы помогает не только правильно использовать инструменты, но и эффективно отлаживать проблемы, оптимизировать производительность и принимать обоснованные архитектурные решения.
            """,
            examples=[
                f"Пример 1: Базовое использование {topic_title}. Рассмотрим простейший случай, который демонстрирует основную концепцию.",
                f"Пример 2: Более сложный сценарий с {topic_title}. Здесь мы видим, как концепция применяется в реальной ситуации.",
                f"Пример 3: Продвинутое применение {topic_title}. Этот пример показывает возможности оптимизации и лучшие практики.",
                f"Пример 4: Интеграция {topic_title} с другими компонентами системы.",
                f"Пример 5: Обработка edge cases и нестандартных ситуаций при работе с {topic_title}."
            ],
            code_snippets=[
                f"# Базовый пример использования {topic_title}\n# Это демонстрационный код\nresult = perform_operation()\nprint(result)",
                f"# Более продвинутый пример\n# С обработкой ошибок и оптимизацией\ntry:\n    result = advanced_operation()\n    process_result(result)\nexcept Exception as e:\n    handle_error(e)",
                f"# Практический пример из реального проекта\n# Показывает интеграцию с другими компонентами\nclass Example:\n    def __init__(self):\n        self.data = initialize_data()\n    \n    def process(self):\n        return transform_data(self.data)"
            ],
            key_points=[
                f"Основная концепция {topic_title} базируется на принципе...",
                "Важно понимать разницу между различными подходами",
                "Производительность зависит от правильного выбора инструментов",
                "Безопасность должна учитываться на всех этапах",
                "Масштабируемость достигается через правильную архитектуру",
                "Тестирование — неотъемлемая часть разработки",
                "Документирование кода помогает в поддержке"
            ],
            common_mistakes=[
                "Ошибка 1: Неправильное понимание базовых концепций. Это приводит к неэффективному использованию инструментов.",
                "Ошибка 2: Игнорирование обработки ошибок. Всегда предусматривайте обработку исключительных ситуаций.",
                "Ошибка 3: Преждевременная оптимизация. Сначала сделайте работающее решение, потом оптимизируйте.",
                "Ошибка 4: Недостаточное тестирование. Покрывайте код тестами для обеспечения надежности.",
                "Ошибка 5: Копирование кода без понимания. Всегда понимайте, что делает код, прежде чем использовать."
            ],
            best_practices=[
                "Практика 1: Следуйте принципам чистого кода и используйте осмысленные имена переменных",
                "Практика 2: Разбивайте сложную логику на небольшие, понятные функции",
                "Практика 3: Документируйте нетривиальные решения и бизнес-логику",
                "Практика 4: Используйте type hints для улучшения читаемости и отлавливания ошибок",
                "Практика 5: Регулярно проводите code review и рефакторинг кода"
            ],
            practice_exercises=[
                f"Задание 1: Создайте простую программу, демонстрирующую базовое использование {topic_title}",
                f"Задание 2: Расширьте предыдущее решение, добавив обработку ошибок",
                f"Задание 3: Оптимизируйте код для повышения производительности",
                f"Задание 4: Напишите unit-тесты для вашего кода",
                f"Задание 5: Создайте мини-проект, интегрирующий {topic_title} с другими технологиями"
            ],
            quiz_questions=[
                f"Вопрос 1: Что такое {topic_title} и зачем это нужно?",
                f"Вопрос 2: Какие основные компоненты входят в {topic_title}?",
                f"Вопрос 3: В чем разница между подходом A и подходом B?",
                f"Вопрос 4: Какие проблемы решает {topic_title}?",
                f"Вопрос 5: Когда следует использовать {topic_title}, а когда нет?",
                f"Вопрос 6: Какие существуют альтернативы {topic_title}?",
                f"Вопрос 7: Как отладить проблемы, связанные с {topic_title}?"
            ],
            additional_resources=[
                "Официальная документация (ссылка)",
                "Рекомендуемая книга по теме",
                "Полезные статьи и туториалы",
                "Видео-курсы для углубленного изучения"
            ],
            estimated_reading_time_minutes=25
        )

