from fastapi import APIRouter, HTTPException
from services.google_calendar import GoogleCalendarClient
from models.google_calendar import (
    GoogleCalendarCreate,
    GoogleCalendarUpdate,
)


calendar = GoogleCalendarClient.from_env()

router = APIRouter(
    prefix="/google-calendar",
    tags=["Google calendar"]
)


@router.get("/list")
async def calendar_list_endpoint(
    time_min: str,
    time_max: str,
    max_results: int = 25
):
    try:
        calendars = calendar.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=max_results
        )
        return calendars
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo realizar la petición correctamente: {str(e)}"
        )


@router.post("/create")
async def calendar_create_endpoint(payload: GoogleCalendarCreate):
    try:
        event = calendar.create_event(
            summary=payload.summary,
            start_rfc3339=payload.start_rfc3339,
            end_rfc3339=payload.end_rfc3339,
            description=payload.description if payload.description else ""
        )
        return event
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo crear el evento correctamente: {str(e)}"
        )


@router.put("/update/{event_id}")
async def calendar_update_endpoint(event_id: str, payload: GoogleCalendarUpdate):
    try:
        event = calendar.update_event(
            event_id=event_id,
            summary=payload.summary,
            start_rfc3339=payload.start_rfc3339,
            end_rfc3339=payload.end_rfc3339,
            description=payload.description
        )
        return event
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo actualizar el evento correctamente: {str(e)}"
        )


@router.delete("/delete/{event_id}")
async def calendar_delete_endpoint(event_id: str):
    try:
        calendar.delete_event(event_id=event_id)
        return {"message": "Evento eliminado correctamente", "event_id": event_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo eliminar el evento correctamente: {str(e)}"
        )
