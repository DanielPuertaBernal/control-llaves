"""
Controlador de Devoluciones - Orquesta entre vistas y servicios
"""
from application.services.devolucion_service import DevolucionService


class DevolucionController:
    """Controlador para gestión de devoluciones"""
    
    def __init__(self, devolucion_service: DevolucionService = None):
        self.service = devolucion_service or DevolucionService()

    def crear_devolucion(self, prestamo_id, docente_nfc, docente_nombre, equipos, auxiliar_que_recibio="Auxiliar"):
        """Registra una devolución de equipos individuales"""
        return self.service.crear_devolucion(prestamo_id, docente_nfc, docente_nombre, equipos, auxiliar_que_recibio)
