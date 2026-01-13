from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, date, time
import json
import os
from session import Session
from google_calendar import CalendarClient
import pytz

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

calendar_client = None
try:
    calendar_client = CalendarClient.from_env()
except Exception:
    calendar_client = None

app = FastAPI()

sessions: dict[str, Session] = {}


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


@app.post("/api/calendar/list")
async def calendar_list_endpoint(payload: CalendarListRequest):
    if calendar_client is None:
        return {"error": "Google Calendar no está configurado"}

    local_tz = pytz.timezone(os.getenv("GOOGLE_CALENDAR_TIMEZONE"))
    
    start_dt = local_tz.localize(datetime.combine(payload.day, time.min))
    end_dt = local_tz.localize(datetime.combine(payload.day, time.max))
    
    result = calendar_client.list_events(
        time_min=start_dt.isoformat(),
        time_max=end_dt.isoformat(),
        max_results=25,
    )

    def format_date(date_str: str | None) -> str:
        if not date_str:
            return ""
        try:
            clean_date = date_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_date)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return f"{date_str} 00:00:00"

    events_simplified = [
        {
            "summary": "Turno ocupado",
            "from": format_date(event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")),
            "to": format_date(event.get("end", {}).get("dateTime") or event.get("end", {}).get("date"))
        }
        for event in result.get("items", [])
    ]

    return events_simplified


@app.post("/api/calendar/create")
async def calendar_create_endpoint(payload: CalendarCreateRequest):
    if calendar_client is None:
        return {"error": "Google Calendar no está configurado"}

    timezone = os.getenv("GOOGLE_CALENDAR_TIMEZONE")
    
    local_tz = pytz.timezone(timezone)
    
    start_dt_local = local_tz.localize(payload.start_time)
    end_dt_local = local_tz.localize(payload.end_time)
    
    return calendar_client.create_event(
        summary=payload.summary,
        start_rfc3339=start_dt_local.isoformat(),
        end_rfc3339=end_dt_local.isoformat(),
        description=payload.description
    )


@app.post("/api/calendar/update")
async def calendar_update_endpoint(payload: CalendarUpdateRequest):
    if calendar_client is None:
        return {"error": "Google Calendar no está configurado"}

    timezone = os.getenv("GOOGLE_CALENDAR_TIMEZONE")

    local_tz = pytz.timezone(timezone)
    
    start_dt_local = local_tz.localize(payload.start_time)
    end_dt_local = local_tz.localize(payload.end_time)

    return calendar_client.update_event(
        event_id=payload.event_id,
        summary=payload.summary,
        start_rfc3339=start_dt_local.isoformat(),
        end_rfc3339=end_dt_local.isoformat(),
        description=payload.description
    )


@app.post("/api/calendar/delete")
async def calendar_delete_endpoint(payload: CalendarDeleteRequest):
    if calendar_client is None:
        return {"error": "Google Calendar no está configurado"}
    calendar_client.delete_event(payload.event_id)
    return {"ok": True}


@app.post("/api/session/start")
async def start_endpoint(call_sid: str):
    """Crea una nueva sesion y devuelve el mensaje de bienvenida"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    today_datetime = datetime.today().strftime('%Y-%m-%d %H:%M:%S %A')

    session.add_context(f"Se inicio una llamada, saluda al cliente. Hoy es {today_datetime}.")

    response = session.generate()

    return json.loads(response)


@app.post("/api/session/context")
async def context_endpoint(call_sid: str, context: str):
    """Inyecta contexto en el chat y devuelve un mensaje"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    session.add_context(context)

    response = session.generate()

    return json.loads(response)


@app.post("/api/session/send")
async def send_endpoint(call_sid: str, message: str):
    """Envia un mensaje como usuario"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    session.add_message("user", message)

    response = session.generate()

    return json.loads(response)


@app.delete("/api/session/end")
async def end_endpoint(call_sid: str):
    """Termina y elimina la sesion"""
    sessions.pop(call_sid, None)
