import os

import fastapi
import uvicorn
from openai import OpenAI

from models import CourseAssistantRequest
from course_assistant import CourseAssistant


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL_ID = os.getenv("MODEL_ID")

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

app = fastapi.FastAPI()
course_assistant_instance = CourseAssistant(client, MODEL_ID)


@app.post("/course-assistant-chat")
async def course_assistant(request: CourseAssistantRequest):
    return course_assistant_instance.chat(request)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
