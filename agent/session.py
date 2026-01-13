from google import genai
from google.genai import types
import os

SYSTEM_INSTRUCTION = ""
BUSSINES_CONTEXT = ""

with open('system_instruction.txt', 'r') as file:
    SYSTEM_INSTRUCTION = file.read()

with open('bussines_context.txt', 'r') as file:
    BUSSINES_CONTEXT = file.read()

SYSTEM_CONTEXT = SYSTEM_INSTRUCTION + "\n\nCONTEXTO DEL NEGOCIO:\n" + BUSSINES_CONTEXT

class Session:
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client
        self.messages = []
    
    def add_message(self, role: str, message: str):
        print(f"({role}) {message}")
        self.messages.append({"role": role, "parts": [{"text": message}]})

    def add_context(self, context: str):
        self.messages.append({"role": "user", "parts": [{"text": f"[SYSTEM CONTEXT] {context}"}]})

    def generate(self):
        message = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_CONTEXT,
                response_mime_type="application/json",
            ),
            contents=self.messages
        )

        self.add_message("model", message.text)

        return message.text
