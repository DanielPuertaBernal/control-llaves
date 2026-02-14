"""
Auth Service - Lógica de autenticación y gestión de usuarios
"""
from typing import Tuple, List
from domain.usuario import Usuario, RolUsuario
from application.auth.auth_manager import AuthManager
from application.auth.session_manager import SessionManager
from infrastructure.repositories.usuario_mongo_repository import UsuarioMongoRepository


class AuthService:
    """Servicio de autenticación"""
    
    def __init__(self, usuario_repository: UsuarioMongoRepository = None):
        """
        Inicializa el servicio
        
        Args:
            usuario_repository (UsuarioMongoRepository): Repository de usuarios
        """
        self.repository = usuario_repository or UsuarioMongoRepository()
        self.session_manager = SessionManager()
    
    def login(self, usuario: str, password: str) -> Tuple[bool, str, Usuario]:
        """
        Autentica un usuario
        
        Args:
            usuario (str): Nombre de usuario
            password (str): Contraseña en texto plano
            
        Returns:
            Tuple[bool, str, Usuario]: (éxito, mensaje, usuario_obj)
        """
        try:
            # Buscar usuario
            usuario_obj = self.repository.buscar_por_usuario(usuario)
            
            if not usuario_obj:
                return False, f"❌ Usuario '{usuario}' no encontrado", None
            
            if not usuario_obj.activo:
                return False, "❌ Usuario inactivo", None
            
            # Verificar contraseña
            if not AuthManager.validar_credenciales(usuario_obj, password):
                return False, "❌ Contraseña incorrecta", None
            
            # Iniciar sesión
            self.session_manager.iniciar_sesion(usuario_obj)
            
            return True, f"✅ Bienvenido {usuario_obj.nombre}", usuario_obj
            
        except Exception as e:
            return False, f"❌ Error en login: {str(e)}", None
    
    def logout(self) -> Tuple[bool, str]:
        """
        Cierra la sesión del usuario actual
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            usuario = self.session_manager.obtener_usuario_actual()
            self.session_manager.cerrar_sesion()
            
            mensaje = f"✅ Sesión cerrada. Hasta pronto {usuario.nombre}" if usuario else "✅ Sesión cerrada"
            return True, mensaje
        except Exception as e:
            return False, f"❌ Error al cerrar sesión: {str(e)}"
    
    def crear_usuario(self, usuario: str, nombre: str, email: str, contacto: str,
                     password: str, rol: RolUsuario) -> Tuple[bool, str]:
        """
        Crea un nuevo usuario (solo ADMIN_PROG)
        
        Args:
            usuario (str): Nombre de usuario
            nombre (str): Nombre completo
            email (str): Email
            contacto (str): Teléfono
            password (str): Contraseña
            rol (RolUsuario): Rol del usuario
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Crear usuario con contraseña hasheada
            nuevo_usuario = AuthManager.crear_usuario(
                usuario=usuario,
                nombre=nombre,
                email=email,
                contacto=contacto,
                password=password,
                rol=rol
            )
            
            # Persistir
            self.repository.crear_usuario(nuevo_usuario)
            
            return True, f"✅ Usuario '{usuario}' creado exitosamente"
            
        except ValueError as e:
            return False, f"❌ Validación: {str(e)}"
        except Exception as e:
            return False, f"❌ Error al crear usuario: {str(e)}"
    
    def obtener_usuario_actual(self) -> Usuario:
        """
        Obtiene el usuario autenticado actualmente
        
        Returns:
            Usuario: Usuario actual o None
        """
        return self.session_manager.obtener_usuario_actual()
    
    def usuario_autenticado(self) -> bool:
        """Verifica si hay usuario autenticado"""
        return self.session_manager.usuario_autenticado()
    
    def usuario_tiene_rol(self, rol: RolUsuario) -> bool:
        """Verifica si el usuario actual tiene un rol"""
        return self.session_manager.usuario_tiene_rol(rol)
    
    def obtener_auxiliares(self, incluir_inactivos: bool = True) -> List[Usuario]:
        """
        Obtiene todos los auxiliares de programación
        
        Args:
            incluir_inactivos (bool): Si True, incluye usuarios inactivos
        """
        return self.repository.obtener_usuarios_por_rol(RolUsuario.AUX_PROG, incluir_inactivos)
    
    def obtener_admins(self) -> List[Usuario]:
        """Obtiene todos los administradores de programación"""
        return self.repository.obtener_usuarios_por_rol(RolUsuario.ADMIN_PROG)
    
    def desactivar_usuario(self, nombre_usuario: str) -> Tuple[bool, str]:
        """
        Desactiva un usuario
        
        Args:
            nombre_usuario (str): Nombre de usuario
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            exito = self.repository.desactivar_usuario(nombre_usuario)
            
            if exito:
                return True, f"✅ Usuario '{nombre_usuario}' desactivado"
            return False, "❌ Usuario no encontrado"
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def reactivar_usuario(self, nombre_usuario: str) -> Tuple[bool, str]:
        """
        Reactiva un usuario inactivo
        
        Args:
            nombre_usuario (str): Nombre de usuario
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            usuario_obj = self.repository.buscar_por_usuario(nombre_usuario)
            
            if not usuario_obj:
                return False, "❌ Usuario no encontrado"
            
            if usuario_obj.activo:
                return False, f"⚠️ Usuario '{nombre_usuario}' ya está activo"
            
            # Reactivar
            usuario_obj.activo = True
            self.repository.actualizar_usuario(usuario_obj)
            
            return True, f"✅ Usuario '{nombre_usuario}' reactivado exitosamente"
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    def actualizar_usuario_info(self, usuario_obj: Usuario, usuario_nuevo: str, nombre_nuevo: str, 
                                email_nuevo: str, contacto_nuevo: str) -> bool:
        """
        Actualiza la información personal del usuario
        
        Args:
            usuario_obj (Usuario): Usuario a actualizar
            usuario_nuevo (str): Nuevo nombre de usuario
            nombre_nuevo (str): Nuevo nombre completo
            email_nuevo (str): Nuevo email
            contacto_nuevo (str): Nuevo contacto
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            from domain.value_objects import NombreUsuario, Email, Telefono
            
            # Validar con Value Objects (normalizan automáticamente)
            nombre_usuario_vo = NombreUsuario(usuario_nuevo)
            email_vo = Email(email_nuevo)
            telefono_vo = Telefono(contacto_nuevo)
            
            # Valores ya normalizados por Value Objects
            usuario_nuevo = nombre_usuario_vo.value
            email_nuevo = email_vo.value
            contacto_nuevo = telefono_vo.value
            nombre_nuevo = nombre_nuevo.strip()
            
            # Guardar usuario anterior para el query a BD
            usuario_anterior = usuario_obj.usuario
            
            # Si el usuario cambió, validar que sea único
            if usuario_nuevo != usuario_anterior:
                existente = self.repository.buscar_por_usuario(usuario_nuevo)
                if existente:
                    raise ValueError(f"El usuario '{usuario_nuevo}' ya existe")
            
            # Actualizar el objeto con los nuevos datos
            usuario_obj.usuario = usuario_nuevo
            usuario_obj.nombre = nombre_nuevo
            usuario_obj.email = email_nuevo
            usuario_obj.contacto = contacto_nuevo
            
            # Actualizar en BD usando el usuario anterior como filtro
            self.repository.actualizar_usuario_por_antiguo(usuario_anterior, usuario_obj)
            
            # Actualizar el usuario en la sesión activa
            self.session_manager.actualizar_usuario_sesion(usuario_obj)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error actualizando usuario: {str(e)}")

    def cambiar_contraseña(self, usuario_obj: Usuario, pwd_actual: str, pwd_nueva: str) -> bool:
        """
        Cambia la contraseña del usuario
        
        Args:
            usuario_obj (Usuario): Usuario cuya contraseña cambiar
            pwd_actual (str): Contraseña actual en texto plano
            pwd_nueva (str): Nueva contraseña en texto plano
            
        Returns:
            bool: True si se cambió exitosamente
        """
        try:
            # Validar contraseña actual
            if not AuthManager.validar_credenciales(usuario_obj, pwd_actual):
                return False
            
            # Crear nuevo hash
            nuevo_hash = AuthManager.hash_password(pwd_nueva)
            usuario_obj.hash_password = nuevo_hash
            
            self.repository.actualizar_usuario(usuario_obj)
            return True
            
        except Exception as e:
            raise Exception(f"Error cambiando contraseña: {str(e)}")
