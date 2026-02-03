"""
Decoradores de Control de Acceso basado en Roles (RBAC)
"""
from functools import wraps
from domain.usuario import RolUsuario
from application.auth.session_manager import SessionManager


def require_role(*roles_permitidos: RolUsuario):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos
    
    Args:
        *roles_permitidos: Roles que pueden ejecutar la función
        
    Raises:
        PermissionError: Si el usuario no tiene permisos
        
    Example:
        @require_role(RolUsuario.ADMIN_PROG)
        def crear_auxiliar(nombre, email):
            pass
    """
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session_manager = SessionManager()
            usuario = session_manager.obtener_usuario_actual()
            
            if not usuario:
                raise PermissionError("❌ No hay usuario autenticado")
            
            if usuario.rol not in roles_permitidos:
                raise PermissionError(
                    f"❌ Acceso denegado. Rol requerido: {', '.join(r.value for r in roles_permitidos)}"
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorador


def require_auth(func):
    """
    Decorador que verifica que haya una sesión activa
    
    Args:
        func: Función a proteger
        
    Raises:
        PermissionError: Si no hay sesión activa
        
    Example:
        @require_auth
        def obtener_llaves():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_manager = SessionManager()
        
        if not session_manager.usuario_autenticado():
            raise PermissionError("❌ Debe autenticarse primero")
        
        return func(*args, **kwargs)
    
    return wrapper


def require_activo(func):
    """
    Decorador que verifica que el usuario esté activo
    
    Args:
        func: Función a proteger
        
    Raises:
        PermissionError: Si el usuario no está activo
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_manager = SessionManager()
        usuario = session_manager.obtener_usuario_actual()
        
        if not usuario or not usuario.activo:
            raise PermissionError("❌ Usuario inactivo o no autenticado")
        
        return func(*args, **kwargs)
    
    return wrapper


def log_accion(accion: str):
    """
    Decorador que registra las acciones críticas
    
    Args:
        accion (str): Descripción de la acción
        
    Example:
        @log_accion("Crear usuario")
        def crear_usuario_nuevo(...):
            pass
    """
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session_manager = SessionManager()
            usuario = session_manager.obtener_usuario_actual()
            usuario_str = usuario.usuario if usuario else "desconocido"
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"[{timestamp}] ℹ️  {usuario_str} | {accion}")
            
            try:
                resultado = func(*args, **kwargs)
                print(f"[{timestamp}] ✅ {accion} exitosa")
                return resultado
            except Exception as e:
                print(f"[{timestamp}] ❌ {accion} falló: {str(e)}")
                raise
        
        return wrapper
    return decorador
