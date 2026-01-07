# app/api/tts_router.py

#Este archivo define las rutas API relacionadas con la conversion de texto a voz.
from fastapi import APIRouter, Response
from app.schemas.agent_schema import TTSRequest
from app.services.tts_services import text_to_speech

router = APIRouter()

@router.post("/tts")
async def tts(request: TTSRequest):
    audio_bytes = text_to_speech(request.text)

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg"
    )
