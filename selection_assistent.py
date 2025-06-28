import uuid
import typing as tp
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from utils import format_initial_user_prompt
from models import CourseAssistantRequest, CourseAssistantResponse
from prompts import COURSE_ASSISTANT_PROMPT as prompt

class CourseAssistant:
    def __init__(self, client: OpenAI, model: str) -> None:
        self.client: OpenAI = client
        self.model: str = model
        self.sessions: tp.Dict[uuid.UUID, tp.List[tp.Dict[str, str]]] = {}

    def _get_session(self, session_id: uuid.UUID) -> tp.List[tp.Dict[str, str]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def _format_course_data(self, course_data: dict) -> str:
        """Форматирует данные курса в читаемый текст"""
        formatted = f"""
**Основная информация:**
- Название курса: {course_data.get('Course Title', 'N/A')}
- Тип активности: {course_data.get('Activity Type', 'N/A')}
- Тренер: {course_data.get('Trainer Name', 'N/A')}
- Язык курса: {course_data.get('Course Language', 'N/A')}

**Детали программы:**
- Уровень сложности: {course_data.get('Difficulty Level', 'N/A')}
- Длительность: {course_data.get('Course Duration (weeks)', 'N/A')} недель
- Частота тренировок: {course_data.get('Weekly Training Frequency', 'N/A')}
- Средняя длительность тренировки: {course_data.get('Average Workout Duration', 'N/A')}
- Цели программы: {', '.join(course_data.get('Program Goal', [])) or 'N/A'}
- Окружение для тренировок: {', '.join(course_data.get('Training Environment', [])) or 'N/A'}
- Возрастная группа: {', '.join(course_data.get('Age Group', [])) or 'N/A'}
- Гендерная ориентация: {course_data.get('Gender Orientation', 'N/A')}
- Физические ограничения: {', '.join(course_data.get('Physical Limitations', [])) or 'Нет'}
- Необходимое оборудование: {', '.join(course_data.get('Required Equipment', [])) or 'N/A'}

**Рейтинги и статистика:**
- Средний рейтинг курса: {course_data.get('Average Course Rating', 'N/A')}
- Количество отзывов: {course_data.get('Number of Reviews', 0)}
- Активные участники: {course_data.get('Active Participants', 0)}

**Сертификация тренера:**
- Тип: {course_data.get('Certification', {}).get('Type', 'N/A')}
- Уровень: {course_data.get('Certification', {}).get('Level', 'N/A')}
- Специализация: {course_data.get('Certification', {}).get('Specialization', 'N/A')}

**Опыт тренера:**
- Стаж: {course_data.get('Experience', {}).get('Years', 'N/A')} лет
- Специализация: {course_data.get('Experience', {}).get('Specialization', 'N/A')}
- Проведено курсов: {course_data.get('Experience', {}).get('Courses', 'N/A')}
- Рейтинг тренера: {course_data.get('Experience', {}).get('Rating', 'N/A')}

**Особенности курса:**
- Визуальный контент: {', '.join(course_data.get('Visual Content', [])) or 'N/A'}
- Форматы обратной связи: {', '.join(course_data.get('Trainer Feedback Options', [])) or 'N/A'}
- Теги: {', '.join(course_data.get('Tags', [])) or 'N/A'}

**Описание программы:**
{course_data.get('Program Description', 'N/A')}

**План тренировок:**
{self._format_training_plan(course_data.get('training_plan', []))}
"""
        return formatted.strip()

    def _format_training_plan(self, training_plan: list) -> str:
        """Форматирует план тренировок"""
        if not training_plan:
            return "N/A"
        
        plan_str = ""
        for day in training_plan:
            plan_str += f"\n### {day.get('title', 'Без названия')}\n"
            for exercise in day.get('exercises', []):
                plan_str += (
                    f"- {exercise.get('exercise', 'N/A')}: "
                    f"{exercise.get('sets', 'N/A')} подход(а/ов) по "
                    f"{exercise.get('duration', 'N/A')}, "
                    f"отдых {exercise.get('rest', 'N/A')}\n"
                    f"  ({exercise.get('description', 'без описания')})\n"
                )
        return plan_str

    def chat(self, request: CourseAssistantRequest) -> CourseAssistantResponse:
        session: tp.List[tp.Dict[str, str]] = self._get_session(request.session_id)

        if not session:
            formatted_course = self._format_course_data(request.course_data)
            prompt_with_course = prompt.format(
                course_data=formatted_course,
            )
            session.append({"role": "system", "content": prompt_with_course})
            session.append(
                {
                    "role": "user",
                    "content": format_initial_user_prompt(
                        request.query, request.user_form
                    ),
                }
            )
        else:
            session.append({"role": "user", "content": request.query})

        response: ChatCompletion = self.client.chat.completions.create(
            model=self.model,
            messages=session,
        )

        session.append(
            {
                "role": "assistant",
                "content": response.choices[0].message.content,
            }
        )

        self.sessions[request.session_id] = session

        return CourseAssistantResponse(answer=response.choices[0].message.content)
