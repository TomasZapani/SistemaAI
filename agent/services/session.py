import ollama

from agent.config import BUSINESS_CONTEXT, OLLAMA_MODEL, OLLAMA_HOST


class Session:
    def __init__(self):
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.messages = [
            {"role": "system", "content": BUSINESS_CONTEXT}
        ]

    def add_message(self, role: str, message: str):
        """
        Añade un mensaje dentro de la sesión.

        Args:
            role (str): Rol del mensaje user/assistant.
            message (str): Mensaje que se añadira.
        """
        self.messages.append(
            {"role": role, "content": message}
        )

    def add_context(self, context: str):
        """
        Añade un mensaje dentro de la sesión que actua como contexto para el modelo.

        Args:
            context (str): Mensaje de contexto.
        """
        self.messages.append(
            {"role": "system", "content": context}
        )

    def generate(self):
        """
        Genera un mensaje del modelo en base al historial de mensajes previo.

        Returns:
            str: Mensaje generado por el modelo.
        """
        response = self.client.chat(
            model=OLLAMA_MODEL,
            messages=self.messages,
        )

        assistant_message = response.message.content
        self.add_message("assistant", assistant_message)

        return assistant_message
