from config import CALENDAR_CLIENT
from fastapi import APIRouter, HTTPException
from models.calendar_events import (
    CalendarEventCreateRequest,
    CalendarEventUpdateRequest
)
from services.calendar_events_service import (
    delete_calendar_event,
    get_calendar_event,
    get_calendar_event_by_appointment_id,
    get_calendar_event_by_external_id,
    list_pending_sync,
    update_external_event_id,
    update_sync_status,
    upsert_calendar_event
)

router = APIRouter(
    prefix="/calendar-event",
    tags=["Calendar Event"]
)


@router.post("/create")
async def calendar_event_create_endpoint(payload: CalendarEventCreateRequest):
    """Crea un evento de calendario vinculado a una cita existente."""
    calendar_event = upsert_calendar_event(
        appointment_id=payload.appointment_id,
        summary=payload.summary,
        description=payload.description,
        sync_status="pending"
    )
    calendar_event_id = calendar_event["id"]

    if CALENDAR_CLIENT and payload.start_time and payload.end_time:
        try:
            google_resp = CALENDAR_CLIENT.create_event(
                summary=payload.summary,
                start_rfc3339=payload.start_time,
                end_rfc3339=payload.end_time,
                description=payload.description or "",
            )

            g_id = google_resp.get("id")
            if g_id:
                update_external_event_id(id=calendar_event_id, external_event_id=g_id)
                return {
                    "status": "created",
                    "id": calendar_event_id,
                    "synced": True
                }
        except Exception as e:
            print(f"Error sincronizando Google: {e}")

    return {"status": "created", "id": calendar_event_id, "synced": False}


@router.post("/update")
async def calendar_event_update_endpoint(payload: CalendarEventUpdateRequest):
    """Actualiza un evento de calendario existente."""
    current = get_calendar_event(id=payload.id)
    if not current:
        raise HTTPException(status_code=404, detail="Evento de calendario no encontrado")

    updated_summary = payload.summary if payload.summary is not None else current["summary"]
    updated_desc = payload.description if payload.description is not None else current.get("description")

    upsert_calendar_event(
        id=payload.id,
        appointment_id=current["appointment_id"],
        external_event_id=current.get("external_event_id"),
        summary=updated_summary,
        description=updated_desc,
        sync_status="pending"
    )

    if CALENDAR_CLIENT and current.get("external_event_id"):
        try:
            appt = current.get("appointment") or {}
            CALENDAR_CLIENT.update_event(
                event_id=current["external_event_id"],
                summary=updated_summary,
                start_rfc3339=appt.get("start_time"),
                end_rfc3339=appt.get("end_time"),
                description=updated_desc or ""
            )
            update_sync_status(id=payload.id, sync_status="synced")

        except Exception as e:
            print(f"Error actualizando Google: {e}")

    return {"status": "updated", "id": payload.id}


@router.post("/delete")
async def calendar_event_delete_endpoint(payload: str):
    """Elimina un evento de calendario y lo borra en Google si está sincronizado."""
    current = get_calendar_event(id=payload)
    if not current:
        raise HTTPException(status_code=404, detail="Evento de calendario no encontrado")

    if CALENDAR_CLIENT and current.get("external_event_id"):
        try:
            CALENDAR_CLIENT.delete_event(current["external_event_id"])
        except Exception as e:
            print(f"No se pudo borrar en Google: {e}")

    delete_calendar_event(id=payload)
    return {"ok": True}


@router.get("/get/{id}")
async def calendar_event_get_endpoint(id: str):
    """Obtiene un evento de calendario por su ID interno."""
    event = get_calendar_event(id=id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento de calendario no encontrado")
    return event


@router.get("/by-appointment/{appointment_id}")
async def calendar_event_by_appointment_endpoint(appointment_id: str):
    """Obtiene el evento de calendario vinculado a una cita."""
    event = get_calendar_event_by_appointment_id(appointment_id=appointment_id)
    if not event:
        raise HTTPException(status_code=404, detail="No se encontró evento para esta cita")
    return event


@router.get("/by-external/{external_event_id}")
async def calendar_event_by_external_endpoint(external_event_id: str):
    """Obtiene un evento de calendario por su ID externo (ej: Google Calendar)."""
    event = get_calendar_event_by_external_id(external_event_id=external_event_id)
    if not event:
        raise HTTPException(status_code=404, detail="No se encontró evento con ese ID externo")
    return event


@router.get("/pending-sync")
async def calendar_event_pending_sync_endpoint():
    """Lista todos los eventos de calendario pendientes de sincronización."""
    return list_pending_sync()