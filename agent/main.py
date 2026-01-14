from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json

from services.session import Session
from services.google_calendar import GoogleCalendarClient
from models import CalendarCreateRequest, CalendarDeleteRequest, CalendarListRequest, CalendarUpdateRequest

from utils.date_utils import get_day_range, format_google_date, localize_datetime, get_now_formatted

from config import CALENDAR_CLIENT, TIMEZONE, GEMINI_CLIENT

app = FastAPI()

sessions: dict[str, Session] = {}

@app.middleware("http")
async def calendar_check(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/calendar"):
        if CALENDAR_CLIENT is None:
            return JSONResponse(
                status_code=503,
                content={"error": "Google Calendar no está configurado o las credenciales son inválidas"}
            )
    
    response = await call_next(request)
    return response


@app.post("/api/calendar/list")
async def calendar_list_endpoint(payload: CalendarListRequest):
    start_iso, end_iso = get_day_range(payload.day, TIMEZONE)
    
    result = CALENDAR_CLIENT.list_events(
        time_min=start_iso,
        time_max=end_iso,
        max_results=25,
    )

    return [
        {
            "event_id": event.get("id", "null"),
            "summary": event.get("summary", "null"),
            "status": "Turno ocupado",
            "from": format_google_date(event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")),
            "to": format_google_date(event.get("end", {}).get("dateTime") or event.get("end", {}).get("date"))
        }
        for event in result.get("items", [])
    ]


@app.post("/api/calendar/create")
async def calendar_create_endpoint(payload: CalendarCreateRequest):
    start_iso = localize_datetime(payload.start_time, TIMEZONE).isoformat()
    end_iso = localize_datetime(payload.end_time, TIMEZONE).isoformat()
    
    try:
        response = CALENDAR_CLIENT.create_event(
            summary=payload.summary,
            start_rfc3339=start_iso,
            end_rfc3339=end_iso,
            description=payload.description
        )
    except Exception as e:
        print("Error requesting create a new event:", e)
        return {"status": "error"}

    if response.get("status") != "confirmed":
        return {"status": "error"}

    return {"status": "confirmed", "event_id": response.get("id")}


@app.post("/api/calendar/update")
async def calendar_update_endpoint(payload: CalendarUpdateRequest):
    start_iso = None
    end_iso = None

    if payload.start_time:
        start_iso = localize_datetime(payload.start_time, TIMEZONE).isoformat()
    if payload.end_time:
        end_iso = localize_datetime(payload.end_time, TIMEZONE).isoformat()

    try:
        response = CALENDAR_CLIENT.update_event(
            event_id=payload.event_id,
            summary=payload.summary,
            start_rfc3339=start_iso,
            end_rfc3339=end_iso,
            description=payload.description
        )
    except Exception as e:
        print("Error requesting create a new event:", e)
        return {"status": "error"}

    if response.get("status") != "confirmed":
        return {"status": "error"}

    return {"status": "confirmed", "event_id": response.get("id")}


@app.post("/api/calendar/delete")
async def calendar_delete_endpoint(payload: CalendarDeleteRequest):
    CALENDAR_CLIENT.delete_event(payload.event_id)
    return {"ok": True}


@app.post("/api/session/start")
async def start_endpoint(call_sid: str):
    """Crea una nueva sesion y devuelve el mensaje de bienvenida"""
    if call_sid not in sessions:
        sessions[call_sid] = Session(GEMINI_CLIENT)
    
    session = sessions[call_sid]

    now = get_now_formatted()
    session.add_context(f"Se inicio una llamada, saluda al cliente. Hoy es {now}.")

    response = session.generate()

    return json.loads(response)


@app.post("/api/session/context")
async def context_endpoint(call_sid: str, context: str):
    """Inyecta contexto en el chat y devuelve un mensaje"""
    if call_sid not in sessions:
            raise HTTPException(status_code=404, detail="No se pudo finalizar: la sesión no existe.")
    
    session = sessions[call_sid]

    session.add_context(context)

    response = session.generate()

    return json.loads(response)


@app.post("/api/session/send")
async def send_endpoint(call_sid: str, message: str):
    """Envia un mensaje como usuario"""
    if call_sid not in sessions:
            raise HTTPException(status_code=404, detail="No se pudo finalizar: la sesión no existe.")
    
    session = sessions[call_sid]

    session.add_message("user", message)

    response = session.generate()

    return json.loads(response)


@app.delete("/api/session/end")
async def end_endpoint(call_sid: str):
    """Termina y elimina la sesion"""
    sessions.pop(call_sid, None)
