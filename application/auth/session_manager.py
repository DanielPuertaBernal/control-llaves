"""
Session Manager - Gestión de sesión del usuario activo
"""
from domain.usuario import Usuario, RolUsuario


class SessionManager:
    """Gestor centralizado de sesiones (Singleton)"""
    
    _instancia = None
    _usuario_actual = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(SessionManager, cls).__new__(cls)
        return cls._instancia
    
    def iniciar_sesion(self, usuario: Usuario):
        """
        Inicia una sesión para un usuario
        
        Args:
            usuario (Usuario): Usuario autenticado
        """
        self._usuario_actual = usuario
    
    def obtener_usuario_actual(self) -> Usuario:
        """
        Obtiene el usuario autenticado actualmente
        
        Returns:
            Usuario: Usuario actual o None
        """
        return self._usuario_actual
    
    def usuario_autenticado(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self._usuario_actual is not None
    
    def usuario_tiene_rol(self, rol: RolUsuario) -> bool:
        """
        Verifica si el usuario actual tiene un rol
        
        Args:
            rol (RolUsuario): Rol a verificar
            
        Returns:
            bool: True si el usuario tiene ese rol
        """
        return self._usuario_actual and self._usuario_actual.rol == rol
    
    def actualizar_usuario_sesion(self, usuario: Usuario):
        """
        Actualiza el usuario en la sesión actual
        (necesario cuando el usuario cambia sus datos)
        
        Args:
            usuario (Usuario): Usuario actualizado
        """
        self._usuario_actual = usuario
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        self._usuario_actual = None
