"""
Entidad Usuario - Domain Model
Define los roles y estructura de un usuario del sistema
"""
from enum import Enum
from datetime import datetime


class RolUsuario(Enum):
    """Roles disponibles en el sistema"""
    ADMIN_PROG = "admin_programacion"      # Administrador de Programación
    AUX_PROG = "auxiliar_programacion"     # Auxiliar de Programación


class Usuario:
    """Entidad Usuario con validaciones de dominio"""
    
    def __init__(self, usuario: str, nombre: str, email: str, contacto: str, 
                 rol: RolUsuario, hash_password: str, activo: bool = True, 
                 fecha_creacion: str = None):
        """
        Inicializa un usuario
        
        Args:
            usuario (str): Nombre de usuario único
            nombre (str): Nombre completo
            email (str): Email del usuario
            contacto (str): Teléfono o contacto
            rol (RolUsuario): Rol del usuario
            hash_password (str): Contraseña hasheada con bcrypt
            activo (bool): Si el usuario está activo
            fecha_creacion (str): ISO format datetime
        """
        self.usuario = usuario.strip().lower()
        self.nombre = nombre.strip()
        self.email = email.strip().lower()
        self.contacto = contacto.strip()
        self.rol = rol
        self.hash_password = hash_password
        self.activo = activo
        self.fecha_creacion = fecha_creacion or datetime.now().isoformat()
        
        # Validar
        self._validar()
    
    def _validar(self):
        """Valida los datos del usuario"""
        if not self.usuario or len(self.usuario) < 3:
            raise ValueError("Usuario debe tener al menos 3 caracteres")
        
        if not self.nombre or len(self.nombre) < 2:
            raise ValueError("Nombre debe tener al menos 2 caracteres")
        
        if not self._es_email_valido(self.email):
            raise ValueError("Email inválido")
        
        if not self.contacto:
            raise ValueError("Contacto requerido")
        
        if not isinstance(self.rol, RolUsuario):
            raise ValueError("Rol debe ser RolUsuario")
    
    @staticmethod
    def _es_email_valido(email: str) -> bool:
        """Validación básica de email"""
        return '@' in email and '.' in email.split('@')[1]
    
    def es_admin(self) -> bool:
        """Verifica si es administrador de programación"""
        return self.rol == RolUsuario.ADMIN_PROG
    
    def es_auxiliar(self) -> bool:
        """Verifica si es auxiliar de programación"""
        return self.rol == RolUsuario.AUX_PROG
    
    def puede_gestionar_programacion(self) -> bool:
        """Verifica si puede gestionar programación"""
        return self.es_admin()
    
    def puede_usar_nfc(self) -> bool:
        """Verifica si puede usar NFC (entregar/devolver llaves)"""
        return self.activo and (self.es_admin() or self.es_auxiliar())
    
    def a_dict(self) -> dict:
        """Convierte a diccionario para persistencia"""
        return {
            'usuario': self.usuario,
            'nombre': self.nombre,
            'email': self.email,
            'contacto': self.contacto,
            'rol': self.rol.value,
            'hash_password': self.hash_password,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion
        }
    
    @classmethod
    def desde_dict(cls, data: dict) -> 'Usuario':
        """Crea un Usuario desde diccionario"""
        rol = RolUsuario(data.get('rol', RolUsuario.AUX_PROG.value))
        return cls(
            usuario=data.get('usuario'),
            nombre=data.get('nombre'),
            email=data.get('email'),
            contacto=data.get('contacto'),
            rol=rol,
            hash_password=data.get('hash_password'),
            activo=data.get('activo', True),
            fecha_creacion=data.get('fecha_creacion')
        )
    
    def __repr__(self) -> str:
        return f"Usuario({self.usuario}, {self.nombre}, rol={self.rol.value})"
