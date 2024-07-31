from pydantic import BaseModel


class Question (BaseModel):
    question : str
    image : str | None = None
    sessionId : str | None = None
