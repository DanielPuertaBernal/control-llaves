"""
Entidad de Dominio: Llave
Representa una llave con su estado y reglas de negocio
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EstadoLlave(Enum):
    """Estados posibles de una llave"""
    EN_PRESTAMO = "En Préstamo"
    DEVUELTA = "Devuelta"
    EXTRAVIADA = "Extraviada"


@dataclass
class Llave:
    """Entidad de dominio para una llave"""
    numero_documento: str
    docente: str
    aula: str
    materia: str
    horario: str
    dia: str
    estado: EstadoLlave = EstadoLlave.EN_PRESTAMO
    fecha_entrega: datetime = None
    hora_entrega: str = None
    fecha_devolucion: datetime = None
    hora_devolucion: str = None
    facultad: str = None
    duracion: str = None
    retraso_devolucion: str = None
    
    def __post_init__(self):
        """Valida que la llave sea válida"""
        self._validar()
    
    def _validar(self):
        """Valida los campos requeridos"""
        if not self.numero_documento or not self.numero_documento.strip():
            raise ValueError("El número de documento es requerido")
        if not self.docente or not self.docente.strip():
            raise ValueError("El nombre del docente es requerido")
        if not self.aula or not self.aula.strip():
            raise ValueError("El aula es requerida")
        if not self.horario or not self.horario.strip():
            raise ValueError("El horario es requerido")
    
    def puede_devolverse(self) -> bool:
        """Valida si la llave puede ser devuelta"""
        return self.estado == EstadoLlave.EN_PRESTAMO
    
    def registrar_entrega(self, fecha: datetime, hora: str):
        """Registra la entrega de la llave"""
        if self.estado != EstadoLlave.EN_PRESTAMO:
            raise ValueError(f"No se puede entregar una llave en estado {self.estado.value}")
        self.fecha_entrega = fecha
        self.hora_entrega = hora
        self.estado = EstadoLlave.EN_PRESTAMO
    
    def registrar_devolucion(self, fecha: datetime, hora: str):
        """Registra la devolución de la llave"""
        if not self.puede_devolverse():
            raise ValueError(f"No se puede devolver una llave en estado {self.estado.value}")
        self.fecha_devolucion = fecha
        self.hora_devolucion = hora
        self.estado = EstadoLlave.DEVUELTA
    
    def marcar_extraviada(self):
        """Marca la llave como extraviada"""
        self.estado = EstadoLlave.EXTRAVIADA
    
    def a_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            'Número de Documento': self.numero_documento,
            'Docente': self.docente,
            'Aula': self.aula,
            'Materia de la Clase': self.materia,
            'Horario': self.horario,
            'Día': self.dia,
            'Estado': self.estado.value,
            'Fecha de entrega': self.fecha_entrega.strftime('%Y-%m-%d') if self.fecha_entrega else None,
            'Hora de entrega': self.hora_entrega,
            'Fecha de devolución': self.fecha_devolucion.strftime('%Y-%m-%d') if self.fecha_devolucion else None,
            'Hora de devolución': self.hora_devolucion,
            'Facultad': self.facultad,
            'Duración clase (entrega→devolución)': self.duracion,
            'Tiempo retraso devolución': self.retraso_devolucion
        }
