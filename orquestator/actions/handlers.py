from typing import Dict, Any
import logging
import json

from helpers.twiml import end_call, gather_call
from api.appointment import (
    appointment_list, 
    appointment_create,
    appointment_update,
    appointment_delete,
    appointment_search
)
from api.session import add_context
from actions.schemas import TalkData

logger = logging.getLogger(__name__)

async def handle_talk(call_sid: str, from_number: str, data: Dict[str, Any]) -> str:
    """Maneja la acción TALK"""
    try:
        talk_data = TalkData(**data)
        return gather_call(talk_data.message)
    except Exception as e:
        logger.error(f"Error in TALK: {e}")
        return end_call("Lo siento, tuvimos un error interno.")

async def handle_end_call(call_sid: str, from_number: str, data: Dict[str, Any]) -> str:
    """Maneja la acción END_CALL"""
    talk_data = TalkData(**data)
    return end_call(talk_data.message)

async def handle_appointment_list(call_sid: str, from_number: str, data: Dict[str, Any]) -> str:
    """Lista citas para un día específico"""
    try:
        resp_body = await appointment_list(data)
        
        # Verificar si la lista está vacía
        if resp_body == [] or resp_body == "[]":
            ctx = "APPOINTMENT_LIST_OK: No hay turnos agendados para este día."
        else:
            ctx = f"APPOINTMENT_LIST_OK {json.dumps(resp_body)}"
        
        # Enviar contexto al agente
        context_response = await add_context(call_sid, ctx)
        
        # Si la IA decide saltar a otra acción
        if context_response["action"] != "TALK":
            from actions.registry import get_action_handler
            next_handler = get_action_handler(context_response["action"])
            if next_handler:
                return await next_handler(call_sid, from_number, context_response["data"])
        
        # Responder con TALK
        talk_data = TalkData(**context_response["data"])
        return gather_call(talk_data.message)
        
    except Exception as e:
        logger.error(f"Error in APPOINTMENT_LIST: {e}")
        ctx = f"APPOINTMENT_LIST_ERROR {str(e)}"
        context_response = await add_context(call_sid, ctx)
        talk_data = TalkData(**context_response["data"])
        return gather_call(talk_data.message)

async def handle_appointment_create(call_sid: str, from_number: str, data: Dict[str, Any]) -> str:
    """Crea una nueva cita"""
    try:
        data["client_phone"] = from_number
        resp_body = await appointment_create(data)
        ctx = f"APPOINTMENT_CREATE_OK {json.dumps(resp_body)}"
    except Exception as e:
        logger.error(f"Error in APPOINTMENT_CREATE: {e}")
        ctx = f"APPOINTMENT_CREATE_ERROR {str(e)}"
    
    context_response = await add_context(call_sid, ctx)
    talk_data = TalkData(**context_response["data"])
    return gather_call(talk_data.message)

async def handle_appointment_update(call_sid: str, from_number: str, data: Dict[str, Any]) -> str:
    """Actualiza una cita existente"""
    try:
        resp_body = await appointment_update(data)
        ctx = f"APPOINTMENT_UPDATE_OK {json.dumps(resp_body)}"
    except Exception as e:
        logger.error(f"Error in APPOINTMENT_UPDATE: {e}")
        ctx = f"APPOINTMENT_UPDATE_ERROR {str(e)}"
    
    context_response = await add_context(call_sid, ctx)
    talk_data = TalkData(**context_response["data"])
    return gather_call(talk_data.message)

async def handle_appointment_delete(call_sid: str, from_number: str, data: Dict[str, Any]) -> str:
    """Elimina una cita"""
    try:
        resp_body = await appointment_delete(data)
        ctx = f"APPOINTMENT_DELETE_OK {json.dumps(resp_body)}"
    except Exception as e:
        logger.error(f"Error in APPOINTMENT_DELETE: {e}")
        ctx = f"APPOINTMENT_DELETE_ERROR {str(e)}"
    
    context_response = await add_context(call_sid, ctx)
    talk_data = TalkData(**context_response["data"])
    return gather_call(talk_data.message)

async def handle_appointment_search(call_sid: str, from_number: str, data: Dict[str, Any]) -> str:
    """Busca citas de un cliente"""
    try:
        resp_body = await appointment_search(data)
        ctx = f"APPOINTMENT_SEARCH_OK {json.dumps(resp_body)}"
    except Exception as e:
        logger.error(f"Error in APPOINTMENT_SEARCH: {e}")
        ctx = f"APPOINTMENT_SEARCH_ERROR {str(e)}"
    
    context_response = await add_context(call_sid, ctx)
    talk_data = TalkData(**context_response["data"])
    return gather_call(talk_data.message)