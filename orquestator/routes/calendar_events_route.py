from orquestator.config import CALENDAR_CLIENT
from fastapi import APIRouter, HTTPException
from orquestator.services.calendar_events_service import (
    delete_calendar_event,
    get_calendar_event,
    get_calendar_event_by_appointment_id,
    get_calendar_event_by_external_id,
    list_pending_sync,
)


router = APIRouter(
    prefix="/calendar-event",
    tags=["Calendar Event"]
)


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
