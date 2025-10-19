"""
Модуль для экспорта курсов и контента модулей в различные форматы
"""
import json
from typing import Optional
from models import Course, ModuleContent, Lecture, Slide
from datetime import datetime


class CourseExporter:
    """Класс для экспорта курсов в различные форматы"""
    
    def export_to_json(self, course: Course) -> str:
        """Экспорт в JSON формат"""
        course_dict = course.dict()
        return json.dumps(course_dict, ensure_ascii=False, indent=2)
    
    def export_to_markdown(self, course: Course) -> str:
        """Экспорт в Markdown формат"""
        md = f"# {course.course_title}\n\n"
        md += f"**Целевая аудитория:** {course.target_audience}\n\n"
        
        if course.duration_weeks:
            md += f"**Длительность:** {course.duration_weeks} недель"
            if course.duration_hours:
                md += f" ({course.duration_hours} часов)\n\n"
            else:
                md += "\n\n"
        
        md += "---\n\n"
        md += "## 📚 Структура курса\n\n"
        
        for i, module in enumerate(course.modules, 1):
            md += f"### Модуль {i}: {module.module_title}\n\n"
            md += f"**Цель модуля:** {module.module_goal}\n\n"
            md += f"**Уроки:**\n\n"
            
            for j, lesson in enumerate(module.lessons, 1):
                md += f"#### {i}.{j} {lesson.lesson_title}\n\n"
                md += f"- **Цель:** {lesson.lesson_goal}\n"
                md += f"- **Формат:** {lesson.format}\n"
                md += f"- **Время:** {lesson.estimated_time_minutes} минут\n"
                md += f"- **Оценка:** {lesson.assessment}\n\n"
                
                if lesson.content_outline:
                    md += "**План содержания:**\n"
                    for topic in lesson.content_outline:
                        md += f"- {topic}\n"
                    md += "\n"
            
            md += "---\n\n"
        
        md += f"\n*Документ сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        return md
    
    def export_to_html(self, course: Course) -> str:
        """Экспорт в HTML формат с красивым оформлением"""
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{course.course_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .meta {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .module {{
            margin-bottom: 40px;
            border-left: 4px solid #667eea;
            padding-left: 20px;
        }}
        
        .module-header {{
            background: #f8f9fa;
            padding: 20px;
            margin-left: -20px;
            margin-bottom: 20px;
            border-radius: 10px;
        }}
        
        .module-title {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 10px;
        }}
        
        .module-goal {{
            color: #666;
            font-style: italic;
            font-size: 1.1em;
        }}
        
        .lesson {{
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 3px solid #764ba2;
        }}
        
        .lesson-title {{
            color: #764ba2;
            font-size: 1.3em;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .lesson-meta {{
            display: flex;
            gap: 20px;
            margin: 10px 0;
            flex-wrap: wrap;
        }}
        
        .meta-item {{
            background: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .meta-item strong {{
            color: #333;
        }}
        
        .content-outline {{
            margin-top: 15px;
        }}
        
        .content-outline h4 {{
            color: #555;
            margin-bottom: 10px;
        }}
        
        .content-outline ul {{
            list-style-position: inside;
            color: #666;
        }}
        
        .content-outline li {{
            padding: 5px 0;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 5px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 {course.course_title}</h1>
            <div class="meta">
                <p>👥 {course.target_audience}</p>
"""
        
        if course.duration_weeks:
            html += f"                <p>⏱️ {course.duration_weeks} недель"
            if course.duration_hours:
                html += f" • {course.duration_hours} часов"
            html += "</p>\n"
        
        html += f"""                <p>📚 {len(course.modules)} модулей</p>
            </div>
        </div>
        
        <div class="content">
"""
        
        # Добавляем модули
        for i, module in enumerate(course.modules, 1):
            html += f"""            <div class="module">
                <div class="module-header">
                    <div class="module-title">Модуль {i}: {module.module_title}</div>
                    <div class="module-goal">🎯 {module.module_goal}</div>
                </div>
                
"""
            
            # Добавляем уроки
            for j, lesson in enumerate(module.lessons, 1):
                html += f"""                <div class="lesson">
                    <div class="lesson-title">{i}.{j} {lesson.lesson_title}</div>
                    <p><strong>Цель:</strong> {lesson.lesson_goal}</p>
                    
                    <div class="lesson-meta">
                        <span class="meta-item"><strong>Формат:</strong> {lesson.format}</span>
                        <span class="meta-item"><strong>Время:</strong> {lesson.estimated_time_minutes} мин</span>
                        <span class="meta-item"><strong>Оценка:</strong> {lesson.assessment}</span>
                    </div>
"""
                
                if lesson.content_outline:
                    html += """                    
                    <div class="content-outline">
                        <h4>📋 План содержания:</h4>
                        <ul>
"""
                    for topic in lesson.content_outline:
                        html += f"                            <li>{topic}</li>\n"
                    
                    html += """                        </ul>
                    </div>
"""
                
                html += "                </div>\n\n"
            
            html += "            </div>\n\n"
        
        html += f"""        </div>
        
        <div class="footer">
            <p>📄 Документ создан: {datetime.now().strftime('%d.%m.%Y в %H:%M')}</p>
            <p>🤖 Сгенерировано AI Course Builder</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def export_to_txt(self, course: Course) -> str:
        """Экспорт в простой TXT формат"""
        txt = f"{'='*80}\n"
        txt += f"{course.course_title.upper().center(80)}\n"
        txt += f"{'='*80}\n\n"
        
        txt += f"Целевая аудитория: {course.target_audience}\n"
        if course.duration_weeks:
            txt += f"Длительность: {course.duration_weeks} недель"
            if course.duration_hours:
                txt += f" ({course.duration_hours} часов)"
            txt += "\n"
        
        txt += f"Количество модулей: {len(course.modules)}\n\n"
        txt += f"{'-'*80}\n\n"
        
        for i, module in enumerate(course.modules, 1):
            txt += f"МОДУЛЬ {i}: {module.module_title.upper()}\n"
            txt += f"{'-'*80}\n"
            txt += f"Цель: {module.module_goal}\n\n"
            
            for j, lesson in enumerate(module.lessons, 1):
                txt += f"  {i}.{j} {lesson.lesson_title}\n"
                txt += f"      Цель: {lesson.lesson_goal}\n"
                txt += f"      Формат: {lesson.format} | Время: {lesson.estimated_time_minutes} мин | Оценка: {lesson.assessment}\n"
                
                if lesson.content_outline:
                    txt += f"      План содержания:\n"
                    for topic in lesson.content_outline:
                        txt += f"        • {topic}\n"
                txt += "\n"
            
            txt += f"{'-'*80}\n\n"
        
        txt += f"\nДокумент создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        txt += f"Сгенерировано: AI Course Builder\n"
        txt += f"{'='*80}\n"
        
        return txt
    
    # ========== ЭКСПОРТ КОНТЕНТА МОДУЛЕЙ ==========
    
    def export_module_content_to_json(self, content: ModuleContent) -> str:
        """Экспорт контента модуля в JSON"""
        content_dict = content.dict()
        return json.dumps(content_dict, ensure_ascii=False, indent=2)
    
    def export_module_content_to_html(self, content: ModuleContent) -> str:
        """Экспорт контента модуля в HTML (презентация)"""
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.module_title} - Лекции</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
        }}
        
        .presentation {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .lecture {{
            margin-bottom: 60px;
        }}
        
        .lecture-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .lecture-title {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}
        
        .lecture-meta {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .objectives {{
            background: #16213e;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }}
        
        .objectives h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .objectives ul {{
            list-style-position: inside;
            line-height: 1.8;
        }}
        
        .slide {{
            background: white;
            color: #333;
            padding: 50px;
            margin-bottom: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            min-height: 500px;
            position: relative;
        }}
        
        .slide-number {{
            position: absolute;
            top: 20px;
            right: 30px;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9em;
        }}
        
        .slide-title {{
            font-size: 2.2em;
            color: #764ba2;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        
        .slide.title-slide {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        
        .slide.title-slide .slide-title {{
            color: white;
            border: none;
            font-size: 3em;
        }}
        
        .slide-content {{
            font-size: 1.3em;
            line-height: 1.8;
            white-space: pre-line;
        }}
        
        .code-example {{
            background: #1a1a2e;
            color: #eee;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            white-space: pre;
            border-left: 4px solid #667eea;
        }}
        
        .notes {{
            background: #fff3cd;
            color: #856404;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            border-left: 4px solid #ffc107;
        }}
        
        .notes h4 {{
            margin-bottom: 10px;
            color: #856404;
        }}
        
        .takeaways {{
            background: #d4edda;
            color: #155724;
            padding: 30px;
            border-radius: 15px;
            margin-top: 30px;
            border-left: 5px solid #28a745;
        }}
        
        .takeaways h3 {{
            color: #28a745;
            margin-bottom: 15px;
        }}
        
        @media print {{
            .slide {{
                page-break-after: always;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation">
        <div class="lecture-header">
            <div class="lecture-title">Модуль {content.module_number}</div>
            <h1>{content.module_title}</h1>
            <div class="lecture-meta">
                {len(content.lectures)} лекций • {content.total_slides} слайдов • {content.estimated_duration_minutes} минут
            </div>
        </div>
"""
        
        for lecture in content.lectures:
            html += f"""
        <div class="lecture">
            <div class="objectives">
                <h3>🎯 Цели обучения</h3>
                <ul>
"""
            for obj in lecture.learning_objectives:
                html += f"                    <li>{obj}</li>\n"
            
            html += """                </ul>
            </div>
"""
            
            # Добавляем слайды
            for slide in lecture.slides:
                slide_class = "title-slide" if slide.slide_type == "title" else ""
                html += f"""
            <div class="slide {slide_class}">
                <div class="slide-number">Слайд {slide.slide_number}</div>
                <h2 class="slide-title">{slide.title}</h2>
                <div class="slide-content">{slide.content}</div>
"""
                
                if slide.code_example:
                    html += f"""
                <div class="code-example">{slide.code_example}</div>
"""
                
                if slide.notes:
                    html += f"""
                <div class="notes">
                    <h4>📝 Заметки для преподавателя:</h4>
                    <p>{slide.notes}</p>
                </div>
"""
                
                html += "            </div>\n"
            
            # Ключевые выводы лекции
            html += """
            <div class="takeaways">
                <h3>✨ Ключевые выводы</h3>
                <ul>
"""
            for takeaway in lecture.key_takeaways:
                html += f"                    <li>{takeaway}</li>\n"
            
            html += """                </ul>
            </div>
        </div>
"""
        
        html += f"""
    </div>
    <div style="text-align: center; padding: 40px; color: #888;">
        <p>📄 Создано: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        <p>🤖 AI Course Builder</p>
    </div>
</body>
</html>"""
        
        return html
    
    def export_module_content_to_markdown(self, content: ModuleContent) -> str:
        """Экспорт контента модуля в Markdown"""
        md = f"# Модуль {content.module_number}: {content.module_title}\n\n"
        md += f"**Лекций:** {len(content.lectures)} • **Слайдов:** {content.total_slides} • **Время:** {content.estimated_duration_minutes} минут\n\n"
        md += "---\n\n"
        
        for lecture in content.lectures:
            md += f"## 📚 {lecture.lecture_title}\n\n"
            md += f"**Длительность:** {lecture.duration_minutes} минут\n\n"
            
            md += "### 🎯 Цели обучения\n\n"
            for obj in lecture.learning_objectives:
                md += f"- {obj}\n"
            md += "\n"
            
            md += "### 📊 Слайды\n\n"
            
            for slide in lecture.slides:
                md += f"#### Слайд {slide.slide_number}: {slide.title}\n\n"
                md += f"**Тип:** {slide.slide_type}\n\n"
                md += f"{slide.content}\n\n"
                
                if slide.code_example:
                    md += "```python\n"
                    md += f"{slide.code_example}\n"
                    md += "```\n\n"
                
                if slide.notes:
                    md += f"> 📝 **Заметки:** {slide.notes}\n\n"
            
            md += "### ✨ Ключевые выводы\n\n"
            for takeaway in lecture.key_takeaways:
                md += f"- {takeaway}\n"
            md += "\n---\n\n"
        
        md += f"\n*Документ создан: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        return md
    
    def export_module_content_to_txt(self, content: ModuleContent) -> str:
        """Экспорт контента модуля в TXT"""
        txt = f"{'='*80}\n"
        txt += f"МОДУЛЬ {content.module_number}: {content.module_title.upper()}\n"
        txt += f"{'='*80}\n\n"
        txt += f"Лекций: {len(content.lectures)} | Слайдов: {content.total_slides} | Время: {content.estimated_duration_minutes} мин\n\n"
        
        for lecture in content.lectures:
            txt += f"{'-'*80}\n"
            txt += f"ЛЕКЦИЯ: {lecture.lecture_title}\n"
            txt += f"{'-'*80}\n"
            txt += f"Длительность: {lecture.duration_minutes} минут\n\n"
            
            txt += "ЦЕЛИ ОБУЧЕНИЯ:\n"
            for obj in lecture.learning_objectives:
                txt += f"  • {obj}\n"
            txt += "\n"
            
            for slide in lecture.slides:
                txt += f"  [{slide.slide_number}] {slide.title}\n"
                txt += f"  Тип: {slide.slide_type}\n"
                txt += f"  {'-'*76}\n"
                
                for line in slide.content.split('\n'):
                    txt += f"    {line}\n"
                
                if slide.code_example:
                    txt += f"\n    КОД:\n"
                    for line in slide.code_example.split('\n'):
                        txt += f"    {line}\n"
                
                if slide.notes:
                    txt += f"\n    [Заметки: {slide.notes}]\n"
                
                txt += "\n"
            
            txt += "КЛЮЧЕВЫЕ ВЫВОДЫ:\n"
            for takeaway in lecture.key_takeaways:
                txt += f"  ✓ {takeaway}\n"
            txt += "\n\n"
        
        txt += f"{'='*80}\n"
        txt += f"Создано: {datetime.now().strftime('%d.%m.%Y %H:%M')} | AI Course Builder\n"
        txt += f"{'='*80}\n"
        
        return txt
    
    # ==================== ЭКСПОРТ ДЕТАЛЬНЫХ МАТЕРИАЛОВ УРОКА ====================
    
    def export_lesson_content_to_json(self, lesson_content) -> str:
        """Экспорт детальных материалов урока в JSON"""
        from models import LessonContent
        if isinstance(lesson_content, LessonContent):
            lesson_dict = lesson_content.dict()
        else:
            lesson_dict = lesson_content
        return json.dumps(lesson_dict, ensure_ascii=False, indent=2)
    
    def export_lesson_content_to_html(self, lesson_content) -> str:
        """Экспорт детальных материалов урока в HTML"""
        from models import LessonContent
        
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{lesson_content.lesson_title} - Детальные материалы</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .topic {{
            margin-bottom: 60px;
            border-left: 4px solid #667eea;
            padding-left: 20px;
        }}
        
        .topic-header {{
            background: #f8f9fa;
            padding: 20px;
            margin-left: -20px;
            margin-bottom: 20px;
            border-radius: 8px;
        }}
        
        .topic-title {{
            font-size: 2em;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .section {{
            margin: 30px 0;
        }}
        
        .section-title {{
            font-size: 1.3em;
            color: #764ba2;
            margin-bottom: 15px;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        
        .introduction, .theory {{
            white-space: pre-wrap;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        
        .example-item, .exercise-item, .question-item {{
            background: #fff;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }}
        
        .code-block {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            white-space: pre;
            margin: 15px 0;
        }}
        
        .key-point {{
            background: #e7f3ff;
            padding: 10px 15px;
            margin: 8px 0;
            border-left: 4px solid #2196F3;
            border-radius: 4px;
        }}
        
        .mistake {{
            background: #fff3cd;
            padding: 10px 15px;
            margin: 8px 0;
            border-left: 4px solid #ff9800;
            border-radius: 4px;
        }}
        
        .best-practice {{
            background: #d4edda;
            padding: 10px 15px;
            margin: 8px 0;
            border-left: 4px solid #28a745;
            border-radius: 4px;
        }}
        
        .resource {{
            background: #e8f5e9;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 4px;
        }}
        
        .time-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 10px 0;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📖 {lesson_content.lesson_title}</h1>
            <p>{lesson_content.lesson_goal}</p>
            <div style="margin-top: 20px;">
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; margin-right: 10px;">
                    Модуль {lesson_content.module_number}
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">
                    {lesson_content.total_topics} тем
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">
                    ~{lesson_content.total_estimated_time_minutes} минут
                </span>
            </div>
        </div>
        
        <div class="content">
"""
        
        for idx, topic in enumerate(lesson_content.topics, 1):
            html += f"""
            <div class="topic">
                <div class="topic-header">
                    <div class="topic-title">Тема {idx}: {topic.topic_title}</div>
                    <p>{topic.topic_description if hasattr(topic, 'topic_description') else ''}</p>
                    <span class="time-badge">⏱️ ~{topic.estimated_reading_time_minutes} минут</span>
                </div>
                
                <div class="section">
                    <div class="section-title">📝 Введение</div>
                    <div class="introduction">{topic.introduction}</div>
                </div>
                
                <div class="section">
                    <div class="section-title">📚 Теория</div>
                    <div class="theory">{topic.theory}</div>
                </div>
"""
            
            if topic.examples:
                html += """
                <div class="section">
                    <div class="section-title">💡 Примеры</div>
"""
                for i, example in enumerate(topic.examples, 1):
                    html += f'<div class="example-item"><strong>Пример {i}:</strong> {example}</div>\n'
                html += "</div>\n"
            
            if topic.code_snippets:
                html += """
                <div class="section">
                    <div class="section-title">💻 Примеры кода</div>
"""
                for i, code in enumerate(topic.code_snippets, 1):
                    html += f'<div class="code-block">{code}</div>\n'
                html += "</div>\n"
            
            if topic.key_points:
                html += """
                <div class="section">
                    <div class="section-title">🎯 Ключевые моменты</div>
"""
                for point in topic.key_points:
                    html += f'<div class="key-point">✓ {point}</div>\n'
                html += "</div>\n"
            
            if topic.common_mistakes:
                html += """
                <div class="section">
                    <div class="section-title">⚠️ Частые ошибки</div>
"""
                for mistake in topic.common_mistakes:
                    html += f'<div class="mistake">⚠️ {mistake}</div>\n'
                html += "</div>\n"
            
            if topic.best_practices:
                html += """
                <div class="section">
                    <div class="section-title">✨ Лучшие практики</div>
"""
                for practice in topic.best_practices:
                    html += f'<div class="best-practice">✓ {practice}</div>\n'
                html += "</div>\n"
            
            if topic.practice_exercises:
                html += """
                <div class="section">
                    <div class="section-title">🏋️ Упражнения для практики</div>
"""
                for i, exercise in enumerate(topic.practice_exercises, 1):
                    html += f'<div class="exercise-item"><strong>Задание {i}:</strong> {exercise}</div>\n'
                html += "</div>\n"
            
            if topic.quiz_questions:
                html += """
                <div class="section">
                    <div class="section-title">❓ Вопросы для самопроверки</div>
"""
                for i, question in enumerate(topic.quiz_questions, 1):
                    html += f'<div class="question-item">{i}. {question}</div>\n'
                html += "</div>\n"
            
            if hasattr(topic, 'additional_resources') and topic.additional_resources:
                html += """
                <div class="section">
                    <div class="section-title">📚 Дополнительные ресурсы</div>
"""
                for resource in topic.additional_resources:
                    html += f'<div class="resource">🔗 {resource}</div>\n'
                html += "</div>\n"
            
            html += "</div>\n"
        
        html += f"""
        </div>
        
        <div class="footer">
            <p>Создано: {datetime.now().strftime('%d.%m.%Y %H:%M')} | AI Course Builder</p>
            <p>Урок: {lesson_content.lesson_title} | Модуль {lesson_content.module_number}</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def export_lesson_content_to_markdown(self, lesson_content) -> str:
        """Экспорт детальных материалов урока в Markdown"""
        from models import LessonContent
        
        md = f"# {lesson_content.lesson_title}\n\n"
        md += f"**Цель урока:** {lesson_content.lesson_goal}\n\n"
        md += f"**Модуль:** {lesson_content.module_number} | **Урок:** {lesson_content.lesson_number}\n"
        md += f"**Тем:** {lesson_content.total_topics} | **Время изучения:** ~{lesson_content.total_estimated_time_minutes} минут\n\n"
        md += "---\n\n"
        
        for idx, topic in enumerate(lesson_content.topics, 1):
            md += f"## Тема {idx}: {topic.topic_title}\n\n"
            
            if hasattr(topic, 'topic_description'):
                md += f"*{topic.topic_description}*\n\n"
            
            md += f"⏱️ Время изучения: ~{topic.estimated_reading_time_minutes} минут\n\n"
            
            md += f"### 📝 Введение\n\n"
            md += f"{topic.introduction}\n\n"
            
            md += f"### 📚 Теория\n\n"
            md += f"{topic.theory}\n\n"
            
            if topic.examples:
                md += f"### 💡 Примеры\n\n"
                for i, example in enumerate(topic.examples, 1):
                    md += f"{i}. {example}\n\n"
            
            if topic.code_snippets:
                md += f"### 💻 Примеры кода\n\n"
                for code in topic.code_snippets:
                    md += f"```python\n{code}\n```\n\n"
            
            if topic.key_points:
                md += f"### 🎯 Ключевые моменты\n\n"
                for point in topic.key_points:
                    md += f"- ✓ {point}\n"
                md += "\n"
            
            if topic.common_mistakes:
                md += f"### ⚠️ Частые ошибки\n\n"
                for mistake in topic.common_mistakes:
                    md += f"- ⚠️ {mistake}\n"
                md += "\n"
            
            if topic.best_practices:
                md += f"### ✨ Лучшие практики\n\n"
                for practice in topic.best_practices:
                    md += f"- ✓ {practice}\n"
                md += "\n"
            
            if topic.practice_exercises:
                md += f"### 🏋️ Упражнения для практики\n\n"
                for i, exercise in enumerate(topic.practice_exercises, 1):
                    md += f"{i}. {exercise}\n"
                md += "\n"
            
            if topic.quiz_questions:
                md += f"### ❓ Вопросы для самопроверки\n\n"
                for i, question in enumerate(topic.quiz_questions, 1):
                    md += f"{i}. {question}\n"
                md += "\n"
            
            if hasattr(topic, 'additional_resources') and topic.additional_resources:
                md += f"### 📚 Дополнительные ресурсы\n\n"
                for resource in topic.additional_resources:
                    md += f"- 🔗 {resource}\n"
                md += "\n"
            
            md += "---\n\n"
        
        md += f"\n*Документ сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M')} | AI Course Builder*\n"
        return md
    
    def export_lesson_content_to_txt(self, lesson_content) -> str:
        """Экспорт детальных материалов урока в TXT"""
        from models import LessonContent
        
        txt = f"{'='*80}\n"
        txt += f"ДЕТАЛЬНЫЕ УЧЕБНЫЕ МАТЕРИАЛЫ\n"
        txt += f"{'='*80}\n\n"
        
        txt += f"УРОК: {lesson_content.lesson_title}\n"
        txt += f"ЦЕЛЬ: {lesson_content.lesson_goal}\n"
        txt += f"МОДУЛЬ: {lesson_content.module_number} | УРОК: {lesson_content.lesson_number}\n"
        txt += f"ТЕМ: {lesson_content.total_topics} | ВРЕМЯ: ~{lesson_content.total_estimated_time_minutes} минут\n\n"
        txt += f"{'-'*80}\n\n"
        
        for idx, topic in enumerate(lesson_content.topics, 1):
            txt += f"\n{'='*80}\n"
            txt += f"ТЕМА {idx}: {topic.topic_title.upper()}\n"
            txt += f"{'='*80}\n\n"
            
            if hasattr(topic, 'topic_description'):
                txt += f"{topic.topic_description}\n\n"
            
            txt += f"Время изучения: ~{topic.estimated_reading_time_minutes} минут\n\n"
            
            txt += f"{'-'*80}\n"
            txt += f"ВВЕДЕНИЕ\n"
            txt += f"{'-'*80}\n\n"
            txt += f"{topic.introduction}\n\n"
            
            txt += f"{'-'*80}\n"
            txt += f"ТЕОРИЯ\n"
            txt += f"{'-'*80}\n\n"
            txt += f"{topic.theory}\n\n"
            
            if topic.examples:
                txt += f"{'-'*80}\n"
                txt += f"ПРИМЕРЫ\n"
                txt += f"{'-'*80}\n\n"
                for i, example in enumerate(topic.examples, 1):
                    txt += f"{i}. {example}\n\n"
            
            if topic.code_snippets:
                txt += f"{'-'*80}\n"
                txt += f"ПРИМЕРЫ КОДА\n"
                txt += f"{'-'*80}\n\n"
                for i, code in enumerate(topic.code_snippets, 1):
                    txt += f"Пример {i}:\n{code}\n\n"
            
            if topic.key_points:
                txt += f"{'-'*80}\n"
                txt += f"КЛЮЧЕВЫЕ МОМЕНТЫ\n"
                txt += f"{'-'*80}\n\n"
                for point in topic.key_points:
                    txt += f"  ✓ {point}\n"
                txt += "\n"
            
            if topic.common_mistakes:
                txt += f"{'-'*80}\n"
                txt += f"ЧАСТЫЕ ОШИБКИ\n"
                txt += f"{'-'*80}\n\n"
                for mistake in topic.common_mistakes:
                    txt += f"  ⚠ {mistake}\n"
                txt += "\n"
            
            if topic.best_practices:
                txt += f"{'-'*80}\n"
                txt += f"ЛУЧШИЕ ПРАКТИКИ\n"
                txt += f"{'-'*80}\n\n"
                for practice in topic.best_practices:
                    txt += f"  ✓ {practice}\n"
                txt += "\n"
            
            if topic.practice_exercises:
                txt += f"{'-'*80}\n"
                txt += f"УПРАЖНЕНИЯ ДЛЯ ПРАКТИКИ\n"
                txt += f"{'-'*80}\n\n"
                for i, exercise in enumerate(topic.practice_exercises, 1):
                    txt += f"{i}. {exercise}\n"
                txt += "\n"
            
            if topic.quiz_questions:
                txt += f"{'-'*80}\n"
                txt += f"ВОПРОСЫ ДЛЯ САМОПРОВЕРКИ\n"
                txt += f"{'-'*80}\n\n"
                for i, question in enumerate(topic.quiz_questions, 1):
                    txt += f"{i}. {question}\n"
                txt += "\n"
            
            if hasattr(topic, 'additional_resources') and topic.additional_resources:
                txt += f"{'-'*80}\n"
                txt += f"ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ\n"
                txt += f"{'-'*80}\n\n"
                for resource in topic.additional_resources:
                    txt += f"  • {resource}\n"
                txt += "\n"
        
        txt += f"\n{'='*80}\n"
        txt += f"Создано: {datetime.now().strftime('%d.%m.%Y %H:%M')} | AI Course Builder\n"
        txt += f"{'='*80}\n"
        
        return txt

