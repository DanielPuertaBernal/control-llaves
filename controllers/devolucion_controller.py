"""
Controlador de Devoluciones - Orquesta entre vistas y servicios
"""
from application.services.devolucion_service import DevolucionService
from bson import ObjectId


class DevolucionController:
    """Controlador para gestión de devoluciones"""
    
    def __init__(self, devolucion_service: DevolucionService = None):
        self.service = devolucion_service or DevolucionService()
    
    def registrar_devolucion(self, prestamo_id, auxiliar, equipos_devueltos, notas=None):
        """Registra una devolución"""
        return self.service.registrar_devolucion(prestamo_id, auxiliar, equipos_devueltos, notas)

    def crear_devolucion(self, prestamo_id, docente_nfc, docente_nombre, equipos, auxiliar_que_recibio="Auxiliar"):
        """Registra una devolución completa de equipos individuales"""
        return self.service.crear_devolucion(prestamo_id, docente_nfc, docente_nombre, equipos, auxiliar_que_recibio)
    
    def obtener_devoluciones_prestamo(self, prestamo_id):
        """Obtiene devoluciones de un préstamo"""
        return self.service.obtener_devoluciones_prestamo(prestamo_id)
    
    def obtener_historial_docente(self, codigo_nfc):
        """Obtiene historial de devoluciones de un docente"""
        return self.service.obtener_historial_docente(codigo_nfc)
    
    def obtener_todas(self):
        """Obtiene todas las devoluciones"""
        return self.service.obtener_todas_devoluciones()
    
    def obtener_devolucion(self, devolucion_id):
        """Obtiene una devolución"""
        return self.service.obtener_devolucion(devolucion_id)
