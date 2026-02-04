"""
Controlador de Equipos - Orquesta entre vistas y servicios
"""
from application.services.equipo_service import EquipoService
from bson import ObjectId


class EquipoController:
    """Controlador para gestión de equipos"""
    
    def __init__(self, equipo_service: EquipoService = None):
        self.service = equipo_service or EquipoService()
    
    def registrar_equipo(self, nombre, marca, codigo, cantidad, descripcion=None, ubicacion=None):
        """Registra un nuevo equipo"""
        return self.service.registrar_equipo(nombre, marca, codigo, cantidad, descripcion, ubicacion)
    
    def obtener_inventario(self):
        """Obtiene todo el inventario"""
        return self.service.obtener_todo_inventario()
    
    def obtener_disponibles(self):
        """Obtiene equipos disponibles"""
        return self.service.obtener_equipos_disponibles()
    
    def obtener_equipo(self, equipo_id):
        """Obtiene un equipo específico"""
        return self.service.obtener_equipo(equipo_id)
    
    def actualizar_equipo(self, equipo_id, nombre=None, marca=None, descripcion=None, ubicacion=None):
        """Actualiza un equipo"""
        return self.service.actualizar_equipo(equipo_id, nombre, marca, descripcion, ubicacion)
    
    def reponer_equipo(self, equipo_id, cantidad):
        """Repone un equipo"""
        return self.service.reponer_equipo(equipo_id, cantidad)
    
    def marcar_dañado(self, equipo_id, cantidad=1):
        """Marca equipo como dañado"""
        return self.service.marcar_equipo_dañado(equipo_id, cantidad)
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas"""
        return self.service.obtener_estadisticas()
