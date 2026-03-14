from config import CALENDAR_CLIENT, TIMEZONE
from fastapi import APIRouter, HTTPException
from models import (
    AppointmentCreateRequest,
    AppointmentListRequest,
    AppointmentUpdateRequest
)
from services.appointment_service import (
    get_appointment,
    list_events_by_phone_sql,
    list_events_sql,
    mark_deleted,
    upsert_appointment
)
from utils.date_utils import (
    get_day_range,
    localize_datetime
)
from services.calendar_events_service import (
    update_external_event_id,
    update_sync_status,
    upsert_calendar_event
)
from services.client_service import get_client
from utils.date_utils import get_day_range, localize_datetime

router = APIRouter(
    prefix="/appointment",
    tags=["Appointment"]
)


@router.post("/list")
async def appointment_list_endpoint(payload: AppointmentListRequest):
    start_iso, end_iso = get_day_range(payload.day, TIMEZONE)
    return list_events_sql(start_iso, end_iso)


@router.post("/create")
async def appointment_create_endpoint(payload: AppointmentCreateRequest):
    # 1. Obtener datos del cliente
    client = get_client(id=payload.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    client_name = client["name"]
    client_phone = client["phone"]

    start_iso = localize_datetime(payload.start_time, TIMEZONE).isoformat()
    end_iso = localize_datetime(payload.end_time, TIMEZONE).isoformat()

    # 2. Crear la cita en Supabase
    appointment = upsert_appointment(
        client_id=payload.client_id,
        start_time=start_iso,
        end_time=end_iso,
        status="confirmed",
        sync_status="pending"
    )
    appointment_id = appointment["id"]

    # 3. Crear el evento de calendario vinculado a la cita
    calendar_event = upsert_calendar_event(
        appointment_id=appointment_id,
        summary=payload.summary,
        description=payload.description,
        sync_status="pending"
    )
    calendar_event_id = calendar_event["id"]

    # 4. Sincronizar con Google Calendar
    if CALENDAR_CLIENT:
        try:
            google_resp = CALENDAR_CLIENT.create_event(
                summary=f"{payload.summary}: {client_name}",
                start_rfc3339=start_iso,
                end_rfc3339=end_iso,
                description=(
                    f"Nombre: {client_name}\n\n"
                    f"Tel: {client_phone}\n\n"
                    f"{payload.description or ''}"
                ),
            )

            g_id = google_resp.get("id")
            if g_id:
                update_external_event_id(id=calendar_event_id, external_event_id=g_id)
                upsert_appointment(
                    id=appointment_id,
                    client_id=payload.client_id,
                    start_time=start_iso,
                    end_time=end_iso,
                    status="confirmed",
                    sync_status="synced"
                )
                return {"status": "confirmed", "id": appointment_id, "synced": True}
        except Exception as e:
            print(f"Error sincronizando Google: {e}")

    return {"status": "confirmed", "id": appointment_id, "synced": False}


@router.post("/update")
async def appointment_update_endpoint(payload: AppointmentUpdateRequest):
    # 1. Obtener cita actual con cliente y calendar_event anidados
    current = get_appointment(id=payload.id)
    if not current:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    current_cal = current.get("calendar_event") or {}
    current_client = current.get("client") or {}

    start_iso = (
        localize_datetime(payload.start_time, TIMEZONE).isoformat()
        if payload.start_time
        else current["start_time"]
    )
    end_iso = (
        localize_datetime(payload.end_time, TIMEZONE).isoformat()
        if payload.end_time
        else current["end_time"]
    )

    updated_summary = payload.summary if payload.summary is not None else current_cal.get("summary")
    updated_desc = payload.description if payload.description is not None else current_cal.get("description")

    upsert_appointment(
        id=payload.id,
        client_id=current["client_id"],
        start_time=start_iso,
        end_time=end_iso,
        status=current["status"],
        sync_status="pending"
    )

    if current_cal.get("id"):
        upsert_calendar_event(
            id=current_cal["id"],
            appointment_id=payload.id,
            external_event_id=current_cal.get("external_event_id"),
            summary=updated_summary,
            description=updated_desc,
            sync_status="pending"
        )

    if CALENDAR_CLIENT and current_cal.get("external_event_id"):
        try:
            CALENDAR_CLIENT.update_event(
                event_id=current_cal["external_event_id"],
                summary=f"{updated_summary}: {current_client.get('name', '')}",
                start_rfc3339=start_iso,
                end_rfc3339=end_iso,
                description=f"Tel: {current_client.get('phone', '')}\n{updated_desc or ''}"
            )
            upsert_appointment(
                id=payload.id,
                client_id=current["client_id"],
                start_time=start_iso,
                end_time=end_iso,
                status=current["status"],
                sync_status="synced"
            )
            if current_cal.get("id"):
                update_sync_status(id=current_cal["id"], sync_status="synced")
        except Exception as e:
            print(f"Error actualizando Google: {e}")

    return {"status": "confirmed", "id": payload.id}


@router.post("/delete")
async def appointment_delete_endpoint(payload: str):
    # 1. Obtener cita para tener el external_event_id antes de borrar
    current = get_appointment(id=payload)
    if not current:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    mark_deleted(id=payload)

    if CALENDAR_CLIENT:
        cal_ev = current.get("calendar_event") or {}
        external_id = cal_ev.get("external_event_id")
        if external_id:
            try:
                CALENDAR_CLIENT.delete_event(external_id)
            except Exception as e:
                print(f"No se pudo borrar en Google: {e}")

    return {"ok": True}


@router.post("/search")
async def appointment_search_endpoint(payload: str):
    """Busca todos los turnos asociados a un número de teléfono."""
    return list_events_by_phone_sql(payload.client_phone)