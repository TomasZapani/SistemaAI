# agent/services/gemini_service.py
import os
from agent.config import SYSTEM_CONTEXT
from google import genai
from google.genai import types
import json


class GeminiService:
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client

    def generate(self, messages: list):
        """
        Genera un mensaje del modelo en base al historial de mensajes.

        Args:
            messages (list): Lista de mensajes en formato:
                [{"role": "user", "content": "texto"}, ...]

        Returns:
            dict: Respuesta generada por el modelo con formato JSON
        """
        # Convertir formato backend a formato Gemini
        formatted_messages = [
            {
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            }
            for msg in messages
        ]

        response = self.gemini_client.models.generate_content(
            model=os.getenv("GEMINI_MODEL"),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_CONTEXT,
                response_mime_type="application/json",
            ),
            contents=formatted_messages,
        )

        return json.loads(response.text)