"""
Entidad de Dominio: Docente
Representa un docente con sus datos y validaciones
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Docente:
    """Entidad de dominio para un docente"""
    numero_documento: str
    nombre: str
    facultad: Optional[str] = None
    tipo: Optional[str] = None
    correo: Optional[str] = None
    id_carnet: Optional[str] = None
    
    def __post_init__(self):
        """Valida que el docente sea válido"""
        self._validar()
    
    def _validar(self):
        """Valida los campos requeridos"""
        if not self.numero_documento or not self.numero_documento.strip():
            raise ValueError("El número de documento es requerido")
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del docente es requerido")
    
    def limpiar_numero_documento(self) -> str:
        """Retorna el documento limpio (sin .0)"""
        return str(self.numero_documento).replace('.0', '').strip()
    
    def es_valido(self) -> bool:
        """Valida si el docente tiene datos válidos"""
        try:
            self._validar()
            return True
        except ValueError:
            return False
    
    def a_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            'Numero de documento': self.numero_documento,
            'Nombre': self.nombre,
            'Facultad': self.facultad,
            'Tipo': self.tipo,
            'Correo': self.correo,
            'ID Carnet': self.id_carnet
        }
