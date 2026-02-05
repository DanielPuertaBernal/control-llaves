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
        consecutivo: str,
        codigo_inventario: str,
        descripcion: str = None
    ) -> Equipo:
        """Registra una nueva instancia de equipo en el inventario"""
        
        # Validar que el código de inventario sea único en todo el sistema
        existente_codigo = self.repository.obtener_por_codigo(codigo_inventario)
        if existente_codigo:
            raise ValueError(f"Ya existe un equipo con código de inventario '{codigo_inventario}'. El código debe ser único.")
        
        # Crear equipo
        equipo = Equipo(
            nombre=nombre,
            marca=marca,
            consecutivo=int(consecutivo),
            codigo_inventario=codigo_inventario,
            descripcion=descripcion
        )
        
        return self.repository.crear(equipo)
    
    def obtener_todo_inventario(self) -> List[Equipo]:
        """Obtiene todo el inventario de equipos"""
        return self.repository.obtener_todos()
    
    def obtener_equipos_disponibles(self) -> List[Equipo]:
        """Obtiene solo equipos disponibles para prestar (estado activo)"""
        equipos = self.repository.obtener_todos()
        return [e for e in equipos if e.está_disponible()]
    
    def obtener_equipo(self, equipo_id: ObjectId) -> Optional[Equipo]:
        """Obtiene un equipo específico"""
        return self.repository.obtener_por_id(equipo_id)
    
    def obtener_por_numero_serie(self, numero_serie: str) -> Optional[Equipo]:
        """Obtiene un equipo por su número de serie"""
        return self.repository.obtener_por_numero_serie(numero_serie)
    
    def actualizar_equipo(
        self,
        equipo_id: ObjectId,
        nombre: str = None,
        marca: str = None,
        consecutivo: str = None,
        descripcion: str = None,
        estado: str = None
    ) -> Optional[Equipo]:
        """Actualiza información de un equipo"""
        
        equipo = self.repository.obtener_por_id(equipo_id)
        if not equipo:
            return None
        
        if nombre:
            equipo.nombre = nombre
        if marca:
            equipo.marca = marca
        if consecutivo:
            equipo.consecutivo = int(consecutivo)
        if descripcion:
            equipo.descripcion = descripcion
        if estado:
            equipo.estado = estado
        
        equipo.fecha_actualizacion = datetime.now()
        
        return self.repository.actualizar(equipo_id, equipo)
    
    def marcar_dañado(self, equipo_id: ObjectId) -> Optional[Equipo]:
        """Marca un equipo como dañado"""
        equipo = self.repository.obtener_por_id(equipo_id)
        if not equipo:
            return None
        
        equipo.marcar_dañado()
        return self.repository.actualizar(equipo_id, equipo)
    
    def reparar_equipo(self, equipo_id: ObjectId) -> Optional[Equipo]:
        """Marca un equipo como reparado (activo)"""
        equipo = self.repository.obtener_por_id(equipo_id)
        if not equipo:
            return None
        
        equipo.reparar()
        return self.repository.actualizar(equipo_id, equipo)
    
    def eliminar_equipo(self, equipo_id: ObjectId) -> bool:
        """Elimina un equipo del inventario"""
        return self.repository.eliminar(equipo_id)
        
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
    
    def eliminar_equipo(self, equipo_id: ObjectId) -> bool:
        """Elimina un equipo del inventario"""
        return self.repository.eliminar(equipo_id)
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del inventario"""
        equipos = self.repository.obtener_todos()
        
        total_equipos = len(equipos)
        equipos_disponibles = len([e for e in equipos if e.está_disponible()])
        equipos_dañados = len([e for e in equipos if e.estado == "dañado"])
        
        return {
            'total_equipos': total_equipos,
            'equipos_disponibles': equipos_disponibles,
            'equipos_dañados': equipos_dañados,
            'porcentaje_disponible': round((equipos_disponibles / total_equipos * 100) if total_equipos > 0 else 0, 2)
        }
