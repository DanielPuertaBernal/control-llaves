"""
DEPRECATED: Controlador redundante - usar directamente LlaveService
Esta capa será removida en futuras versiones.
Por ahora mantiene compatibilidad con código existente.
"""
from application.services.llave_service import LlaveService


class LlaveController:
    """DEPRECATED: Delega directamente a LlaveService sin agregar valor"""
    
    def __init__(self, llave_service: LlaveService):
        self.service = llave_service
    
    def procesar_entrega(self, info_clase):
        return self.service.procesar_entrega(info_clase)
    
    def procesar_devolucion(self, nroidenti, nombre_docente=None):
        return self.service.procesar_devolucion(nroidenti, nombre_docente)
    
    def obtener_llaves_en_prestamo(self):
        return self.service.obtener_llaves_en_prestamo()
    
    def obtener_clases_procesadas_hoy(self):
        return self.service.obtener_clases_procesadas_hoy()
    
    def obtener_llaves_prestadas_dia(self):
        return self.service.obtener_llaves_prestadas_dia()
    
    def verificar_tiene_llave(self, nroidenti):
        return self.service.verificar_tiene_llave(nroidenti)
    
    def obtener_info_llave(self, nroidenti):
        return self.service.obtener_info_llave(nroidenti)

    def evaluar_retraso_entrega(self, horario):
        return self.service.evaluar_retraso_entrega(horario)
