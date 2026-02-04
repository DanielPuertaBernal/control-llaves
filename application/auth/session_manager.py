"""
Session Manager - Gestión de sesión del usuario activo
"""
from datetime import datetime, timedelta
from domain.usuario import Usuario, RolUsuario


class Session:
    """Sesión de usuario activo en la aplicación"""
    
    def __init__(self, usuario: Usuario, token: str = None, duracion_minutos: int = 480):
        """
        Crea una sesión para un usuario
        
        Args:
            usuario (Usuario): Usuario autenticado
            token (str): Token único de sesión (opcional)
            duracion_minutos (int): Duración de la sesión en minutos (default 8h)
        """
        self.usuario = usuario
        self.token = token or self._generar_token()
        self.inicio = datetime.now()
        self.expiracion = self.inicio + timedelta(minutes=duracion_minutos)
        self.activa = True
    
    @staticmethod
    def _generar_token() -> str:
        """Genera un token único para la sesión"""
        import uuid
        return str(uuid.uuid4())
    
    def es_valida(self) -> bool:
        """Verifica si la sesión sigue siendo válida"""
        if not self.activa:
            return False
        
        if datetime.now() > self.expiracion:
            self.activa = False
            return False
        
        return True
    
    def tiempo_restante(self) -> int:
        """Retorna minutos restantes de sesión"""
        if not self.es_valida():
            return 0
        
        diferencia = self.expiracion - datetime.now()
        return max(0, int(diferencia.total_seconds() / 60))
    
    def renovar(self, duracion_minutos: int = 480):
        """Renueva la sesión por otros N minutos"""
        if self.es_valida():
            self.expiracion = datetime.now() + timedelta(minutes=duracion_minutos)
    
    def cerrar(self):
        """Cierra la sesión"""
        self.activa = False
    
    def tiene_rol(self, rol: RolUsuario) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        return self.usuario.rol == rol
    
    def __repr__(self) -> str:
        estado = "activa" if self.es_valida() else "expirada"
        return f"Session({self.usuario.usuario}, {estado})"


class SessionManager:
    """Gestor centralizado de sesiones"""
    
    _instancia = None
    _sesion_actual = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(SessionManager, cls).__new__(cls)
        return cls._instancia
    
    def iniciar_sesion(self, usuario: Usuario) -> Session:
        """
        Inicia una sesión para un usuario
        
        Args:
            usuario (Usuario): Usuario a autenticar
            
        Returns:
            Session: Sesión activa
        """
        self._sesion_actual = Session(usuario)
        return self._sesion_actual
    
    def obtener_sesion(self) -> Session:
        """Obtiene la sesión actual"""
        if self._sesion_actual and self._sesion_actual.es_valida():
            return self._sesion_actual
        return None
    
    def obtener_usuario_actual(self) -> Usuario:
        """Obtiene el usuario de la sesión actual"""
        sesion = self.obtener_sesion()
        return sesion.usuario if sesion else None
    
    def usuario_autenticado(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.obtener_sesion() is not None
    
    def usuario_tiene_rol(self, rol: RolUsuario) -> bool:
        """Verifica si el usuario autenticado tiene un rol"""
        sesion = self.obtener_sesion()
        return sesion.tiene_rol(rol) if sesion else False
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        if self._sesion_actual:
            self._sesion_actual.cerrar()
            self._sesion_actual = None
    
    def renovar_sesion(self, duracion_minutos: int = 480):
        """Renueva la sesión actual"""
        if self._sesion_actual:
            self._sesion_actual.renovar(duracion_minutos)
