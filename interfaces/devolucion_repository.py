"""
Interfaz para el repositorio de Devoluciones
Define el contrato que debe cumplir cualquier implementación
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from bson import ObjectId
from domain.devolucion import Devolución


class DevolucionRepository(ABC):
    """Interfaz para operaciones CRUD de devoluciones"""
    
    @abstractmethod
    def crear(self, devolucion: Devolución) -> Devolución:
        """Crea una nueva devolución y retorna con ID asignado"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, devolucion_id: ObjectId) -> Optional[Devolución]:
        """Obtiene una devolución por su ID"""
        pass
    
    @abstractmethod
    def obtener_todos(self) -> List[Devolución]:
        """Obtiene todas las devoluciones"""
        pass
    
    @abstractmethod
    def obtener_por_prestamo(self, prestamo_id: ObjectId) -> List[Devolución]:
        """Obtiene todas las devoluciones relacionadas a un préstamo"""
        pass
    
    @abstractmethod
    def obtener_por_docente_nfc(self, codigo_nfc: str) -> List[Devolución]:
        """Obtiene todas las devoluciones de un docente por su código NFC"""
        pass
    
    @abstractmethod
    def buscar(self, criterios: dict) -> List[Devolución]:
        """Busca devoluciones según criterios"""
        pass
