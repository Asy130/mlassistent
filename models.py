import uuid
import typing as tp
from pydantic import BaseModel

class CourseAssistantResponse(BaseModel):
    answer: str

class CourseAssistantRequest(BaseModel):
    session_id: uuid.UUID
    query: str
    user_form: str
    course_data: dict  # Теперь принимаем полные данные курса в виде словаря
