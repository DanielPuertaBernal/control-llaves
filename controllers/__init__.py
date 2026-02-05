"""
Controladores del sistema MVC
Capa de lógica de negocio
"""
from .llave_controller import LlaveController
from .programacion_controller import ProgramacionController
from .historial_controller import HistorialController
from .docente_controller import DocenteController
from .equipo_controller import EquipoController
from .prestamo_controller import PréstamoController
from .devolucion_controller import DevolucionController

__all__ = [
    'LlaveController', 
    'ProgramacionController', 
    'HistorialController', 
    'DocenteController',
    'EquipoController',
    'PréstamoController',
    'DevolucionController'
]
