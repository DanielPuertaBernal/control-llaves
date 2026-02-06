"""
Controlador de Préstamos - Orquesta entre vistas y servicios
"""
from application.services.prestamo_service import PréstamoService
from bson import ObjectId


class PréstamoController:
    """Controlador para gestión de préstamos"""
    
    def __init__(self, prestamo_service: PréstamoService = None):
        self.service = prestamo_service or PréstamoService()
    
    def crear_prestamo(self, docente_nfc, docente_nombre, equipos, auxiliar="Auxiliar", dias_plazo=None, notas=None):
        """Crea un nuevo préstamo (acepta tuplas o diccionarios)"""
        return self.service.crear_prestamo(docente_nfc, docente_nombre, equipos, auxiliar, dias_plazo, notas)
    
    def obtener_activos(self):
        """Obtiene préstamos activos"""
        return self.service.obtener_prestamos_activos()
    
    def obtener_historial_docente(self, codigo_nfc):
        """Obtiene historial de un docente"""
        return self.service.obtener_historial_docente(codigo_nfc)
    
    def obtener_activos_docente(self, codigo_nfc):
        """Obtiene préstamos activos de un docente"""
        return self.service.obtener_prestamos_activos_docente(codigo_nfc)
    
    def obtener_prestamo(self, prestamo_id):
        """Obtiene un préstamo"""
        return self.service.obtener_prestamo(prestamo_id)
    
    def obtener_todos(self):
        """Obtiene todos los préstamos"""
        return self.service.obtener_todos_prestamos()
    
    def agregar_equipo(self, prestamo_id, equipo_id, cantidad):
        """Agrega equipo a un préstamo"""
        return self.service.agregar_equipo_prestamo(prestamo_id, equipo_id, cantidad)
    
    def marcar_vencido(self, prestamo_id):
        """Marca préstamo como vencido"""
        return self.service.marcar_vencido(prestamo_id)
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas"""
        return self.service.obtener_estadisticas()
