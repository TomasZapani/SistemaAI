import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]


@dataclass
class GoogleCalendarClient:
    service: Any
    calendar_id: str
    timezone_str: str = "UTC"

    @staticmethod
    def from_env() -> "CalendarClient":
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        if not calendar_id:
            raise ValueError("Missing env var GOOGLE_CALENDAR_ID")

        tz = os.getenv("GOOGLE_CALENDAR_self.timezone_str", "UTC")

        sa_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

        if sa_path:
            creds = service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)
        elif sa_json:
            creds = service_account.Credentials.from_service_account_info(json.loads(sa_json), scopes=SCOPES)
        else:
            raise ValueError(
                "Missing service account credentials. Set GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_JSON"
            )

        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        return GoogleCalendarClient(service=service, calendar_id=calendar_id, timezone_str=tz)

    def list_events(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 25,
        single_events: bool = True,
        order_by: str = "startTime",
    ):
        return (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=single_events,
                orderBy=order_by,
            )
            .execute()
        )

    def create_event(
        self,
        summary: str,
        start_rfc3339: str,
        end_rfc3339: str,
        description: str = "",
    ):
        body = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_rfc3339, "timeZone": self.timezone_str},
            "end": {"dateTime": end_rfc3339, "timeZone": self.timezone_str},
        }
        return self.service.events().insert(calendarId=self.calendar_id, body=body).execute()

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_rfc3339: Optional[str] = None,
        end_rfc3339: Optional[str] = None,
        description: Optional[str] = None
    ):
        event = self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()

        if summary is not None:
            event["summary"] = summary
        if description is not None:
            event["description"] = description
        if start_rfc3339 is not None:
            event["start"] = {"dateTime": start_rfc3339, "timeZone": self.timezone_str}
        if end_rfc3339 is not None:
            event["end"] = {"dateTime": end_rfc3339, "timeZone": self.timezone_str}

        return self.service.events().update(calendarId=self.calendar_id, eventId=event_id, body=event).execute()

    def delete_event(self, event_id: str) -> None:
        self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()


def to_rfc3339(dt: datetime) -> str:
    if dt.tzinfo is None:
        return dt.isoformat()
    return dt.isoformat()
