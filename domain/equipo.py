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
    consecutivo: int  # Consecutivo único por tipo de equipo (Ej: 1, 2, 5)
    codigo_inventario: str  # Código del tipo de equipo en inventario
    descripcion: Optional[str] = None
    estado: str = "activo"  # "activo", "dañado", "descartado"
    codigo_barras: str = ""  # Código de barras único, generado automáticamente
    
    id: Optional[ObjectId] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones después de inicializar"""
        if not self.codigo_inventario or not self.codigo_inventario.strip():
            raise ValueError("El código de inventario es requerido")
        if self.consecutivo <= 0:
            raise ValueError("El consecutivo debe ser mayor a 0")
        if not self.codigo_barras:
            self.codigo_barras = self.generar_codigo_barras()
    
    def generar_codigo_barras(self) -> str:
        """Genera un código de barras único: INV-{codigo}-{consecutivo:03d}"""
        return f"INV-{self.codigo_inventario}-{self.consecutivo:03d}"
    
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
            'consecutivo': self.consecutivo,
            'codigo_inventario': self.codigo_inventario,
            'codigo_barras': self.codigo_barras,
            'descripcion': self.descripcion,
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
            consecutivo=data.get('consecutivo', 1),
            codigo_inventario=data['codigo_inventario'],
            codigo_barras=data.get('codigo_barras', ''),
            descripcion=data.get('descripcion'),
            estado=data.get('estado', 'activo')
        )
        obj.id = data.get('_id')
        obj.fecha_creacion = data.get('fecha_creacion', datetime.now())
        obj.fecha_actualizacion = data.get('fecha_actualizacion', datetime.now())
        return obj
