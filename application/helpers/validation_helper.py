"""
Helper para validaciones comunes de modelos de dominio
Centraliza validaciones repetidas en servicios
"""
from typing import Optional
from bson import ObjectId


class ValidationHelper:
    """Utilidades para validaciones comunes en servicios"""
    
    @staticmethod
    def validar_equipo_existe(equipo, equipo_id: ObjectId) -> None:
        """
        Valida que un equipo exista
        
        Args:
            equipo: Objeto equipo del repositorio (puede ser None)
            equipo_id: ID del equipo para mensaje de error
            
        Raises:
            ValueError: Si el equipo no existe
        """
        if not equipo:
            raise ValueError(f"Equipo con ID {equipo_id} no existe")
    
    @staticmethod
    def validar_equipo_disponible(equipo) -> None:
        """
        Valida que un equipo esté disponible para préstamo
        
        Args:
            equipo: Objeto equipo con método está_disponible()
            
        Raises:
            ValueError: Si el equipo no está disponible
        """
        if not equipo.está_disponible():
            raise ValueError(f"Equipo no disponible: {equipo.nombre}")
    
    @staticmethod
    def validar_cantidad_individual(cantidad: int) -> None:
        """
        Valida que la cantidad sea 1 (modelo de equipos individuales)
        
        Args:
            cantidad: Cantidad a validar
            
        Raises:
            ValueError: Si la cantidad no es 1
        """
        if cantidad != 1:
            raise ValueError("El modelo actual usa equipos individuales (cantidad=1)")
    
    @staticmethod
    def validar_prestamo_existe(prestamo, prestamo_id: ObjectId) -> None:
        """
        Valida que un préstamo exista
        
        Args:
            prestamo: Objeto préstamo del repositorio (puede ser None)
            prestamo_id: ID del préstamo para mensaje de error
            
        Raises:
            ValueError: Si el préstamo no existe
        """
        if not prestamo:
            raise ValueError(f"Préstamo con ID {prestamo_id} no existe")
    
    @staticmethod
    def validar_prestamo_no_devuelto(prestamo) -> None:
        """
        Valida que un préstamo no esté completamente devuelto
        
        Args:
            prestamo: Objeto préstamo
            
        Raises:
            ValueError: Si el préstamo ya fue devuelto completamente
        """
        if prestamo.estado == "completamente_devuelto":
            raise ValueError("Este préstamo ya fue completamente devuelto")
    
    @staticmethod
    def validar_lista_no_vacia(lista: list, mensaje: str) -> None:
        """
        Valida que una lista no esté vacía
        
        Args:
            lista: Lista a validar
            mensaje: Mensaje de error si está vacía
            
        Raises:
            ValueError: Si la lista está vacía
        """
        if not lista:
            raise ValueError(mensaje)
    
    @staticmethod
    def normalizar_object_id(valor) -> Optional[ObjectId]:
        """
        Convierte un string o valor a ObjectId si es necesario
        
        Args:
            valor: String, ObjectId o None
            
        Returns:
            ObjectId o None si el valor es None
        """
        if valor is None:
            return None
        if isinstance(valor, str):
            return ObjectId(valor)
        return valor
