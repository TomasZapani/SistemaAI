# app/services/agent_brain.py

#Este archivo contiene la lògica gral de como debe actuar el agente: 1.El contexto gral de como debe comportarse, 2.Extarer notas importantes de los mensajes del cliente, 3.Generar respuestas del agente.
from app.services.openai_service import reason
from app.services.conversation_memory import (
    save_message,
    get_conversation_history,
    format_history_for_prompt
)

SYSTEM_PROMPT = """
Sos un agente comercial profesional, amable y claro.
Tu misión:
- Responder al cliente de forma natural.
- Guiar la conversación hacia el objetivo (venta o información).
- Extraer datos útiles que el cliente mencione.
- Ser breve, humano y persuasivo.
"""

async def extract_notes(user_msg: str):
    prompt = f"""
Extraé las notas importantes del siguiente mensaje del cliente.

Mensaje:
{user_msg}

Devolvé una lista con puntos importantes. Formato:
- dato1
- dato2
- dato3
"""
    result = await reason(prompt)
    notes = [n.strip("- ").strip() for n in result.split("\n") if n.strip()]
    return notes


async def agent_reply(user_msg: str, call_id: str = None, context: str = ""):
    """
    Genera respuesta del agente usando memoria de conversación.
    
    Args:
        user_msg: Mensaje del cliente
        call_id: ID único de la llamada (para persistencia)
        context: Contexto adicional (legacy)
    
    Returns:
        Tupla (reply, notes)
    """
    # Obtener historial de conversación si hay call_id
    history_text = ""
    if call_id:
        history = get_conversation_history(call_id)
        history_text = format_history_for_prompt(history)
        # Guardar mensaje del cliente
        save_message(call_id, "user", user_msg)
    else:
        history_text = context
    
    # Construir prompt con historial
    prompt = f"""
{SYSTEM_PROMPT}

{history_text}

El cliente dijo:
\"{user_msg}\"

Respuesta del agente:
"""
    
    reply = await reason(prompt)
    notes = await extract_notes(user_msg)
    
    # Guardar respuesta del agente
    if call_id:
        save_message(call_id, "assistant", reply)
    
    return reply, notes
