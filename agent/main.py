from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import json


from services.session import Session
from services.google_calendar import GoogleCalendarClient
from models import CalendarCreateRequest, CalendarDeleteRequest, CalendarListRequest, CalendarUpdateRequest, CalendarSearchRequest
from services.sql_store import init_db, get_event, upsert_event, mark_deleted, list_events_sql, list_events_by_phone_sql

from utils.date_utils import get_day_range, format_google_date, localize_datetime, get_now_formatted

from config import CALENDAR_CLIENT, TIMEZONE, GEMINI_CLIENT

app = FastAPI()

init_db()

sessions: dict[str, Session] = {}


@app.post("/api/calendar/list")
async def calendar_list_endpoint(payload: CalendarListRequest):
    start_iso, end_iso = get_day_range(payload.day, TIMEZONE)
    return list_events_sql(start_iso, end_iso)


@app.post("/api/calendar/create")
async def calendar_create_endpoint(payload: CalendarCreateRequest):
    internal_id = str(uuid.uuid4())
    start_iso = localize_datetime(payload.start_time, TIMEZONE).isoformat()
    end_iso = localize_datetime(payload.end_time, TIMEZONE).isoformat()
    
    upsert_event(
        event_id=internal_id,
        summary=payload.summary,
        client_name=payload.client_name,
        client_phone=payload.client_phone,
        start_time=start_iso,
        end_time=end_iso,
        description=payload.description,
        status="confirmed",
        sync_status="pending"
    )

    if CALENDAR_CLIENT:
        try:
            google_resp = CALENDAR_CLIENT.create_event(
                summary=f"{payload.summary}: {payload.client_name}",
                start_rfc3339=start_iso,
                end_rfc3339=end_iso,
                description=f"Tel: {payload.client_phone}\n\n{payload.description}"
            )
            if google_resp.get("id"):
                upsert_event(
                    event_id=google_resp.get("id"),
                    summary=payload.summary,
                    client_name=payload.client_name,
                    client_phone=payload.client_phone,
                    start_time=start_iso,
                    end_time=end_iso,
                    description=payload.description,
                    sync_status="synced"
                )
                
                return {"status": "confirmed", "event_id": google_resp.get("id")}
        except Exception as e:
            print(f"Error sincronizando Google (Plus): {e}")

    return {"status": "confirmed", "event_id": internal_id}


@app.post("/api/calendar/update")
async def calendar_update_endpoint(payload: CalendarUpdateRequest):
    current = get_event(event_id=payload.event_id)
    if not current:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    start_iso = localize_datetime(payload.start_time, TIMEZONE).isoformat() if payload.start_time else current['start_time']
    end_iso = localize_datetime(payload.end_time, TIMEZONE).isoformat() if payload.end_time else current['end_time']
    
    updated_summary = payload.summary if payload.summary is not None else current['summary']
    updated_name = payload.client_name if payload.client_name is not None else current['client_name']
    updated_phone = payload.client_phone if payload.client_phone is not None else current['client_phone']
    updated_desc = payload.description if payload.description is not None else current['description']

    upsert_event(
        event_id=payload.event_id,
        summary=updated_summary,
        client_name=updated_name,
        client_phone=updated_phone,
        start_time=start_iso,
        end_time=end_iso,
        description=updated_desc,
        status="confirmed",
        sync_status="pending"
    )

    if CALENDAR_CLIENT:
        try:
            CALENDAR_CLIENT.update_event(
                event_id=payload.event_id,
                summary=f"{updated_summary}: {updated_name}",
                start_rfc3339=start_iso,
                end_rfc3339=end_iso,
                description=f"Tel: {updated_phone}\n{updated_desc}"
            )
            
            upsert_event(event_id=payload.event_id, summary=updated_summary, client_name=updated_name, 
                         client_phone=updated_phone, start_time=start_iso, end_time=end_iso, 
                         description=updated_desc, sync_status="synced")
        except Exception as e:
            print(f"Error actualizando Google: {e}")

    return {"status": "confirmed", "event_id": payload.event_id}


@app.post("/api/calendar/delete")
async def calendar_delete_endpoint(payload: CalendarDeleteRequest):
    mark_deleted(event_id=payload.event_id)

    if CALENDAR_CLIENT:
        try:
            CALENDAR_CLIENT.delete_event(payload.event_id)
        except Exception as e:
            print(f"No se pudo borrar en Google: {e}")

    return {"ok": True}


@app.post("/api/calendar/search")
async def calendar_search_endpoint(payload: CalendarSearchRequest):
    """
    Busca todos los turnos asociados a un número de teléfono.
    """
    events = list_events_by_phone_sql(payload.client_phone)
    return events

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

    print(json.loads(response))

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
