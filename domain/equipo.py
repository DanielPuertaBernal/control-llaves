"""
Entidad Equipo - Modelo de dominio
Representa una instancia individual de un equipo que puede ser prestado
(Ej: Bafle 1, Bafle 2, Cable HDMI #5, etc.)
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from bson import ObjectId


@dataclass
class Equipo:
    """Representación de una instancia individual de equipo"""
    
    nombre: str  # Ej: "Bafle", "Cable HDMI", "Proyector"
    marca: str  # Ej: "Sony", "Belkin", "Epson"
    numero_serie: str  # Identificador único (Ej: "BAFLE_001", "CABLE_HDMI_005")
    codigo_inventario: str  # Código del tipo de equipo en inventario
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None  # Donde se guarda normalmente
    estado: str = "activo"  # "activo", "dañado", "descartado"
    
    id: Optional[ObjectId] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones después de inicializar"""
        if not self.numero_serie or not self.numero_serie.strip():
            raise ValueError("El número de serie es requerido")
    
    def está_disponible(self) -> bool:
        """Verifica si el equipo está disponible para prestar"""
        return self.estado == "activo"
    
    def marcar_dañado(self):
        """Marca el equipo como dañado"""
        self.estado = "dañado"
        self.fecha_actualizacion = datetime.now()
    
    def reparar(self):
        """Marca el equipo como reparado (activo)"""
        self.estado = "activo"
        self.fecha_actualizacion = datetime.now()
    
    def to_dict(self):
        """Convierte a diccionario para persistencia"""
        data = {
            'nombre': self.nombre,
            'marca': self.marca,
            'numero_serie': self.numero_serie,
            'codigo_inventario': self.codigo_inventario,
            'descripcion': self.descripcion,
            'ubicacion': self.ubicacion,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }
        
        # Incluir _id si existe
        if self.id:
            data['_id'] = self.id
            
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        obj = cls(
            nombre=data['nombre'],
            marca=data['marca'],
            numero_serie=data['numero_serie'],
            codigo_inventario=data['codigo_inventario'],
            descripcion=data.get('descripcion'),
            ubicacion=data.get('ubicacion'),
            estado=data.get('estado', 'activo')
        )
        obj.id = data.get('_id')
        obj.fecha_creacion = data.get('fecha_creacion', datetime.now())
        obj.fecha_actualizacion = data.get('fecha_actualizacion', datetime.now())
        return obj
