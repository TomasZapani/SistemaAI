import os
import pytz
from services.google_calendar import GoogleCalendarClient


TIMEZONE = pytz.timezone(os.getenv("GOOGLE_CALENDAR_TIMEZONE", "UTC"))

try:
    CALENDAR_CLIENT = GoogleCalendarClient.from_env()
except Exception:
    CALENDAR_CLIENT = None
