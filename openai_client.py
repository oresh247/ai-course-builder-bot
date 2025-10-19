import openai
import json
import logging
import httpx
import os
from typing import Optional, Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        # Получаем API ключ из переменных окружения
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
        
        # Настраиваем прокси из .env или используем прямое подключение
        proxy_url = os.getenv('HTTPS_PROXY') or os.getenv('HTTP_PROXY')
        
        if proxy_url:
            logger.info(f"Используем прокси для OpenAI API")
            # httpx 0.24.1 использует proxies, а не proxy
            http_client = httpx.Client(
                verify=False, 
                timeout=60.0,
                proxies=proxy_url
            )
        else:
            logger.info("Прямое подключение к OpenAI API")
            http_client = httpx.Client(verify=False, timeout=60.0)
        
        self.client = openai.OpenAI(
            api_key=api_key,
            http_client=http_client
        )
    
    def generate_course_structure(self, topic: str, audience_level: str, 
                                module_count: int, duration_weeks: int = None, 
                                hours_per_week: int = None) -> Optional[Dict[str, Any]]:
        """
        Генерирует структуру курса с помощью ChatGPT API
        """
        try:
            # Формируем промпт напрямую, без шаблона
            duration_text = ""
            if duration_weeks and hours_per_week:
                duration_text = f"Длительность — {duration_weeks} недель, {hours_per_week} часов в неделю. "
            elif duration_weeks:
                duration_text = f"Длительность — {duration_weeks} недель. "
            
            prompt = f"""Сформируй структуру IT-курса по теме "{topic}" для {audience_level} разработчиков. 
Курс должен включать {module_count} модулей, каждый из которых содержит 3–5 уроков. 
{duration_text}
Добавь цели, описание, формат и проверочные задания для каждого урока.

Ответ дай СТРОГО в JSON формате со следующей структурой:
{{
  "course_title": "название курса",
  "target_audience": "целевая аудитория",
  "duration_weeks": число_недель,
  "duration_hours": число_часов,
  "modules": [
    {{
      "module_number": 1,
      "module_title": "название модуля",
      "module_goal": "цель модуля",
      "lessons": [
        {{
          "lesson_title": "название урока",
          "lesson_goal": "цель урока",
          "content_outline": ["тема 1", "тема 2"],
          "assessment": "метод оценки",
          "format": "theory",
          "estimated_time_minutes": 60
        }}
      ]
    }}
  ]
}}"""
            
            logger.info(f"Отправляем запрос в OpenAI: {prompt[:100]}...")
            
            system_prompt = "Ты — эксперт по созданию образовательных IT-курсов. Создаёшь структурированные программы обучения с модулями, уроками и практическими заданиями. Отвечаешь строго в JSON формате."
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"Получен ответ от OpenAI: {content[:200]}...")
            
            # Пытаемся извлечь JSON из ответа
            json_content = self._extract_json_from_response(content)
            
            if json_content:
                return json_content
            else:
                logger.error("Не удалось извлечь JSON из ответа OpenAI")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при обращении к OpenAI API: {e}")
            # Возвращаем тестовую структуру курса для демонстрации
            logger.info("Возвращаем тестовую структуру курса...")
            return self._get_test_course_structure(topic, audience_level, module_count, duration_weeks, hours_per_week)
    
    def _extract_json_from_response(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает JSON из ответа ChatGPT
        """
        try:
            # Ищем JSON блок в ответе
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Если JSON не найден, пытаемся распарсить весь контент
                return json.loads(content)
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return None
    
    def generate_lesson_content(self, lesson_title: str, lesson_goal: str, 
                              format_type: str) -> Optional[str]:
        """
        Генерирует контент для урока
        """
        try:
            prompt = f"""
            Создай детальный контент для урока: "{lesson_title}"
            
            Цель урока: {lesson_goal}
            Формат: {format_type}
            
            Включи:
            - Подробный план урока
            - Теоретический материал
            - Практические задания
            - Критерии оценки
            
            Ответ дай в формате Markdown.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты — эксперт по созданию образовательного контента для IT-курсов."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при генерации контента урока: {e}")
            return None
    
    def _get_test_course_structure(self, topic: str, audience_level: str, 
                                   module_count: int, duration_weeks: int = None, 
                                   hours_per_week: int = None) -> Dict[str, Any]:
        """
        Возвращает тестовую структуру курса (для демонстрации без OpenAI API)
        """
        return {
            "course_title": f"Курс по {topic}",
            "target_audience": f"{audience_level.title()} разработчики",
            "duration_weeks": duration_weeks or 8,
            "duration_hours": (duration_weeks or 8) * (hours_per_week or 5),
            "modules": [
                {
                    "module_number": i + 1,
                    "module_title": f"Модуль {i + 1}: Основы {topic}",
                    "module_goal": f"Изучить ключевые концепции {topic}",
                    "lessons": [
                        {
                            "lesson_title": f"Урок {j + 1}: Введение",
                            "lesson_goal": "Понять основные принципы",
                            "content_outline": [
                                "Теоретическая часть",
                                "Практические примеры",
                                "Домашнее задание"
                            ],
                            "assessment": "Тест из 10 вопросов",
                            "format": "theory",
                            "estimated_time_minutes": 60
                        }
                        for j in range(3)
                    ]
                }
                for i in range(module_count)
            ]
        }
