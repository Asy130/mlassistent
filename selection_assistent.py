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
**Название курса:** {course_data.get('Course Title', 'N/A')}
**Тренер:** {course_data.get('Trainer Name', 'N/A')} 
**Сертификация:** {course_data.get('Certification', {}).get('Type', 'N/A')} {course_data.get('Certification', {}).get('Level', '')}
**Уровень сложности:** {course_data.get('Difficulty Level', 'N/A')}
**Длительность:** {course_data.get('Course Duration (weeks)', 'N/A')} недель
**Частота тренировок:** {course_data.get('Weekly Training Frequency', 'N/A')}
**Длительность тренировки:** {course_data.get('Average Workout Duration', 'N/A')}

**Цели программы:** {', '.join(course_data.get('Program Goal', []))}
**Требуемое оборудование:** {', '.join(course_data.get('Required Equipment', []))}
**Рейтинг курса:** {course_data.get('Average Course Rating', 'N/A')} ({course_data.get('Number of Reviews', 0)} отзывов)
**Активные участники:** {course_data.get('Active Participants', 0)}

**Описание программы:**
{course_data.get('Program Description', 'N/A')}
"""
        return formatted

    def chat(self, request: CourseAssistantRequest) -> CourseAssistantResponse:
        session: tp.List[tp.Dict[str, str]] = self._get_session(request.session_id)

        # Первый запрос в сессии
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
