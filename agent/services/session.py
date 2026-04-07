# agent/services/session.py
import os
import json
from groq import Groq
from agent.config import BUSINESS_CONTEXT
from agent.services.orchestator_client import OrchestratorClient
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

# Definición de las herramientas (tools) que el agente puede usar
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_appointments",
            "description": "Search for all appointments associated with a customer's phone number. Use this when the customer asks about their existing appointments or wants to check their schedule.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {
                        "type": "string",
                        "description": "The customer's phone number"
                    }
                },
                "required": ["phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment. Use this ONLY after confirming with the customer that they want to cancel. Requires the appointment ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "string",
                        "description": "The unique ID of the appointment to cancel"
                    }
                },
                "required": ["appointment_id"]
            }
        }
    }
]


class Session:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.messages = [
            {"role": "system", "content": BUSINESS_CONTEXT}
        ]

    def add_message(self, role: str, message: str):
        """Añade un mensaje dentro de la sesión."""
        self.messages.append({"role": role, "content": message})

    def add_context(self, context: str):
        """Añade un mensaje de contexto dentro de la sesión."""
        self.messages.append({"role": "system", "content": context})

    def _execute_function(self, function_name: str, arguments: dict) -> str:
        """
        Ejecuta la función solicitada por el LLM y devuelve el resultado.
        """
        if function_name == "search_appointments":
            phone = arguments.get("phone")
            appointments = OrchestratorClient.search_appointments_by_phone(phone)
            
            if not appointments:
                return json.dumps({"success": True, "appointments": [], "message": "No se encontraron turnos para este teléfono"})
            
            return json.dumps({"success": True, "appointments": appointments})
        
        elif function_name == "cancel_appointment":
            appointment_id = arguments.get("appointment_id")
            success = OrchestratorClient.delete_appointment(appointment_id)
            
            if success:
                return json.dumps({"success": True, "message": "Turno cancelado exitosamente"})
            else:
                return json.dumps({"success": False, "message": "No se pudo cancelar el turno"})
        
        return json.dumps({"error": "Función no reconocida"})

    def generate(self):
        """
        Genera un mensaje del modelo, ejecutando funciones si es necesario.
        """
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=self.messages,
            tools=TOOLS,
            tool_choice="auto",
            timeout=30
        )

        assistant_message = response.choices[0].message
        
        # Si el modelo quiere usar una función
        if assistant_message.tool_calls:
            # Agregar el mensaje del asistente (con tool_calls)
            self.messages.append(assistant_message)
            
            # Ejecutar cada función solicitada
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"🔧 Ejecutando función: {function_name} con args: {arguments}")
                
                # Ejecutar la función
                function_result = self._execute_function(function_name, arguments)
                
                # Agregar el resultado como mensaje de tipo "tool"
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_result
                })
            
            # Generar respuesta final después de ejecutar las funciones
            final_response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=self.messages,
                timeout=30
            )
            
            final_message = final_response.choices[0].message.content
            self.add_message("assistant", final_message)
            return final_message
        
        # Si no usa funciones, devolver respuesta normal
        else:
            content = assistant_message.content
            self.add_message("assistant", content)
            return content