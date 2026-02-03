"""
Data Transfer Objects (DTOs)
Transforman datos entre capas sin exponer entidades internas
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class LlaveDTO:
    """DTO para Llave - transferencia entre capas"""
    numero_documento: str
    docente: str
    aula: str
    materia: str
    horario: str
    dia: str
    estado: str = "En Préstamo"
    fecha_entrega: Optional[str] = None
    hora_entrega: Optional[str] = None
    fecha_devolucion: Optional[str] = None
    hora_devolucion: Optional[str] = None
    facultad: Optional[str] = None
    
    @classmethod
    def desde_dict(cls, data: Dict[str, Any]) -> 'LlaveDTO':
        """Crea un DTO desde un diccionario"""
        return cls(
            numero_documento=data.get('Número de Documento'),
            docente=data.get('Docente'),
            aula=data.get('Aula'),
            materia=data.get('Materia de la Clase'),
            horario=data.get('Horario'),
            dia=data.get('Día'),
            estado=data.get('Estado', 'En Préstamo'),
            fecha_entrega=data.get('Fecha de entrega'),
            hora_entrega=data.get('Hora de entrega'),
            fecha_devolucion=data.get('Fecha de devolución'),
            hora_devolucion=data.get('Hora de devolución'),
            facultad=data.get('Facultad')
        )
    
    def a_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para persistencia"""
        return {
            'Número de Documento': self.numero_documento,
            'Docente': self.docente,
            'Aula': self.aula,
            'Materia de la Clase': self.materia,
            'Horario': self.horario,
            'Día': self.dia,
            'Estado': self.estado,
            'Fecha de entrega': self.fecha_entrega,
            'Hora de entrega': self.hora_entrega,
            'Fecha de devolución': self.fecha_devolucion,
            'Hora de devolución': self.hora_devolucion,
            'Facultad': self.facultad
        }


@dataclass
class DocenteDTO:
    """DTO para Docente - transferencia entre capas"""
    numero_documento: str
    nombre: str
    facultad: Optional[str] = None
    tipo: Optional[str] = None
    correo: Optional[str] = None
    id_carnet: Optional[str] = None
    
    @classmethod
    def desde_dict(cls, data: Dict[str, Any]) -> 'DocenteDTO':
        """Crea un DTO desde un diccionario"""
        return cls(
            numero_documento=data.get('Numero de documento'),
            nombre=data.get('Nombre'),
            facultad=data.get('Facultad'),
            tipo=data.get('Tipo'),
            correo=data.get('Correo'),
            id_carnet=data.get('ID Carnet')
        )
    
    def a_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'Numero de documento': self.numero_documento,
            'Nombre': self.nombre,
            'Facultad': self.facultad,
            'Tipo': self.tipo,
            'Correo': self.correo,
            'ID Carnet': self.id_carnet
        }


@dataclass
class ClaseDTO:
    """DTO para Clase - transferencia entre capas"""
    numero_documento: str
    docente: str
    dia: str
    horario: str
    aula: str
    materia: str
    codigo_materia: Optional[str] = None
    grupo: Optional[str] = None
    facultad: Optional[str] = None
    semestre: Optional[str] = None
    
    @classmethod
    def desde_dict(cls, data: Dict[str, Any]) -> 'ClaseDTO':
        """Crea un DTO desde un diccionario"""
        return cls(
            numero_documento=data.get('Número de Documento'),
            docente=data.get('Docente'),
            dia=data.get('Día'),
            horario=data.get('Horario'),
            aula=data.get('Aula'),
            materia=data.get('Materia de la Clase'),
            codigo_materia=data.get('Código Materia'),
            grupo=data.get('Grupo'),
            facultad=data.get('Facultad'),
            semestre=data.get('Semestre')
        )
    
    def a_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'Número de Documento': self.numero_documento,
            'Docente': self.docente,
            'Día': self.dia,
            'Horario': self.horario,
            'Aula': self.aula,
            'Materia de la Clase': self.materia,
            'Código Materia': self.codigo_materia,
            'Grupo': self.grupo,
            'Facultad': self.facultad,
            'Semestre': self.semestre
        }


@dataclass
class ResultadoNFCDTO:
    """DTO para resultado de operación NFC"""
    exito: bool
    accion: str  # 'entrega', 'devolucion', 'advertencia', 'error'
    mensaje: str
    datos_docente: Optional[Dict[str, Any]] = None
    datos_clase: Optional[Dict[str, Any]] = None
    requiere_confirmacion: bool = False
    tiempo_faltante: Optional[str] = None
    callback_confirmar: Optional[callable] = None
    hora_operacion: Optional[str] = None
    
    def a_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario (sin callback)"""
        return {
            'exito': self.exito,
            'accion': self.accion,
            'mensaje': self.mensaje,
            'datos_docente': self.datos_docente,
            'datos_clase': self.datos_clase,
            'requiere_confirmacion': self.requiere_confirmacion,
            'tiempo_faltante': self.tiempo_faltante,
            'hora_operacion': self.hora_operacion
        }
