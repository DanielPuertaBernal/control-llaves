"""
Interfaz para el repositorio de Equipos
Define el contrato que debe cumplir cualquier implementación
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from bson import ObjectId
from domain.equipo import Equipo


class EquipoRepository(ABC):
    """Interfaz para operaciones CRUD de equipos"""
    
    @abstractmethod
    def crear(self, equipo: Equipo) -> Equipo:
        """Crea un nuevo equipo y retorna con ID asignado"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, equipo_id: ObjectId) -> Optional[Equipo]:
        """Obtiene un equipo por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_codigo(self, codigo_inventario: str) -> Optional[Equipo]:
        """Obtiene un equipo por su código de inventario"""
        pass

    @abstractmethod
    def obtener_por_codigo_barras(self, codigo_barras: str) -> Optional[Equipo]:
        """Obtiene un equipo por su código de barras"""
        pass
    
    @abstractmethod
    def obtener_todos(self) -> List[Equipo]:
        """Obtiene todos los equipos"""
        pass
    
    @abstractmethod
    def obtener_disponibles(self) -> List[Equipo]:
        """Obtiene solo equipos con disponibilidad > 0"""
        pass
    
    @abstractmethod
    def actualizar(self, equipo_id: ObjectId, equipo: Equipo) -> Optional[Equipo]:
        """Actualiza un equipo existente"""
        pass
    
    @abstractmethod
    def eliminar(self, equipo_id: ObjectId) -> bool:
        """Elimina un equipo (marca como inactivo)"""
        pass
    
    @abstractmethod
    def buscar(self, criterios: dict) -> List[Equipo]:
        """Busca equipos según criterios"""
        pass
