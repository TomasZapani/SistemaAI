"""
Capturador de conversaciones reales para training
Integra con Session para guardar automáticamente conversaciones exitosas
"""
import json
import os
from datetime import datetime
from typing import Dict, List
from .dataset_builder import DatasetBuilder

class ConversationCapture:
    def __init__(self, output_dir: str = "training/captured"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.builder = DatasetBuilder(output_dir)
    
    def capture_from_session(self, session, quality_score: int = None, tags: List[str] = None):
        """
        Captura una conversación desde una Session activa.
        
        Args:
            session: Instancia de Session
            quality_score: Calificación de calidad (1-5)
            tags: Etiquetas descriptivas (ej: ["cita_exitosa", "cliente_satisfecho"])
        """
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
            "tags": tags or [],
            "stats": session.get_stats()
        }
        
        self.builder.add_from_session_log(session.messages, metadata)
        
        # Guardar inmediatamente
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"captured_{timestamp}.jsonl"
        self.builder.save(filename)
        self.builder.conversations = []
        
        print(f"Conversación capturada: {filename}")
    
    def capture_manual(self, messages: List[Dict], metadata: Dict = None):
        """
        Captura manualmente una conversación.
        
        Args:
            messages: Lista de mensajes [{"role": "user/model", "content": "..."}]
            metadata: Metadatos adicionales
        """
        self.builder.add_conversation(messages, metadata)
    
    def save_batch(self, filename: str = None):
        """Guarda todas las conversaciones capturadas en batch. Batch es basicamente todo lo que se ha capturado hasta ahora."""
        return self.builder.save(filename)


def integrate_with_session_example():
    """
    Ejemplo de cómo integrar el capturador con tu Session actual.
    
    Añade esto a tu flujo principal:
    """
    print("""
    Para capturar conversaciones automáticamente, añade al final de tu flujo:
    
    ```python
    from agent.data_pipeline.capture_conversation import ConversationCapture
    
    # Después de una conversación exitosa
    if conversation_was_successful:
        capture = ConversationCapture()
        capture.capture_from_session(
            session=my_session,
            quality_score=5,  # 1-5
            tags=["cita_agendada", "cliente_satisfecho"]
        )
    ```
    
    O para capturar todas las conversaciones:
    
    ```python
    # Al final de cada conversación
    capture = ConversationCapture()
    capture.capture_from_session(session=my_session)
    ```
    """)


if __name__ == "__main__":
    integrate_with_session_example()


