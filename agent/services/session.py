from google import genai
from google.genai import types
import os
from config import SYSTEM_CONTEXT

class Session:
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client
        self.messages = []
    
    def add_message(self, role: str, message: str):
        """
        Añade un mensaje dentro de la sesión.

        Args:
            role (str): Rol del mensaje user/model.
            message (str): Mensaje que se añadira.
        """
        self.messages.append({"role": role, "parts": [{"text": message}]})

    def add_context(self, context: str):
        """
        Añade un mensaje dentro de la sesión que actua como contexto para el modelo.

        Args:
            context (str): Mensaje de contexto.
        """
        self.messages.append({"role": "user", "parts": [{"text": f"[SYSTEM CONTEXT] {context}"}]})

    def generate(self):
        """
        Genera un mensaje del modelo en base al historial de mensajes previo.

        Returns:
            str: Mensaje generado por el modelo.
        """
        message = self.gemini_client.models.generate_content(
            model=os.getenv("GEMINI_MODEL"),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_CONTEXT,
                response_mime_type="application/json",
            ),
            contents=self.messages
        )

        self.add_message("model", message.text)

        return message.text
