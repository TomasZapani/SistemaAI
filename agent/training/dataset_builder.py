"""
Dataset Builder para Fine-tuning de Gemini
Genera datasets en formato JSONL para entrenar el modelo en servicio al cliente
"""
import json
import os
from datetime import datetime
from typing import List, Dict

class DatasetBuilder:
    def __init__(self, output_dir: str = "training/datasets"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.conversations = []
    
    def add_conversation(self, messages: List[Dict[str, str]], metadata: Dict = None):
        """
        Añade una conversación al dataset.
        
        Args:
            messages: Lista de mensajes con formato [{"role": "user", "content": "..."}, {"role": "model", "content": "..."}]
            metadata: Información adicional (tema, calidad, fecha, etc.)
        """
        conversation = {
            "messages": messages,
            "metadata": metadata or {}
        }
        self.conversations.append(conversation)
    
    def add_from_session_log(self, session_messages: List[Dict]):
        """
        Convierte mensajes de sesión al formato de training.
        Filtra mensajes de sistema y contexto.
        
        Args:
            session_messages: Mensajes del formato Session.messages
        """
        cleaned_messages = []
        
        for msg in session_messages:
            role = msg.get("role")
            text = msg.get("parts", [{}])[0].get("text", "")
            
            # Filtrar contexto del sistema
            if "[SYSTEM CONTEXT]" in text:
                continue
            
            # Mapear roles
            if role in ["user", "model"]:
                cleaned_messages.append({
                    "role": role,
                    "content": text
                })
        
        if cleaned_messages:
            self.add_conversation(cleaned_messages)
    
    def save(self, filename: str = None):
        """
        Guarda el dataset en formato JSONL.
        
        Args:
            filename: Nombre del archivo (se genera automático si es None)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dataset_{timestamp}.jsonl"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for conv in self.conversations:
                f.write(json.dumps(conv, ensure_ascii=False) + '\n')
        
        print(f"Dataset guardado: {filepath}")
        print(f"  Total conversaciones: {len(self.conversations)}")
        return filepath
    
    def validate(self) -> Dict:
        """
        Valida el dataset y retorna estadísticas.
        
        Returns:
            Dict con métricas de calidad
        """
        stats = {
            "total_conversations": len(self.conversations),
            "total_messages": 0,
            "avg_messages_per_conversation": 0,
            "user_messages": 0,
            "model_messages": 0,
            "errors": []
        }
        
        for i, conv in enumerate(self.conversations):
            messages = conv.get("messages", [])
            stats["total_messages"] += len(messages)
            
            for msg in messages:
                if msg["role"] == "user":
                    stats["user_messages"] += 1
                elif msg["role"] == "model":
                    stats["model_messages"] += 1
                
                # Validaciones
                if not msg.get("content"):
                    stats["errors"].append(f"Conversación {i}: mensaje vacío")
                
                if msg["role"] not in ["user", "model"]:
                    stats["errors"].append(f"Conversación {i}: rol inválido '{msg['role']}'")
        
        if stats["total_conversations"] > 0:
            stats["avg_messages_per_conversation"] = stats["total_messages"] / stats["total_conversations"]
        
        return stats
    
    def print_stats(self):
        """Imprime estadísticas del dataset."""
        stats = self.validate()
        
        print("\n" + "="*50)
        print("ESTADÍSTICAS DEL DATASET")
        print("="*50)
        print(f"Conversaciones: {stats['total_conversations']}")
        print(f"Mensajes totales: {stats['total_messages']}")
        print(f"Promedio mensajes/conversación: {stats['avg_messages_per_conversation']:.1f}")
        print(f"Mensajes de usuario: {stats['user_messages']}")
        print(f"Mensajes del modelo: {stats['model_messages']}")
        
        if stats['errors']:
            print(f"\n Errores encontrados: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Mostrar primeros 5
                print(f"  - {error}")
        else:
            print("\n Dataset válido")
        print("="*50 + "\n")


def create_example_dataset():
    """Crea un dataset de ejemplo con conversaciones de servicio al cliente."""
    builder = DatasetBuilder()
    
    # Ejemplo 1: Agendar cita
    builder.add_conversation([
        {"role": "user", "content": "Hola, necesito agendar una cita"},
        {"role": "model", "content": "¡Hola! Claro, con gusto te ayudo. ¿Para qué fecha te gustaría agendar?"},
        {"role": "user", "content": "Para el 15 de febrero a las 3 de la tarde"},
        {"role": "model", "content": "Perfecto, ¿a nombre de quién será la cita?"},
        {"role": "user", "content": "Carlos Mendez"},
        {"role": "model", "content": "¡Listo Carlos! Tu cita está confirmada para el 15 de febrero a las 3:00 PM. Te esperamos."}
    ], metadata={"topic": "agendar_cita", "quality": "high"})
    
    # Ejemplo 2: Consultar disponibilidad
    builder.add_conversation([
        {"role": "user", "content": "¿Tienen disponibilidad mañana?"},
        {"role": "model", "content": "Déjame revisar. ¿Qué horario prefieres, mañana o tarde?"},
        {"role": "user", "content": "Por la mañana"},
        {"role": "model", "content": "Tenemos disponible a las 9:00 AM, 10:30 AM y 11:00 AM. ¿Cuál te viene mejor?"},
        {"role": "user", "content": "Las 10:30 está bien"},
        {"role": "model", "content": "Perfecto. ¿A nombre de quién?"},
        {"role": "user", "content": "María González"},
        {"role": "model", "content": "¡Confirmado María! Tu cita es mañana a las 10:30 AM. Nos vemos."}
    ], metadata={"topic": "consultar_disponibilidad", "quality": "high"})
    
    # Ejemplo 3: Cancelar cita
    builder.add_conversation([
        {"role": "user", "content": "Necesito cancelar mi cita"},
        {"role": "model", "content": "Entendido. ¿Para qué fecha tenías agendada tu cita?"},
        {"role": "user", "content": "El 20 de enero"},
        {"role": "model", "content": "Tu cita del 20 de enero ha sido cancelada exitosamente. ¿Deseas reagendar para otra fecha?"},
        {"role": "user", "content": "No, por ahora no. Gracias"},
        {"role": "model", "content": "Perfecto, cualquier cosa estamos a tu disposición. ¡Que tengas buen día!"}
    ], metadata={"topic": "cancelar_cita", "quality": "high"})
    
    builder.print_stats()
    filepath = builder.save("example_dataset.jsonl")
    
    return builder, filepath


if __name__ == "__main__":
    # Crear dataset de ejemplo
    builder, filepath = create_example_dataset()
    print(f"\n Dataset guardado en: {filepath}")
    print("\nPuedes usar este builder para añadir tus propias conversaciones.")
