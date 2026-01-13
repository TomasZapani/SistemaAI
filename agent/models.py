from pydantic import BaseModel
from datetime import date, datetime

class CalendarListRequest(BaseModel):
    day: date


class CalendarCreateRequest(BaseModel):
    summary: str
    start_time: datetime
    end_time: datetime
    description: str = ""


class CalendarUpdateRequest(BaseModel):
    event_id: str
    summary: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    description: str | None = None


class CalendarDeleteRequest(BaseModel):
    event_id: str