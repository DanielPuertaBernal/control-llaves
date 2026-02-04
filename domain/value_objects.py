"""
Value Objects - Objetos de valor con validaciones de dominio
Encapsulan reglas de negocio fundamentales que no cambian
"""
import re
from typing import Tuple


class Email:
    """Value Object para Email con validación"""
    
    PATRON = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def __init__(self, email: str):
        self._value = email.strip().lower()
        self._validar()
    
    def _validar(self):
        """Valida el formato del email"""
        if not self._value:
            raise ValueError("El email no puede estar vacío")
        
        if not re.match(self.PATRON, self._value):
            raise ValueError(f"Email inválido: {self._value}. Formato esperado: ejemplo@dominio.com")
    
    @property
    def value(self) -> str:
        return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self._value == other._value
        return False


class Telefono:
    """Value Object para Teléfono con validación"""
    
    PATRON = r'^[\d\s\+\-\(\)]+$'
    
    def __init__(self, telefono: str):
        self._value = telefono.strip()
        self._validar()
    
    def _validar(self):
        """Valida el formato del teléfono"""
        if not self._value:
            raise ValueError("El teléfono no puede estar vacío")
        
        if len(self._value) < 7:
            raise ValueError("El teléfono debe tener al menos 7 caracteres")
        
        if not re.match(self.PATRON, self._value):
            raise ValueError(f"Teléfono inválido: {self._value}. Solo se permiten números, +, -, (, )")
    
    @property
    def value(self) -> str:
        return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Telefono):
            return self._value == other._value
        return False


class NombreUsuario:
    """Value Object para nombre de usuario con validación"""
    
    LONGITUD_MINIMA = 3
    LONGITUD_MAXIMA = 50
    PATRON = r'^[a-z0-9_]+$'  # Solo letras minúsculas, números y guiones bajos
    
    def __init__(self, usuario: str):
        self._value = usuario.strip().lower()
        self._validar()
    
    def _validar(self):
        """Valida el nombre de usuario"""
        if not self._value:
            raise ValueError("El nombre de usuario no puede estar vacío")
        
        if len(self._value) < self.LONGITUD_MINIMA:
            raise ValueError(f"El usuario debe tener al menos {self.LONGITUD_MINIMA} caracteres")
        
        if len(self._value) > self.LONGITUD_MAXIMA:
            raise ValueError(f"El usuario no puede tener más de {self.LONGITUD_MAXIMA} caracteres")
        
        if not re.match(self.PATRON, self._value):
            raise ValueError(
                f"Usuario inválido: '{self._value}'. "
                "Solo se permiten letras minúsculas, números y guiones bajos"
            )
    
    @property
    def value(self) -> str:
        return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, NombreUsuario):
            return self._value == other._value
        return False


class Password:
    """Value Object para contraseña con validación"""
    
    LONGITUD_MINIMA = 6
    
    @staticmethod
    def validar(password: str) -> Tuple[bool, str]:
        """
        Valida una contraseña
        
        Returns:
            Tuple[bool, str]: (es_valida, mensaje_error)
        """
        if not password:
            return False, "La contraseña no puede estar vacía"
        
        if len(password) < Password.LONGITUD_MINIMA:
            return False, f"La contraseña debe tener al menos {Password.LONGITUD_MINIMA} caracteres"
        
        return True, ""
    
    @staticmethod
    def validar_confirmacion(password: str, confirmacion: str) -> Tuple[bool, str]:
        """
        Valida que dos contraseñas coincidan
        
        Returns:
            Tuple[bool, str]: (coinciden, mensaje_error)
        """
        if password != confirmacion:
            return False, "Las contraseñas no coinciden"
        
        return True, ""
