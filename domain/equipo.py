"""
Entidad Equipo - Modelo de dominio
Representa un equipo/elemento que puede ser prestado
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from bson import ObjectId


@dataclass
class Equipo:
    """Representación de un equipo de inventario"""
    
    nombre: str  # Ej: "Bafle", "Cable de Internet", "HDMI"
    marca: str  # Ej: "Sony", "Belkin", "Generic"
    codigo_inventario: str  # Código único del inventario
    cantidad_total: int  # Cantidad total de unidades disponibles
    cantidad_disponible: int = None  # Se calcula automáticamente
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None  # Donde se guarda
    estado: str = "activo"  # "activo", "dañado", "descartado"
    
    id: Optional[ObjectId] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones después de inicializar"""
        if self.cantidad_disponible is None:
            self.cantidad_disponible = self.cantidad_total
        
        if self.cantidad_total <= 0:
            raise ValueError("La cantidad total debe ser mayor a 0")
        
        if self.cantidad_disponible > self.cantidad_total:
            raise ValueError("La cantidad disponible no puede superar la total")
    
    def está_disponible(self, cantidad: int = 1) -> bool:
        """Verifica si hay suficiente cantidad disponible"""
        return self.cantidad_disponible >= cantidad
    
    def prestar(self, cantidad: int = 1):
        """Reduce la cantidad disponible al prestar"""
        if not self.está_disponible(cantidad):
            raise ValueError(f"Solo hay {self.cantidad_disponible} disponibles")
        self.cantidad_disponible -= cantidad
    
    def devolver(self, cantidad: int = 1):
        """Aumenta la cantidad disponible al devolver"""
        self.cantidad_disponible += cantidad
        if self.cantidad_disponible > self.cantidad_total:
            self.cantidad_disponible = self.cantidad_total
    
    def to_dict(self):
        """Convierte a diccionario para persistencia"""
        return {
            'nombre': self.nombre,
            'marca': self.marca,
            'codigo_inventario': self.codigo_inventario,
            'cantidad_total': self.cantidad_total,
            'cantidad_disponible': self.cantidad_disponible,
            'descripcion': self.descripcion,
            'ubicacion': self.ubicacion,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        obj = cls(
            nombre=data['nombre'],
            marca=data['marca'],
            codigo_inventario=data['codigo_inventario'],
            cantidad_total=data['cantidad_total'],
            cantidad_disponible=data.get('cantidad_disponible', data['cantidad_total']),
            descripcion=data.get('descripcion'),
            ubicacion=data.get('ubicacion'),
            estado=data.get('estado', 'activo')
        )
        obj.id = data.get('_id')
        obj.fecha_creacion = data.get('fecha_creacion', datetime.now())
        obj.fecha_actualizacion = data.get('fecha_actualizacion', datetime.now())
        return obj
