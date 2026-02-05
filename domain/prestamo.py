"""
Entidad Préstamo - Modelo de dominio
Representa un préstamo de equipos a un docente
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from bson import ObjectId


@dataclass
class DetallePréstamo:
    """Detalle de un equipo prestado (item individual)"""
    
    equipo_id: ObjectId
    equipo_nombre: str
    equipo_marca: str
    equipo_codigo: str
    cantidad: int
    
    def to_dict(self):
        return {
            'equipo_id': self.equipo_id,
            'equipo_nombre': self.equipo_nombre,
            'equipo_marca': self.equipo_marca,
            'equipo_codigo': self.equipo_codigo,
            'cantidad': self.cantidad
        }


@dataclass
class Préstamo:
    """Representación de un préstamo de equipos"""
    
    docente_codigo_nfc: str  # Código NFC del docente
    docente_nombre: str  # Nombre del docente
    auxiliar_prestamista: str  # Nombre del auxiliar que prestó
    
    docente_id: Optional[ObjectId] = None  # ID del docente en BD
    equipos: List[DetallePréstamo] = field(default_factory=list)
    auxiliar_id: Optional[ObjectId] = None  # ID del auxiliar en BD
    
    fecha_prestamo: datetime = field(default_factory=datetime.now)
    fecha_prevista_devolucion: Optional[datetime] = None  # Opcional: plazo para devolver
    
    estado: str = "activo"  # "activo", "parcialmente_devuelto", "completamente_devuelto", "vencido"
    notas: Optional[str] = None
    
    id: Optional[ObjectId] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    
    def agregar_equipo(self, equipo_id: ObjectId, nombre: str, marca: str, codigo: str, cantidad: int):
        """Agrega un equipo al préstamo"""
        # Verificar que no esté duplicado
        for det in self.equipos:
            if det.equipo_id == equipo_id:
                det.cantidad += cantidad
                return
        
        # Agregar nuevo
        self.equipos.append(DetallePréstamo(
            equipo_id=equipo_id,
            equipo_nombre=nombre,
            equipo_marca=marca,
            equipo_codigo=codigo,
            cantidad=cantidad
        ))
    
    def obtener_total_items(self) -> int:
        """Retorna la cantidad total de items prestados"""
        return sum(item.cantidad for item in self.equipos)
    
    def está_vencido(self) -> bool:
        """Verifica si el plazo de devolución pasó"""
        if self.fecha_prevista_devolucion is None:
            return False
        return datetime.now() > self.fecha_prevista_devolucion
    
    def to_dict(self):
        """Convierte a diccionario para persistencia"""
        data = {
            'docente_codigo_nfc': self.docente_codigo_nfc,
            'docente_nombre': self.docente_nombre,
            'docente_id': self.docente_id,
            'equipos': [equipo.to_dict() for equipo in self.equipos],
            'auxiliar_prestamista': self.auxiliar_prestamista,
            'auxiliar_id': self.auxiliar_id,
            'fecha_prestamo': self.fecha_prestamo,
            'fecha_prevista_devolucion': self.fecha_prevista_devolucion,
            'estado': self.estado,
            'notas': self.notas,
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
        # Reconstruir detalles
        equipos = [
            DetallePréstamo(
                equipo_id=item['equipo_id'],
                equipo_nombre=item['equipo_nombre'],
                equipo_marca=item['equipo_marca'],
                equipo_codigo=item['equipo_codigo'],
                cantidad=item['cantidad']
            )
            for item in data.get('equipos', [])
        ]
        
        obj = cls(
            docente_codigo_nfc=data['docente_codigo_nfc'],
            docente_nombre=data['docente_nombre'],
            docente_id=data.get('docente_id'),
            equipos=equipos,
            auxiliar_prestamista=data['auxiliar_prestamista'],
            auxiliar_id=data.get('auxiliar_id'),
            fecha_prestamo=data.get('fecha_prestamo', datetime.now()),
            fecha_prevista_devolucion=data.get('fecha_prevista_devolucion'),
            estado=data.get('estado', 'activo'),
            notas=data.get('notas')
        )
        obj.id = data.get('_id')
        obj.fecha_creacion = data.get('fecha_creacion', datetime.now())
        obj.fecha_actualizacion = data.get('fecha_actualizacion', datetime.now())
        return obj
