from typing import Optional
from supabase_conn.connection import supabase


def upsert_calendar_event(
    *,
    id: str = None,
    appointment_id: str,
    external_event_id: str = None,
    summary: str,
    description: str = None,
    sync_status: str = "pending"
) -> dict:
    """Crea o actualiza un evento de calendario. Si no se provee id, Supabase genera el UUID."""
    data = {
        "appointment_id": appointment_id,
        "external_event_id": external_event_id,
        "summary": summary,
        "description": description,
        "sync_status": sync_status,
    }

    if id:
        data["id"] = id

    result = supabase.table("calendar_events").upsert(data).execute()
    inserted_id = id or result.data[0]["id"]
    return get_calendar_event(id=inserted_id)


def get_calendar_event(*, id: str) -> Optional[dict]:
    """Obtiene un evento de calendario por su ID interno."""
    result = (
        supabase.table("calendar_events")
        .select("*, appointment:appointment_id(id, start_time, end_time, status, client_id)")
        .eq("id", id)
        .single()
        .execute()
    )

    if not result.data:
        return None

    data = result.data

    appointment_data = None
    if data.get("appointment"):
        appt = data["appointment"]
        appointment_data = {
            "id": appt["id"],
            "start_time": appt["start_time"],
            "end_time": appt["end_time"],
            "status": appt["status"],
            "client_id": appt["client_id"],
        }

    return {
        "id": data["id"],
        "appointment_id": data["appointment_id"],
        "external_event_id": data.get("external_event_id"),
        "summary": data["summary"],
        "description": data.get("description"),
        "sync_status": data["sync_status"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
        "appointment": appointment_data,
    }


def get_calendar_event_by_appointment_id(*, appointment_id: str) -> Optional[dict]:
    """Obtiene el evento de calendario vinculado a una cita."""
    result = (
        supabase.table("calendar_events")
        .select("*")
        .eq("appointment_id", appointment_id)
        .single()
        .execute()
    )

    if not result.data:
        return None

    data = result.data
    return {
        "id": data["id"],
        "appointment_id": data["appointment_id"],
        "external_event_id": data.get("external_event_id"),
        "summary": data["summary"],
        "description": data.get("description"),
        "sync_status": data["sync_status"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
    }


def get_calendar_event_by_external_id(*, external_event_id: str) -> Optional[dict]:
    """Obtiene un evento de calendario por su ID externo (ej: Google Calendar)."""
    result = (
        supabase.table("calendar_events")
        .select("*")
        .eq("external_event_id", external_event_id)
        .single()
        .execute()
    )

    if not result.data:
        return None

    data = result.data
    return {
        "id": data["id"],
        "appointment_id": data["appointment_id"],
        "external_event_id": data.get("external_event_id"),
        "summary": data["summary"],
        "description": data.get("description"),
        "sync_status": data["sync_status"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
    }


def update_sync_status(*, id: str, sync_status: str) -> None:
    """Actualiza el estado de sincronización de un evento de calendario."""
    supabase.table("calendar_events").update(
        {"sync_status": sync_status}
    ).eq("id", id).execute()


def update_external_event_id(*, id: str, external_event_id: str) -> None:
    """Actualiza el ID externo y marca como synced."""
    supabase.table("calendar_events").update(
        {"external_event_id": external_event_id, "sync_status": "synced"}
    ).eq("id", id).execute()


def list_pending_sync() -> list[dict]:
    """Lista todos los eventos de calendario con sync_status 'pending'."""
    result = (
        supabase.table("calendar_events")
        .select(
            "id, appointment_id, external_event_id, summary, description, sync_status, "
            "appointment:appointment_id(start_time, end_time, status)"
        )
        .eq("sync_status", "pending")
        .order("created_at", desc=False)
        .execute()
    )

    events = []
    for row in result.data:
        appointment_data = None
        if row.get("appointment"):
            appt = row["appointment"]
            appointment_data = {
                "start_time": appt["start_time"],
                "end_time": appt["end_time"],
                "status": appt["status"],
            }

        events.append({
            "id": row["id"],
            "appointment_id": row["appointment_id"],
            "external_event_id": row.get("external_event_id"),
            "summary": row["summary"],
            "description": row.get("description"),
            "sync_status": row["sync_status"],
            "appointment": appointment_data,
        })

    return events


def delete_calendar_event(*, id: str) -> None:
    """Elimina un evento de calendario por su ID interno."""
    supabase.table("calendar_events").delete().eq("id", id).execute()