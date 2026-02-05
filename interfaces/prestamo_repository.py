"""
Interfaz para el repositorio de Préstamos
Define el contrato que debe cumplir cualquier implementación
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from bson import ObjectId
from domain.prestamo import Préstamo


class PréstamoRepository(ABC):
    """Interfaz para operaciones CRUD de préstamos"""
    
    @abstractmethod
    def crear(self, prestamo: Préstamo) -> Préstamo:
        """Crea un nuevo préstamo y retorna con ID asignado"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, prestamo_id: ObjectId) -> Optional[Préstamo]:
        """Obtiene un préstamo por su ID"""
        pass
    
    @abstractmethod
    def obtener_todos(self) -> List[Préstamo]:
        """Obtiene todos los préstamos"""
        pass
    
    @abstractmethod
    def obtener_activos(self) -> List[Préstamo]:
        """Obtiene solo préstamos activos"""
        pass
    
    @abstractmethod
    def obtener_por_docente_nfc(self, codigo_nfc: str) -> List[Préstamo]:
        """Obtiene todos los préstamos de un docente por su código NFC"""
        pass
    
    @abstractmethod
    def obtener_activos_por_docente(self, codigo_nfc: str) -> List[Préstamo]:
        """Obtiene préstamos activos de un docente específico"""
        pass
    
    @abstractmethod
    def actualizar(self, prestamo: Préstamo) -> bool:
        """Actualiza un préstamo existente"""
        pass
    
    @abstractmethod
    def buscar(self, criterios: dict) -> List[Préstamo]:
        """Busca préstamos según criterios"""
        pass
