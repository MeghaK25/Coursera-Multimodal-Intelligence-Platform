from pydantic import BaseModel, HttpUrl

class CourseRequest(BaseModel):
    course_url: HttpUrl

class ChatRequest(BaseModel):
    course_id: str
    question: str
