# agent/api/routes.py
from fastapi import APIRouter, HTTPException
from agent.services.gemini_service import GeminiService
from agent.config import GEMINI_CLIENT


router = APIRouter(prefix="/agent", tags=["Agent"])
gemini_service = GeminiService(GEMINI_CLIENT)


@router.post("/generate")
async def generate_endpoint(messages: list):
    """
    Genera una respuesta usando Gemini basada en el historial de mensajes.
    
    Args:
        messages: Lista de mensajes [{"role": "user/model", "content": "texto"}]
    
    Returns:
        dict: Respuesta JSON del modelo
    """
    try:
        response = gemini_service.generate(messages)
        return {
            "text": response,
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando respuesta: {str(e)}"
        )
