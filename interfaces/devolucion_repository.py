"""
Interfaz para el repositorio de Devoluciones
Define el contrato que debe cumplir cualquier implementación
"""
from abc import ABC, abstractmethod
from typing import Optional
from bson import ObjectId
from domain.devolucion import Devolución


class DevolucionRepository(ABC):
    """Interfaz para operaciones CRUD de devoluciones"""
    
    @abstractmethod
    def crear(self, devolucion: Devolución) -> Devolución:
        """Crea una nueva devolución y retorna con ID asignado"""
        pass
