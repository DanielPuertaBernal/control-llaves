"""
Entidad de Dominio: Clase
Representa una clase académica con sus datos
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Clase:
    """Entidad de dominio para una clase académica"""
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
    
    def __post_init__(self):
        """Valida que la clase sea válida"""
        self._validar()
    
    def _validar(self):
        """Valida los campos requeridos"""
        if not self.numero_documento or not self.numero_documento.strip():
            raise ValueError("El número de documento es requerido")
        if not self.docente or not self.docente.strip():
            raise ValueError("El docente es requerido")
        if not self.dia or not self.dia.strip():
            raise ValueError("El día es requerido")
        if not self.horario or not self.horario.strip():
            raise ValueError("El horario es requerido")
        if not self.aula or not self.aula.strip():
            raise ValueError("El aula es requerida")
        if not self.materia or not self.materia.strip():
            raise ValueError("La materia es requerida")
    
    def es_valida(self) -> bool:
        """Valida si la clase tiene datos válidos"""
        try:
            self._validar()
            return True
        except ValueError:
            return False
    
    def obtener_hora_inicio(self) -> Optional[str]:
        """Extrae la hora de inicio del horario"""
        try:
            horario = str(self.horario).strip()
            if '-' in horario:
                return horario.split('-')[0].strip()
            elif ' A ' in horario.upper():
                partes = [p for p in horario.split() if ':' in p]
                return partes[0].strip() if partes else None
            return horario
        except Exception:
            return None
    
    def limpiar_numero_documento(self) -> str:
        """Retorna el documento limpio (sin .0)"""
        return str(self.numero_documento).replace('.0', '').strip()
    
    def a_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
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
