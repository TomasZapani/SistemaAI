from typing import Optional
from orquestator.supabase_conn.connection import supabase


def upsert_appointment(
    *,
    id: str,
    google_event_id: str = None,
    summary: str,
    start_time: str,
    end_time: str,
    client_id: str,
    description: str = None,
    status: str = "confirmed",
    sync_status: str = "pending"
) -> dict:
    """Crea o actualiza una cita."""
    data = {
        "id": id,
        "google_event_id": google_event_id,
        "summary": summary,
        "client_id": client_id,
        "start_time": start_time,
        "end_time": end_time,
        "description": description,
        "status": status,
        "sync_status": sync_status,
    }
    
    supabase.table("appointments").upsert(data).execute()
    return get_appointment(id=id)


def mark_deleted(*, id: str) -> None:
    """Marca como borrado usando el ID interno."""
    update_data = {
        "status": "deleted",
        "sync_status": "pending"
    }
    supabase.table("appointments").update(update_data).eq("id", id).execute()


def get_appointment(*, id: str) -> Optional[dict]:
    """Obtiene un evento por su ID interno con datos del cliente."""
    result = (
        supabase.table("appointments")
        .select("*, client:client_id(name, phone)")
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
    
    return {
        "id": data["id"],
        "google_event_id": data.get("google_event_id"),
        "summary": data["summary"],
        "client_id": data["client_id"],
        "start_time": data["start_time"],
        "end_time": data["end_time"],
        "description": data.get("description"),
        "status": data["status"],
        "sync_status": data["sync_status"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
        "client": client_data
    }


def list_events_sql(start_iso: str, end_iso: str) -> list[dict]:
    """Lista citas en un rango de fechas con información del cliente."""
    result = (
        supabase.table("appointments")
        .select("id, summary, start_time, end_time, description, "
                "client:client_id(name, phone)")
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
        
        events.append({
            "id": row["id"],
            "summary": row["summary"],
            "from": row["start_time"],
            "to": row["end_time"],
            "description": row.get("description"),
            "client_name": client_name,
            "client_phone": client_phone,
            "status": "Turno ocupado",
        })
    
    return events


def list_events_by_phone_sql(phone: str) -> list[dict]:
    """Lista todas las citas de un cliente por su teléfono."""
    result = (
        supabase.table("appointments")
        .select("id, summary, start_time, end_time, description, status, "
                "client:client_id(name, phone)")
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
        
        events.append({
            "id": row["id"],
            "summary": row["summary"],
            "from": row["start_time"],
            "to": row["end_time"],
            "description": row.get("description"),
            "status": row["status"],
            "client_name": client_name,
        })
    
    return events


def list_events_by_client_id(client_id: str) -> list[dict]:
    """Lista todas las citas de un cliente por su ID."""
    result = (
        supabase.table("appointments")
        .select("id, summary, start_time, end_time, description, status")
        .eq("client_id", client_id)
        .neq("status", "deleted")
        .order("start_time", desc=False)
        .execute()
    )
    
    events = []
    for row in result.data:
        events.append({
            "id": row["id"],
            "summary": row["summary"],
            "from": row["start_time"],
            "to": row["end_time"],
            "description": row.get("description"),
            "status": row["status"],
        })
    
    return events
