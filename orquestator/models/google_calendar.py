from pydantic import BaseModel
from typing import Optional


class GoogleCalendarCreate(BaseModel):
    summary: str
    start_rfc3339: str
    end_rfc3339: str
    description: Optional[str] = ""


class GoogleCalendarUpdate(BaseModel):
    summary: Optional[str] = None
    start_rfc3339: Optional[str] = None
    end_rfc3339: Optional[str] = None
    description: Optional[str] = None
