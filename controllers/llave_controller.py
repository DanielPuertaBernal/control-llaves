"""
Controlador para la gestión de llaves
Maneja la lógica de negocio de entregas y devoluciones
"""
from application.services.llave_service import LlaveService


class LlaveController:
    """Controlador para gestionar préstamos de llaves"""
    
    def __init__(self, llave_service: LlaveService):
        self.service = llave_service
    
    def procesar_entrega(self, info_clase):
        """
        Procesa la entrega de una llave a un docente
        
        Args:
            info_clase (dict): Información de la clase con llaves requeridas
        
        Returns:
            tuple: (exito, mensaje)
        """
        return self.service.procesar_entrega(info_clase)
    
    def procesar_devolucion(self, nroidenti, nombre_docente=None):
        """
        Procesa la devolución de una llave
        
        Args:
            nroidenti: Número de documento del docente
            nombre_docente (str): Nombre del docente (opcional, para mensaje)
        
        Returns:
            tuple: (exito, mensaje)
        """
        return self.service.procesar_devolucion(nroidenti, nombre_docente)
    
    def obtener_llaves_en_prestamo(self):
        """
        Obtiene todas las llaves actualmente en préstamo
        
        Returns:
            list: Lista de diccionarios con información de préstamos activos
        """
        return self.service.obtener_llaves_en_prestamo()
    
    def obtener_clases_procesadas_hoy(self):
        """
        Obtiene todas las clases que tuvieron entrega de llaves hoy
        (tanto en préstamo como devueltas), para evitar mostrarlas nuevamente
        
        Returns:
            list: Lista de diccionarios con información de clases procesadas hoy
        """
        return self.service.obtener_clases_procesadas_hoy()
    
    def obtener_llaves_prestadas_dia(self):
        """
        Obtiene las llaves prestadas exclusivamente del día actual
        
        Returns:
            list: Lista de diccionarios con información de préstamos del día
        """
        return self.service.obtener_llaves_prestadas_dia()
    
    def verificar_tiene_llave(self, nroidenti):
        """
        Verifica si un docente tiene una llave prestada
        
        Args:
            nroidenti: Número de documento
        
        Returns:
            bool: True si tiene llave prestada
        """
        return self.service.verificar_tiene_llave(nroidenti)
    
    def obtener_info_llave(self, nroidenti):
        """
        Obtiene información de una llave específica en préstamo
        
        Args:
            nroidenti: Número de documento
        
        Returns:
            dict: Información de la llave o None si no existe
        """
        return self.service.obtener_info_llave(nroidenti)

    def evaluar_retraso_entrega(self, horario):
        """Evalúa si hay retraso en entrega para un horario"""
        return self.service.evaluar_retraso_entrega(horario)

