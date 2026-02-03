"""Entidades del dominio (puras)"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Docente:
    numero_documento: str
    nombre: str
    facultad: Optional[str] = None
    tipo: Optional[str] = None
    correo: Optional[str] = None
    id_carnet: Optional[str] = None


@dataclass(frozen=True)
class ClaseProgramacion:
    codigo_materia: Optional[str]
    grupo: Optional[str]
    nivel_grupo: Optional[str]
    estudiantes_matriculados: Optional[int]
    total_estudiantes: Optional[int]
    numero_documento: str
    docente: str
    dia: str
    hora_inicio: Optional[str]
    hora_fin: Optional[str]
    aula: str
    facultad: Optional[str]
    materia_clase: str
    semestre: Optional[str]
    semanas: Optional[str]
    numero_horas: Optional[str]


@dataclass(frozen=True)
class RegistroLlave:
    numero_documento: str
    docente: str
    dia: str
    horario: str
    aula: str
    facultad: Optional[str]
    materia_clase: str
    fecha_entrega: str
    hora_entrega: str
    estado: str
    fecha_devolucion: Optional[str] = None
    hora_devolucion: Optional[str] = None
    duracion: Optional[str] = None
    se_reclamo_a_tiempo: Optional[str] = None
    tiempo_retraso: Optional[str] = None
    retraso_entrega: Optional[str] = None
    tiempo_retraso_devolucion: Optional[str] = None
