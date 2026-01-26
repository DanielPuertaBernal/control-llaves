""">
Controlador para la gestión de llaves
Maneja la lógica de negocio de entregas y devoluciones
"""
from models import LlaveModel
from datetime import datetime, date


class LlaveController:
    """Controlador para gestionar préstamos de llaves"""
    
    def __init__(self):
        self.model = LlaveModel()
    
    def procesar_entrega(self, info_clase):
        """
        Procesa la entrega de una llave a un docente
        
        Args:
            info_clase (dict): Información de la clase con llaves requeridas
        
        Returns:
            tuple: (exito, mensaje)
        """
        # Validar información
        if not self._validar_info_clase(info_clase):
            return False, "Información de clase incompleta"
        
        # Intentar registrar entrega
        exito = self.model.registrar_entrega(info_clase)
        
        if exito:
            return True, f"✅ Llave entregada a {info_clase.get('profesor')}"
        else:
            return False, "❌ El docente ya tiene una llave prestada"
    
    def procesar_devolucion(self, nroidenti, nombre_docente=None):
        """
        Procesa la devolución de una llave
        
        Args:
            nroidenti: Número de documento del docente
            nombre_docente (str): Nombre del docente (opcional, para mensaje)
        
        Returns:
            tuple: (exito, mensaje)
        """
        exito = self.model.registrar_devolucion(nroidenti)
        
        if exito:
            docente = nombre_docente if nombre_docente else "el docente"
            return True, f"✅ Llave devuelta por {docente}"
        else:
            return False, "❌ No se encontró llave en préstamo para este docente"
    
    def obtener_llaves_en_prestamo(self):
        """
        Obtiene todas las llaves actualmente en préstamo
        
        Returns:
            list: Lista de diccionarios con información de préstamos activos
        """
        return self.model.obtener_llaves_pendientes()
    
    def obtener_clases_procesadas_hoy(self):
        """
        Obtiene todas las clases que tuvieron entrega de llaves hoy
        (tanto en préstamo como devueltas), para evitar mostrarlas nuevamente
        
        Returns:
            list: Lista de diccionarios con información de clases procesadas hoy
        """
        fecha_actual = date.today()
        return self.model.obtener_clases_procesadas_hoy(fecha_actual)
    
    def obtener_llaves_prestadas_dia(self):
        """
        Obtiene las llaves prestadas exclusivamente del día actual
        
        Returns:
            list: Lista de diccionarios con información de préstamos del día
        """
        fecha_actual = date.today()
        return self.model.obtener_llaves_prestadas_dia(fecha_actual)
    
    def verificar_tiene_llave(self, nroidenti):
        """
        Verifica si un docente tiene una llave prestada
        
        Args:
            nroidenti: Número de documento
        
        Returns:
            bool: True si tiene llave prestada
        """
        llaves = self.model.obtener_llaves_pendientes()
        nroidenti_limpio = str(nroidenti).replace('.0', '')
        
        for llave in llaves:
            if llave['documento'] == nroidenti_limpio:
                return True
        return False
    
    def obtener_info_llave(self, nroidenti):
        """
        Obtiene información de una llave específica en préstamo
        
        Args:
            nroidenti: Número de documento
        
        Returns:
            dict: Información de la llave o None si no existe
        """
        llaves = self.model.obtener_llaves_pendientes()
        nroidenti_limpio = str(nroidenti).replace('.0', '')
        
        for llave in llaves:
            if llave['documento'] == nroidenti_limpio:
                return llave
        return None
    
    def _validar_info_clase(self, info_clase):
        """Valida que la información de clase tenga los campos requeridos"""
        campos_requeridos = ['nroidenti', 'profesor', 'aula']
        return all(campo in info_clase for campo in campos_requeridos)

