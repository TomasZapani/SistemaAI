from google import genai
from google.genai import types
import os
import json
import logging
import time
from config import SYSTEM_CONTEXT

logger = logging.getLogger(__name__)

class Session:
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client
        self.messages = []
        self.metadata = {
            "total_tokens": 0,
            "api_calls": 0,
            "errors": 0,
            "created_at": time.time()
        }
        
        # Configuración del modelo
        self.model_config = {
            "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            "top_p": float(os.getenv("GEMINI_TOP_P", "0.95")),
            "top_k": int(os.getenv("GEMINI_TOP_K", "40")),
            "max_output_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "2048")),
        }
        
        # Retry configuration
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("GEMINI_RETRY_DELAY", "1.0"))
    
    def add_message(self, role: str, message: str):
        """
        Añade un mensaje dentro de la sesión.

        Args:
            role (str): Rol del mensaje user/model.
            message (str): Mensaje que se añadira.
        """
        self.messages.append({"role": role, "parts": [{"text": message}]})
        logger.debug(f"Message added - Role: {role}, Length: {len(message)} chars")

    def add_context(self, context: str):
        """
        Añade un mensaje dentro de la sesión que actua como contexto para el modelo.

        Args:
            context (str): Mensaje de contexto.
        """
        self.messages.append({"role": "user", "parts": [{"text": f"[SYSTEM CONTEXT] {context}"}]})
        logger.info(f"Context added: {context[:100]}...")

    def _validate_json_response(self, response_text: str) -> bool:
        """
        Valida que la respuesta sea JSON válido con la estructura esperada.

        Args:
            response_text (str): Texto de respuesta del modelo.

        Returns:
            bool: True si es válido, False en caso contrario.
        """
        try:
            data = json.loads(response_text)
            
            # Validar estructura básica
            if not isinstance(data, dict):
                logger.error("Response is not a JSON object")
                return False
            
            if "action" not in data:
                logger.error("Response missing 'action' field")
                return False
            
            if "data" not in data:
                logger.error("Response missing 'data' field")
                return False
            
            logger.debug(f"Valid JSON response with action: {data['action']}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return False

    def generate(self):
        """
        Genera un mensaje del modelo en base al historial de mensajes previo.
        Incluye retry logic y validación de respuestas.

        Returns:
            str: Mensaje generado por el modelo en formato JSON.

        Raises:
            Exception: Si falla después de todos los reintentos.
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Generating response (attempt {attempt + 1}/{self.max_retries})")
                
                # Llamada a la API de Gemini
                message = self.gemini_client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_CONTEXT,
                        response_mime_type="application/json",
                        temperature=self.model_config["temperature"],
                        top_p=self.model_config["top_p"],
                        top_k=self.model_config["top_k"],
                        max_output_tokens=self.model_config["max_output_tokens"],
                    ),
                    contents=self.messages
                )
                
                self.metadata["api_calls"] += 1
                
                # Validar que tenemos una respuesta
                if not message or not message.text:
                    raise ValueError("Empty response from model")
                
                response_text = message.text.strip()
                
                # Validar que la respuesta sea JSON válido
                if not self._validate_json_response(response_text):
                    raise ValueError("Invalid JSON response structure")
                
                # Agregar respuesta al historial
                self.add_message("model", response_text)
                
                # Actualizar metadata
                if hasattr(message, 'usage_metadata'):
                    self.metadata["total_tokens"] += getattr(message.usage_metadata, 'total_token_count', 0)
                
                logger.info(f"Response generated successfully: {response_text[:100]}...")
                return response_text
                
            except Exception as e:
                last_error = e
                self.metadata["errors"] += 1
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                # Si no es el último intento, esperar antes de reintentar
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")
        
        # Si llegamos aquí, todos los intentos fallaron
        raise Exception(f"Failed to generate response after {self.max_retries} attempts: {str(last_error)}")
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de la sesión.

        Returns:
            dict: Diccionario con métricas de la sesión.
        """
        return {
            **self.metadata,
            "message_count": len(self.messages),
            "duration": time.time() - self.metadata["created_at"]
        }
