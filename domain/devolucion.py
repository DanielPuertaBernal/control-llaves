"""
Entidad Devolución - Modelo de dominio
Representa la devolución (total o parcial) de equipos prestados
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from bson import ObjectId


@dataclass
class DetalleDevolucion:
    """Detalle de un equipo devuelto"""
    
    equipo_id: ObjectId
    equipo_nombre: str
    cantidad_devuelta: int
    estado_equipo: str = "bueno"  # "bueno", "dañado", "extraviado"
    notas: Optional[str] = None
    
    def to_dict(self):
        return {
            'equipo_id': self.equipo_id,
            'equipo_nombre': self.equipo_nombre,
            'cantidad_devuelta': self.cantidad_devuelta,
            'estado_equipo': self.estado_equipo,
            'notas': self.notas
        }


@dataclass
class Devolución:
    """Representación de una devolución de equipos"""
    
    prestamo_id: ObjectId  # ID del préstamo original
    docente_codigo_nfc: str
    docente_nombre: str
    auxiliar_que_recibio: str  # Nombre del auxiliar que recibió
    
    equipos_devueltos: List[DetalleDevolucion] = field(default_factory=list)
    auxiliar_id: Optional[ObjectId] = None
    
    fecha_devolucion: datetime = field(default_factory=datetime.now)
    
    es_devolucion_completa: bool = True  # Si todos los items fueron devueltos
    notas: Optional[str] = None
    
    id: Optional[ObjectId] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    def agregar_equipo_devuelto(
        self, 
        equipo_id: ObjectId, 
        nombre: str, 
        cantidad: int, 
        estado: str = "bueno",
        notas: Optional[str] = None
    ):
        """Agrega un equipo devuelto"""
        self.equipos_devueltos.append(DetalleDevolucion(
            equipo_id=equipo_id,
            equipo_nombre=nombre,
            cantidad_devuelta=cantidad,
            estado_equipo=estado,
            notas=notas
        ))
    
    def obtener_total_items_devueltos(self) -> int:
        """Retorna la cantidad total de items devueltos"""
        return sum(item.cantidad_devuelta for item in self.equipos_devueltos)
    
    def to_dict(self):
        """Convierte a diccionario para persistencia"""
        data = {
            'prestamo_id': self.prestamo_id,
            'docente_codigo_nfc': self.docente_codigo_nfc,
            'docente_nombre': self.docente_nombre,
            'equipos_devueltos': [equipo.to_dict() for equipo in self.equipos_devueltos],
            'auxiliar_que_recibio': self.auxiliar_que_recibio,
            'auxiliar_id': self.auxiliar_id,
            'fecha_devolucion': self.fecha_devolucion,
            'es_devolucion_completa': self.es_devolucion_completa,
            'notas': self.notas,
            'fecha_creacion': self.fecha_creacion
        }
        
        # Incluir _id si existe
        if self.id:
            data['_id'] = self.id
            
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        equipos = [
            DetalleDevolucion(
                equipo_id=item['equipo_id'],
                equipo_nombre=item['equipo_nombre'],
                cantidad_devuelta=item['cantidad_devuelta'],
                estado_equipo=item.get('estado_equipo', 'bueno'),
                notas=item.get('notas')
            )
            for item in data.get('equipos_devueltos', [])
        ]
        
        obj = cls(
            prestamo_id=data['prestamo_id'],
            docente_codigo_nfc=data['docente_codigo_nfc'],
            docente_nombre=data['docente_nombre'],
            equipos_devueltos=equipos,
            auxiliar_que_recibio=data['auxiliar_que_recibio'],
            auxiliar_id=data.get('auxiliar_id'),
            fecha_devolucion=data.get('fecha_devolucion', datetime.now()),
            es_devolucion_completa=data.get('es_devolucion_completa', True),
            notas=data.get('notas')
        )
        obj.id = data.get('_id')
        obj.fecha_creacion = data.get('fecha_creacion', datetime.now())
        return obj
