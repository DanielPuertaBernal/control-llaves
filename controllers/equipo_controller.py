"""
Controlador de Equipos - Orquesta entre vistas y servicios
"""
from application.services.equipo_service import EquipoService


class EquipoController:
    """Controlador para gestión de equipos"""
    
    def __init__(self, equipo_service: EquipoService = None):
        self.service = equipo_service or EquipoService()
    
    def registrar_equipo(self, nombre, marca, consecutivo, codigo_inventario, descripcion=None):
        """Registra una nueva instancia de equipo"""
        return self.service.registrar_equipo(nombre, marca, consecutivo, codigo_inventario, descripcion)
    
    def obtener_inventario(self):
        """Obtiene todo el inventario"""
        return self.service.obtener_todo_inventario()
    
    def obtener_disponibles(self):
        """Obtiene equipos disponibles"""
        return self.service.obtener_equipos_disponibles()
    
    def obtener_equipo(self, equipo_id):
        """Obtiene un equipo específico"""
        return self.service.obtener_equipo(equipo_id)
    
    def obtener_por_consecutivo(self, consecutivo):
        """Obtiene un equipo por su consecutivo"""
        return self.service.obtener_por_numero_serie(consecutivo)
    
    def obtener_por_codigo_barras(self, codigo_barras):
        """Obtiene un equipo por código de barras"""
        return self.service.obtener_por_codigo_barras(codigo_barras)
    
    def actualizar_equipo(self, equipo_id, nombre=None, marca=None, consecutivo=None, descripcion=None, estado=None):
        """Actualiza un equipo"""
        return self.service.actualizar_equipo(equipo_id, nombre, marca, consecutivo, descripcion, estado)
    
