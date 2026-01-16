from pydantic import BaseModel
from datetime import date, datetime

class CalendarListRequest(BaseModel):
    day: date

class CalendarCreateRequest(BaseModel):
    summary: str
    client_name: str
    client_phone: str
    start_time: datetime
    end_time: datetime
    description: str | None = ""

class CalendarUpdateRequest(BaseModel):
    event_id: str
    summary: str | None = None
    client_name: str | None = None
    client_phone: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    description: str | None = None

class CalendarDeleteRequest(BaseModel):
    event_id: str

class CalendarSearchRequest(BaseModel):
    client_phone: str