"""
Servicios auxiliares del sistema
Componentes reutilizables para funcionalidades comunes
"""
from .paginacion_service import PaginacionService
from .tabla_service import TablaService
from .nfc_service import NFCService

__all__ = ['PaginacionService', 'TablaService', 'NFCService']
