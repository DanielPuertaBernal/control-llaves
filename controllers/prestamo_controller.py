"""
DEPRECATED: Controlador redundante - usar directamente PréstamoService
Esta capa será removida en futuras versiones.
Por ahora mantiene compatibilidad con código existente.
"""
from application.services.prestamo_service import PréstamoService


class PréstamoController:
    """DEPRECATED: Delega directamente a PréstamoService sin agregar valor"""
    
    def __init__(self, prestamo_service: PréstamoService = None):
        self.service = prestamo_service or PréstamoService()
    
    def crear_prestamo(self, docente_nfc, docente_nombre, equipos, auxiliar_prestamista="Auxiliar"):
        return self.service.crear_prestamo(docente_nfc, docente_nombre, equipos, auxiliar_prestamista)
    
    def obtener_activos(self):
        return self.service.obtener_prestamos_activos()
    
    def obtener_historial_docente(self, codigo_nfc):
        return self.service.obtener_historial_docente(codigo_nfc)
    
    def obtener_activos_docente(self, codigo_nfc):
        return self.service.obtener_prestamos_activos_docente(codigo_nfc)
    
    def obtener_prestamo(self, prestamo_id):
        return self.service.obtener_prestamo(prestamo_id)
    
    def obtener_todos(self):
        return self.service.obtener_todos_prestamos()
    
    def agregar_equipo(self, prestamo_id, equipo_id, cantidad):
        return self.service.agregar_equipo_prestamo(prestamo_id, equipo_id, cantidad)
    
    def marcar_vencido(self, prestamo_id):
        return self.service.marcar_vencido(prestamo_id)
    
    def verificar_equipo_prestado(self, equipo_id):
        return self.service.verificar_equipo_prestado(equipo_id)
