from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
import os
from session import Session
from google_calendar import CalendarClient

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("API_KEY"))

calendar_client = None
try:
    calendar_client = CalendarClient.from_env()
except Exception:
    calendar_client = None

app = FastAPI()

sessions: dict[str, Session] = {}


class CalendarListRequest(BaseModel):
    time_min: str | None = None
    time_max: str | None = None
    max_results: int = 25


class CalendarCreateRequest(BaseModel):
    summary: str
    start_rfc3339: str
    end_rfc3339: str
    description: str = ""
    timezone: str = "America/Argentina/Buenos_Aires"


class CalendarUpdateRequest(BaseModel):
    event_id: str
    summary: str | None = None
    start_rfc3339: str | None = None
    end_rfc3339: str | None = None
    description: str | None = None
    timezone: str = "America/Argentina/Buenos_Aires"


class CalendarDeleteRequest(BaseModel):
    event_id: str

@app.post("/api/start")
async def start_endpoint(call_sid: str):
    """Crea una nueva sesion y devuelve el mensaje de bienvenida"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    session.add_context("Se inicio una llamada, saluda al cliente.")

    response = session.generate()

    return json.loads(response)


@app.post("/api/calendar/list")
async def calendar_list_endpoint(payload: CalendarListRequest):
    if calendar_client is None:
        return {"error": "Google Calendar no está configurado"}
    return calendar_client.list_events(
        time_min=payload.time_min,
        time_max=payload.time_max,
        max_results=payload.max_results,
    )


@app.post("/api/calendar/create")
async def calendar_create_endpoint(payload: CalendarCreateRequest):
    if calendar_client is None:
        return {"error": "Google Calendar no está configurado"}
    return calendar_client.create_event(
        summary=payload.summary,
        start_rfc3339=payload.start_rfc3339,
        end_rfc3339=payload.end_rfc3339,
        description=payload.description,
        timezone=payload.timezone,
    )


@app.post("/api/calendar/update")
async def calendar_update_endpoint(payload: CalendarUpdateRequest):
    if calendar_client is None:
        return {"error": "Google Calendar no está configurado"}
    return calendar_client.update_event(
        event_id=payload.event_id,
        summary=payload.summary,
        start_rfc3339=payload.start_rfc3339,
        end_rfc3339=payload.end_rfc3339,
        description=payload.description,
        timezone=payload.timezone,
    )


@app.post("/api/calendar/delete")
async def calendar_delete_endpoint(payload: CalendarDeleteRequest):
    if calendar_client is None:
        return {"error": "Google Calendar no está configurado"}
    calendar_client.delete_event(payload.event_id)
    return {"ok": True}

@app.post("/api/context")
async def context_endpoint(call_sid: str, context: str):
    """Inyecta contexto en el chat y devuelve un mensaje"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    session.add_context(context)

    response = session.generate()

    return json.loads(response)

@app.post("/api/send")
async def send_endpoint(call_sid: str, message: str):
    """Envia un mensaje como usuario"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    session.add_message("user", message)

    response = session.generate()

    return json.loads(response)

@app.delete("/api/end")
async def end_endpoint(call_sid: str):
    """Termina y elimina la sesion"""
    sessions.pop(call_sid, None)
