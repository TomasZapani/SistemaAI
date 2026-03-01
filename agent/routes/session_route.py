import json
from fastapi import APIRouter, HTTPException
from agent.services.session import Session
from agent.utils.date_utils import get_now_formatted


sessions: dict[str, Session] = {}
router = APIRouter(
    prefix="/session",
    tags=["Session"]
)


@router.post("/start")
async def start_endpoint(call_sid: str):
    """Crea una nueva sesion y devuelve el mensaje de bienvenida"""
    if call_sid not in sessions:
        sessions[call_sid] = Session()
    
    session = sessions[call_sid]
    now = get_now_formatted()
    session.add_context(
         f"Se inicio una llamada, saluda al cliente. Hoy es {now}."
    )
    response = session.generate()

    return json.loads(response)


@router.post("/context")
async def context_endpoint(call_sid: str, context: str):
    """Inyecta contexto en el chat y devuelve un mensaje"""
    if call_sid not in sessions:
            raise HTTPException(
                 status_code=404,
                 detail="No se pudo finalizar: la sesión no existe."
            )
    
    session = sessions[call_sid]
    session.add_context(context)
    response = session.generate()

    print(json.loads(response))

    return json.loads(response)


@router.post("/send")
async def send_endpoint(call_sid: str, message: str):
    """Envia un mensaje como usuario"""
    if call_sid not in sessions:
            raise HTTPException(
                status_code=404,
                detail="No se pudo finalizar: la sesión no existe."
            )
    
    session = sessions[call_sid]
    session.add_message("user", message)
    response = session.generate()

    return json.loads(response)


@router.delete("/end")
async def end_endpoint(call_sid: str):
    """Termina y elimina la sesion"""
    sessions.pop(call_sid, None)
