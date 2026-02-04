"""
Servicio de Equipos - Lógica de negocio para gestión de inventario
"""
from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime

from domain.equipo import Equipo
from infrastructure.repositories.equipo_mongo_repository import EquipoMongoRepository


class EquipoService:
    """Casos de uso para gestión de equipos"""
    
    def __init__(self, equipo_repository: EquipoMongoRepository = None):
        self.repository = equipo_repository or EquipoMongoRepository()
    
    def registrar_equipo(
        self,
        nombre: str,
        marca: str,
        codigo_inventario: str,
        cantidad_total: int,
        descripcion: str = None,
        ubicacion: str = None
    ) -> Equipo:
        """Registra un nuevo equipo en el inventario"""
        
        # Validar que no exista código duplicado
        existente = self.repository.obtener_por_codigo(codigo_inventario)
        if existente:
            raise ValueError(f"Ya existe un equipo con código: {codigo_inventario}")
        
        # Crear equipo
        equipo = Equipo(
            nombre=nombre,
            marca=marca,
            codigo_inventario=codigo_inventario,
            cantidad_total=cantidad_total,
            descripcion=descripcion,
            ubicacion=ubicacion
        )
        
        return self.repository.crear(equipo)
    
    def obtener_todo_inventario(self) -> List[Equipo]:
        """Obtiene todo el inventario de equipos"""
        return self.repository.obtener_todos()
    
    def obtener_equipos_disponibles(self) -> List[Equipo]:
        """Obtiene solo equipos disponibles para prestar"""
        return self.repository.obtener_disponibles()
    
    def obtener_equipo(self, equipo_id: ObjectId) -> Optional[Equipo]:
        """Obtiene un equipo específico"""
        return self.repository.obtener_por_id(equipo_id)
    
    def actualizar_equipo(
        self,
        equipo_id: ObjectId,
        nombre: str = None,
        marca: str = None,
        descripcion: str = None,
        ubicacion: str = None
    ) -> Optional[Equipo]:
        """Actualiza información de un equipo"""
        
        equipo = self.repository.obtener_por_id(equipo_id)
        if not equipo:
            return None
        
        if nombre:
            equipo.nombre = nombre
        if marca:
            equipo.marca = marca
        if descripcion:
            equipo.descripcion = descripcion
        if ubicacion:
            equipo.ubicacion = ubicacion
        
        self.repository.actualizar(equipo)
        return equipo
    
    def reponer_equipo(self, equipo_id: ObjectId, cantidad: int) -> Optional[Equipo]:
        """Agrega más cantidad de un equipo (reposición)"""
        
        equipo = self.repository.obtener_por_id(equipo_id)
        if not equipo:
            return None
        
        if cantidad <= 0:
            raise ValueError("La cantidad a reponer debe ser mayor a 0")
        
        equipo.cantidad_total += cantidad
        equipo.cantidad_disponible += cantidad
        
        self.repository.actualizar(equipo)
        return equipo
    
    def marcar_equipo_dañado(self, equipo_id: ObjectId, cantidad: int = 1) -> Optional[Equipo]:
        """Marca equipo como dañado, reduciendo cantidad disponible"""
        
        equipo = self.repository.obtener_por_id(equipo_id)
        if not equipo:
            return None
        
        if cantidad > equipo.cantidad_total:
            raise ValueError(f"Solo hay {equipo.cantidad_total} unidades totales")
        
        equipo.cantidad_total -= cantidad
        if equipo.cantidad_disponible > equipo.cantidad_total:
            equipo.cantidad_disponible = equipo.cantidad_total
        
        self.repository.actualizar(equipo)
        return equipo
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del inventario"""
        equipos = self.repository.obtener_todos()
        
        total_equipos = len(equipos)
        cantidad_total = sum(e.cantidad_total for e in equipos)
        cantidad_disponible = sum(e.cantidad_disponible for e in equipos)
        cantidad_prestada = cantidad_total - cantidad_disponible
        
        return {
            'total_tipos_equipo': total_equipos,
            'cantidad_total_unidades': cantidad_total,
            'cantidad_disponible': cantidad_disponible,
            'cantidad_prestada': cantidad_prestada,
            'porcentaje_disponible': round((cantidad_disponible / cantidad_total * 100) if cantidad_total > 0 else 0, 2)
        }
