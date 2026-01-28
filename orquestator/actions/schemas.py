from pydantic import BaseModel

class TalkData(BaseModel):
    message: str