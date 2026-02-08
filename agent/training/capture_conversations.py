"""
Capturador de conversaciones reales para training
Integra con Session para guardar automáticamente conversaciones exitosas
"""
import json
import os
from datetime import datetime
from typing import Dict, List
from dataset_builder import DatasetBuilder

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
        
        self.builder.add_from_session_log(session.messages)
        
        # Guardar inmediatamente
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"captured_{timestamp}.jsonl"
        self.builder.save(filename)
        
        print(f"✓ Conversación capturada: {filename}")
    
    def capture_manual(self, messages: List[Dict], metadata: Dict = None):
        """
        Captura manualmente una conversación.
        
        Args:
            messages: Lista de mensajes [{"role": "user/model", "content": "..."}]
            metadata: Metadatos adicionales
        """
        self.builder.add_conversation(messages, metadata)
    
    def save_batch(self, filename: str = None):
        """Guarda todas las conversaciones capturadas en batch."""
        return self.builder.save(filename)


if __name__ == "__main__":
    integrate_with_session_example()
