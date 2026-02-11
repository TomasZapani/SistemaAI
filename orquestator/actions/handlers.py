import json
import logging
import uuid
from typing import Any, Dict
from actions.schemas import TalkData
from api.session import add_context
from helper.twiml import end_call, gather_call

from orquestator.config import CALENDAR_CLIENT, TIMEZONE
from orquestator.services.appointment_service import (
    get_appointment,
    list_events_by_phone_sql,
    list_events_sql,
    mark_deleted,
    upsert_appointment
)
from orquestator.utils.date_utils import (
    get_day_range,
    localize_datetime
)


logger = logging.getLogger(__name__)


async def handle_talk(
    call_sid: str, from_number: str, data: Dict[str, Any]
) -> str:
    """Maneja la acción TALK"""
    try:
        talk_data = TalkData(**data)
        return gather_call(talk_data.message)
    except Exception as e:
        logger.error(f"Error in TALK: {e}")
        return end_call("Lo siento, tuvimos un error interno.")


async def handle_end_call(
    call_sid: str, from_number: str, data: Dict[str, Any]
) -> str:
    """Maneja la acción END_CALL"""
    talk_data = TalkData(**data)
    return end_call(talk_data.message)


async def handle_appointment_list(
    call_sid: str, from_number: str, data: Dict[str, Any]
) -> str:
    """Lista citas para un día específico"""
    try:
        # Llamada directa al servicio local
        start_iso, end_iso = get_day_range(data["day"], TIMEZONE)
        appointments = list_events_sql(start_iso, end_iso)

        # Verificar si la lista está vacía
        if not appointments or len(appointments) == 0:
            ctx = "APPOINTMENT_LIST_OK: No hay turnos agendados para este día."
        else:
            ctx = f"APPOINTMENT_LIST_OK {json.dumps(appointments)}"

    except Exception as e:
        logger.error(f"Error in APPOINTMENT_LIST: {e}", exc_info=True)
        ctx = f"APPOINTMENT_LIST_ERROR {str(e)}"

    # Enviar contexto al agente y ejecutar siguiente acción
    return await _notify_and_execute(call_sid, from_number, ctx)


async def handle_appointment_create(
    call_sid: str, from_number: str, data: Dict[str, Any]
) -> str:
    """Crea una nueva cita"""
    try:
        internal_id = str(uuid.uuid4())
        
        # Normalizar fechas
        start_iso = localize_datetime(
            data["start_time"],
            TIMEZONE
        ).isoformat()
        
        end_iso = localize_datetime(
            data["end_time"],
            TIMEZONE
        ).isoformat()
        
        # Crear en BD local
        upsert_appointment(
            id=internal_id,
            summary=data["summary"],
            client_name=data["client_name"],
            client_phone=from_number,  # Usar número de llamada
            start_time=start_iso,
            end_time=end_iso,
            description=data.get("description", ""),
            status="confirmed",
            sync_status="pending"
        )

        result = {
            "status": "confirmed",
            "id": internal_id,
            "synced": False
        }

        # Intentar sincronizar con Google Calendar
        if CALENDAR_CLIENT:
            try:
                google_resp = CALENDAR_CLIENT.create_event(
                    summary=f"{data['summary']}: {data['client_name']}",
                    start_rfc3339=start_iso,
                    end_rfc3339=end_iso,
                    description=(
                        f"Nombre: {data['client_name']}\n\n"
                        f"Tel: {from_number}\n\n"
                        f"{data.get('description', '')}"
                    ),
                )

                g_id = google_resp.get("id")
                if g_id:
                    upsert_appointment(
                        id=internal_id,
                        google_event_id=g_id,
                        summary=data["summary"],
                        client_name=data["client_name"],
                        client_phone=from_number,
                        start_time=start_iso,
                        end_time=end_iso,
                        description=data.get("description", ""),
                        sync_status="synced"
                    )
                    result["synced"] = True

            except Exception as e:
                logger.warning(f"Error sincronizando con Google: {e}")

        ctx = f"APPOINTMENT_CREATE_OK {json.dumps(result)}"

    except Exception as e:
        logger.error(f"Error in APPOINTMENT_CREATE: {e}", exc_info=True)
        ctx = f"APPOINTMENT_CREATE_ERROR {str(e)}"

    return await _notify_and_execute(call_sid, from_number, ctx)


async def handle_appointment_update(
    call_sid: str, from_number: str, data: Dict[str, Any]
) -> str:
    """Actualiza una cita existente"""
    try:
        # Obtener cita actual
        current = get_appointment(id=data["id"])
        if not current:
            raise ValueError("Evento no encontrado")

        # Normalizar fechas si se proporcionan
        start_iso = (
            localize_datetime(data["start_time"], TIMEZONE).isoformat()
            if data.get("start_time")
            else current["start_time"]
        )
        
        end_iso = (
            localize_datetime(data["end_time"], TIMEZONE).isoformat()
            if data.get("end_time")
            else current["end_time"]
        )
        
        # Usar valores actuales como fallback
        updated_summary = data.get("summary") or current["summary"]
        updated_name = data.get("client_name") or current["client_name"]
        updated_phone = data.get("client_phone") or current["client_phone"]
        updated_desc = data.get("description") or current["description"]

        # Actualizar en BD local
        upsert_appointment(
            id=data["id"],
            summary=updated_summary,
            client_name=updated_name,
            client_phone=updated_phone,
            start_time=start_iso,
            end_time=end_iso,
            description=updated_desc,
            sync_status="pending"
        )

        # Intentar actualizar en Google Calendar
        if CALENDAR_CLIENT and current.get("google_event_id"):
            try:
                CALENDAR_CLIENT.update_event(
                    event_id=current["google_event_id"],
                    summary=f"{updated_summary}: {updated_name}",
                    start_rfc3339=start_iso,
                    end_rfc3339=end_iso,
                    description=f"Tel: {updated_phone}\n{updated_desc}"
                )
                
                upsert_appointment(
                    id=data["id"],
                    summary=updated_summary,
                    start_time=start_iso,
                    end_time=end_iso,
                    sync_status="synced"
                )

            except Exception as e:
                logger.warning(f"Error actualizando en Google: {e}")

        result = {"status": "confirmed", "id": data["id"]}
        ctx = f"APPOINTMENT_UPDATE_OK {json.dumps(result)}"

    except Exception as e:
        logger.error(f"Error in APPOINTMENT_UPDATE: {e}", exc_info=True)
        ctx = f"APPOINTMENT_UPDATE_ERROR {str(e)}"

    return await _notify_and_execute(call_sid, from_number, ctx)


async def handle_appointment_delete(
    call_sid: str, from_number: str, data: Dict[str, Any]
) -> str:
    """Elimina una cita"""
    try:
        appointment_id = data.get("id")
        
        # Obtener cita antes de eliminar
        current = get_appointment(id=appointment_id)
        
        # Marcar como eliminada en BD
        mark_deleted(id=appointment_id)

        # Intentar eliminar de Google Calendar
        if CALENDAR_CLIENT and current and current.get("google_event_id"):
            try:
                CALENDAR_CLIENT.delete_event(current["google_event_id"])
            except Exception as e:
                logger.warning(f"No se pudo borrar en Google: {e}")

        ctx = f"APPOINTMENT_DELETE_OK {json.dumps({'ok': True})}"

    except Exception as e:
        logger.error(f"Error in APPOINTMENT_DELETE: {e}", exc_info=True)
        ctx = f"APPOINTMENT_DELETE_ERROR {str(e)}"

    return await _notify_and_execute(call_sid, from_number, ctx)


async def handle_appointment_search(
    call_sid: str, from_number: str, data: Dict[str, Any]
) -> str:
    """Busca citas de un cliente por teléfono"""
    try:
        # Usar el teléfono del data o el de la llamada como fallback
        phone = data.get("client_phone", from_number)
        
        # Llamada directa al servicio local
        appointments = list_events_by_phone_sql(phone)
        
        ctx = f"APPOINTMENT_SEARCH_OK {json.dumps(appointments)}"

    except Exception as e:
        logger.error(f"Error in APPOINTMENT_SEARCH: {e}", exc_info=True)
        ctx = f"APPOINTMENT_SEARCH_ERROR {str(e)}"

    return await _notify_and_execute(call_sid, from_number, ctx)


# ============ HELPER PRIVADO ============

async def _notify_and_execute(
    call_sid: str,
    from_number: str,
    context: str
) -> str:
    """
    Notifica al agente del resultado y ejecuta la siguiente acción.
    Centraliza la lógica repetida de todos los handlers.
    """
    # 1. Notificar al agente
    context_response = await add_context(call_sid, context)
    
    # 2. Si el agente decide ejecutar otra acción (no TALK)
    if context_response["action"] != "TALK":
        from actions.registry import get_action_handler
        
        next_handler = get_action_handler(context_response["action"])
        if next_handler:
            return await next_handler(
                call_sid,
                from_number,
                context_response["data"]
            )
    
    # 3. Por defecto, responder con TALK
    talk_data = TalkData(**context_response["data"])
    return gather_call(talk_data.message)