# app/services/tts_services.py

#Este archivo maneja la conversion de texto a voz usando ElevenLabs cuando el agente responde
import os
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

def text_to_speech(text: str) -> bytes:
    """
    Convierte texto a audio MP3 usando ElevenLabs
    Devuelve bytes reales (no generator)
    """

    audio_stream = client.text_to_speech.convert(
        voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        model_id="eleven_multilingual_v2",
        text=text
    )

    audio_bytes = b"".join(chunk for chunk in audio_stream)

    return audio_bytes
