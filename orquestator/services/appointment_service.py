from typing import Optional
from supabase_conn.connection import supabase


def upsert_appointment(
    *,
    id: str = None,
    client_id: str,
    start_time: str,
    end_time: str,
    status: str = "confirmed",
    sync_status: str = "pending"
) -> dict:
    """Crea o actualiza una cita. Si no se provee id, Supabase genera el UUID."""
    data = {
        "client_id": client_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "sync_status": sync_status,
    }

    if id:
        data["id"] = id

    result = supabase.table("appointments").upsert(data).execute()
    inserted_id = id or result.data[0]["id"]
    return get_appointment(id=inserted_id)


def mark_deleted(*, id: str) -> None:
    """Marca como borrado usando el ID interno."""
    update_data = {
        "status": "deleted",
        "sync_status": "pending"
    }
    supabase.table("appointments").update(update_data).eq("id", id).execute()


def get_appointment(*, id: str) -> Optional[dict]:
    """Obtiene una cita por su ID interno con datos del cliente y del evento de calendario."""
    result = (
        supabase.table("appointments")
        .select("*, client:client_id(name, phone), calendar_events(*)")
        .eq("id", id)
        .single()
        .execute()
    )

    if not result.data:
        return None

    data = result.data

    client_data = None
    if data.get("client"):
        client_data = {
            "name": data["client"]["name"],
            "phone": data["client"]["phone"]
        }

    calendar_event = None
    if data.get("calendar_events"):
        ev = data["calendar_events"]
        if isinstance(ev, list) and ev:
            ev = ev[0]
        if isinstance(ev, dict):
            calendar_event = {
                "id": ev["id"],
                "external_event_id": ev.get("external_event_id"),
                "summary": ev.get("summary"),
                "description": ev.get("description"),
                "sync_status": ev.get("sync_status"),
                "created_at": ev.get("created_at"),
                "updated_at": ev.get("updated_at"),
            }

    return {
        "id": data["id"],
        "client_id": data["client_id"],
        "start_time": data["start_time"],
        "end_time": data["end_time"],
        "status": data["status"],
        "sync_status": data["sync_status"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
        "client": client_data,
        "calendar_event": calendar_event,
    }


def list_events_sql(start_iso: str, end_iso: str) -> list[dict]:
    """Lista citas en un rango de fechas con información del cliente y del evento de calendario."""
    result = (
        supabase.table("appointments")
        .select(
            "id, start_time, end_time, "
            "client:client_id(name, phone), "
            "calendar_events(summary, description)"
        )
        .neq("status", "deleted")
        .gte("start_time", start_iso)
        .lte("start_time", end_iso)
        .order("start_time", desc=False)
        .execute()
    )

    events = []
    for row in result.data:
        client_name = None
        client_phone = None
        if row.get("client"):
            client_name = row["client"]["name"]
            client_phone = row["client"]["phone"]

        summary = None
        description = None
        cal_ev = row.get("calendar_events")
        if isinstance(cal_ev, list) and cal_ev:
            cal_ev = cal_ev[0]
        if isinstance(cal_ev, dict):
            summary = cal_ev.get("summary")
            description = cal_ev.get("description")

        events.append({
            "id": row["id"],
            "summary": summary,
            "from": row["start_time"],
            "to": row["end_time"],
            "description": description,
            "client_name": client_name,
            "client_phone": client_phone,
            "status": "Turno ocupado",
        })

    return events


def list_events_by_phone_sql(phone: str) -> list[dict]:
    """Lista todas las citas de un cliente por su teléfono."""
    result = (
        supabase.table("appointments")
        .select(
            "id, start_time, end_time, status, "
            "client:client_id(name, phone), "
            "calendar_events(summary, description)"
        )
        .eq("client.phone", phone)
        .neq("status", "deleted")
        .order("start_time", desc=False)
        .execute()
    )

    events = []
    for row in result.data:
        client_name = None
        if row.get("client"):
            client_name = row["client"]["name"]

        summary = None
        description = None
        cal_ev = row.get("calendar_events")
        if isinstance(cal_ev, list) and cal_ev:
            cal_ev = cal_ev[0]
        if isinstance(cal_ev, dict):
            summary = cal_ev.get("summary")
            description = cal_ev.get("description")

        events.append({
            "id": row["id"],
            "summary": summary,
            "from": row["start_time"],
            "to": row["end_time"],
            "description": description,
            "status": row["status"],
            "client_name": client_name,
        })

    return events


def list_events_by_client_id(client_id: str) -> list[dict]:
    """Lista todas las citas de un cliente por su ID."""
    result = (
        supabase.table("appointments")
        .select(
            "id, start_time, end_time, status, "
            "calendar_events(summary, description)"
        )
        .eq("client_id", client_id)
        .neq("status", "deleted")
        .order("start_time", desc=False)
        .execute()
    )

    events = []
    for row in result.data:
        summary = None
        description = None
        cal_ev = row.get("calendar_events")
        if isinstance(cal_ev, list) and cal_ev:
            cal_ev = cal_ev[0]
        if isinstance(cal_ev, dict):
            summary = cal_ev.get("summary")
            description = cal_ev.get("description")

        events.append({
            "id": row["id"],
            "summary": summary,
            "from": row["start_time"],
            "to": row["end_time"],
            "description": description,
            "status": row["status"],
        })

    return events