from typing import Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Tipo para action handlers
ActionHandler = Callable[[str, str, Dict[str, Any]], str]

# Registro global de acciones
_actions: Dict[str, ActionHandler] = {}

def register_action(name: str, handler: ActionHandler):
    """Registra una acción en el sistema"""
    _actions[name] = handler
    logger.info(f"Action registered: {name}")

def get_action_handler(name: str) -> ActionHandler | None:
    """Obtiene el handler de una acción"""
    return _actions.get(name)

def init_actions():
    """Inicializa todas las acciones del sistema"""
    from actions.handlers import (
        handle_talk,
        handle_end_call,
        handle_appointment_list,
        handle_appointment_create,
        handle_appointment_update,
        handle_appointment_delete,
        handle_appointment_search
    )
    
    register_action("TALK", handle_talk)
    register_action("END_CALL", handle_end_call)
    register_action("APPOINTMENT_LIST", handle_appointment_list)
    register_action("APPOINTMENT_CREATE", handle_appointment_create)
    register_action("APPOINTMENT_UPDATE", handle_appointment_update)
    register_action("APPOINTMENT_DELETE", handle_appointment_delete)
    register_action("APPOINTMENT_SEARCH", handle_appointment_search)