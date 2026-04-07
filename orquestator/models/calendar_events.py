from typing import Optional
from pydantic import BaseModel


class CalendarEventCreateRequest(BaseModel):
    appointment_id: str
    summary: str
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class CalendarEventUpdateRequest(BaseModel):
    id: str
    summary: Optional[str] = None
    description: Optional[str] = None