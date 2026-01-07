# app/services/whisper_service.py

#Este archivo maneja la transcripcion de audio a texto usando la API de OpenAI Whisper
import os
from openai import OpenAI


client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))


async def transcribe_audio(file_path: str)-> str:
    """
    Tomar un archivo de audio del disco(de prueba por ahora) y devuelve texto
    """

    with open(file_path, "rb") as audio:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )

        return response.text