# agent/services/orchestrator_client.py
import httpx
import os
from typing import Optional

ORCHESTRATOR_API = os.getenv("ORCHESTRATOR_API", "http://localhost:3000")

class OrchestratorClient:
    """Cliente para interactuar con el API del orquestador"""
    
    @staticmethod
    def search_appointments_by_phone(phone: str) -> list:
        """
        Busca todos los turnos asociados a un número de teléfono.
        
        Args:
            phone: Número de teléfono del cliente
            
        Returns:
            Lista de turnos encontrados
        """
        try:
            response = httpx.post(
                f"{ORCHESTRATOR_API}/appointment/search",
                json={"client_phone": phone},
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error buscando turnos: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error conectando con orquestador: {e}")
            return []
    
    @staticmethod
    def delete_appointment(appointment_id: str) -> bool:
        """
        Cancela un turno existente.
        
        Args:
            appointment_id: ID del turno a cancelar
            
        Returns:
            True si se canceló exitosamente
        """
        try:
            response = httpx.post(
                f"{ORCHESTRATOR_API}/appointment/delete",
                json=appointment_id,
                timeout=10.0
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error cancelando turno: {e}")
            return False