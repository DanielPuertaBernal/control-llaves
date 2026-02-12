"""
Entidad Préstamo - Modelo de dominio
Representa un préstamo de equipos a un docente
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from bson import ObjectId


@dataclass
class DetallePréstamo:
    """Detalle de un equipo prestado con ciclo de vida completo (entrega y devolución)"""
    
    equipo_id: ObjectId
    equipo_nombre: str
    equipo_marca: str
    equipo_codigo: str
    equipo_consecutivo: int  # Consecutivo del equipo
    equipo_codigo_barras: str  # Código de barras del equipo
    
    # Ciclo de vida del equipo en el préstamo
    estado_equipo: str = "entregado"  # "entregado", "devuelto"
    fecha_entrega: datetime = field(default_factory=datetime.now)
    fecha_devolucion: Optional[datetime] = None
    auxiliar_que_recibio_devolucion: Optional[str] = None  # Quién recibió la devolución
    
    def to_dict(self):
        return {
            'equipo_id': self.equipo_id,
            'equipo_nombre': self.equipo_nombre,
            'equipo_marca': self.equipo_marca,
            'equipo_codigo': self.equipo_codigo,
            'equipo_consecutivo': self.equipo_consecutivo,
            'equipo_codigo_barras': self.equipo_codigo_barras,
            'estado_equipo': self.estado_equipo,
            'fecha_entrega': self.fecha_entrega,
            'fecha_devolucion': self.fecha_devolucion,
            'auxiliar_que_recibio_devolucion': self.auxiliar_que_recibio_devolucion
        }
    
    @staticmethod
    def from_dict(data: dict):
        return DetallePréstamo(
            equipo_id=data.get('equipo_id'),
            equipo_nombre=data.get('equipo_nombre', ''),
            equipo_marca=data.get('equipo_marca', ''),
            equipo_codigo=data.get('equipo_codigo', ''),
            equipo_consecutivo=data.get('equipo_consecutivo', 0),
            equipo_codigo_barras=data.get('equipo_codigo_barras', ''),
            estado_equipo=data.get('estado_equipo', 'entregado'),
            fecha_entrega=data.get('fecha_entrega', datetime.now()),
            fecha_devolucion=data.get('fecha_devolucion'),
            auxiliar_que_recibio_devolucion=data.get('auxiliar_que_recibio_devolucion')
        )


@dataclass
class Préstamo:
    """Representación de un préstamo de equipos"""
    
    docente_codigo_nfc: str  # Código NFC del docente
    docente_nombre: str  # Nombre del docente
    auxiliar_prestamista: str  # Nombre del auxiliar que prestó
    
    equipos: List[DetallePréstamo] = field(default_factory=list)
    
    fecha_prestamo: datetime = field(default_factory=datetime.now)
    estado: str = "activo"  # "activo", "parcialmente_devuelto", "completamente_devuelto", "vencido"
    
    id: Optional[ObjectId] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    
    def agregar_equipo(self, equipo_id: ObjectId, nombre: str, marca: str, codigo: str, consecutivo: int, codigo_barras: str):
        """Agrega un equipo al préstamo (cada equipo es único, sin cantidad)"""
        # Verificar que no esté duplicado
        for det in self.equipos:
            if det.equipo_id == equipo_id:
                return  # Ya está en el préstamo, no agregar duplicado
        
        # Agregar nuevo
        self.equipos.append(DetallePréstamo(
            equipo_id=equipo_id,
            equipo_nombre=nombre,
            equipo_marca=marca,
            equipo_codigo=codigo,
            equipo_consecutivo=consecutivo,
            equipo_codigo_barras=codigo_barras
        ))
    
    def obtener_total_items(self) -> int:
        """Retorna la cantidad total de equipos prestados (cada equipo cuenta como 1)"""
        return len(self.equipos)
    
    def to_dict(self):
        """Convierte a diccionario para persistencia"""
        data = {
            'docente_codigo_nfc': self.docente_codigo_nfc,
            'docente_nombre': self.docente_nombre,
            'equipos': [equipo.to_dict() for equipo in self.equipos],
            'auxiliar_prestamista': self.auxiliar_prestamista,
            'fecha_prestamo': self.fecha_prestamo,
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
        # Reconstruir detalles - usar DetallePréstamo.from_dict para capturar todos los campos
        equipos = [
            DetallePréstamo.from_dict(item)
            for item in data.get('equipos', [])
        ]
        
        obj = cls(
            docente_codigo_nfc=data['docente_codigo_nfc'],
            docente_nombre=data['docente_nombre'],
            equipos=equipos,
            auxiliar_prestamista=data['auxiliar_prestamista'],
            fecha_prestamo=data.get('fecha_prestamo', datetime.now()),
            estado=data.get('estado', 'activo')
        )
        obj.id = data.get('_id')
        obj.fecha_creacion = data.get('fecha_creacion', datetime.now())
        obj.fecha_actualizacion = data.get('fecha_actualizacion', datetime.now())
        return obj
