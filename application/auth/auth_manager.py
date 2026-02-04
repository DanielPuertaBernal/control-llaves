"""
Auth Manager - Manejo de autenticación y cifrado de contraseñas
"""
import bcrypt
from domain.usuario import Usuario, RolUsuario


class AuthManager:
    """Gestor centralizado de autenticación"""
    
    SALT_ROUNDS = 12  # Costo de bcrypt (más alto = más seguro pero más lento)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashea una contraseña con bcrypt
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash bcrypt de la contraseña
        """
        if not password or len(password) < 6:
            raise ValueError("Contraseña debe tener al menos 6 caracteres")
        
        # Generar salt y hashear
        salt = bcrypt.gensalt(rounds=AuthManager.SALT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hash_stored: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash
        
        Args:
            password (str): Contraseña en texto plano
            hash_stored (str): Hash almacenado en BD
            
        Returns:
            bool: True si coincide, False si no
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hash_stored.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def crear_usuario(usuario: str, nombre: str, email: str, contacto: str,
                     password: str, rol: RolUsuario = RolUsuario.AUX_PROG) -> Usuario:
        """
        Crea un nuevo usuario con contraseña hasheada
        
        Args:
            usuario (str): Nombre de usuario
            nombre (str): Nombre completo
            email (str): Email
            contacto (str): Teléfono
            password (str): Contraseña en texto plano
            rol (RolUsuario): Rol del usuario
            
        Returns:
            Usuario: Instancia de Usuario con contraseña hasheada
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        # Hashear contraseña
        hash_password = AuthManager.hash_password(password)
        
        # Crear usuario con contraseña hasheada
        nuevo_usuario = Usuario(
            usuario=usuario,
            nombre=nombre,
            email=email,
            contacto=contacto,
            rol=rol,
            hash_password=hash_password,
            activo=True
        )
        
        return nuevo_usuario
    
    @staticmethod
    def validar_credenciales(usuario_obj: Usuario, password: str) -> bool:
        """
        Valida que las credenciales sean correctas
        
        Args:
            usuario_obj (Usuario): Objeto Usuario de BD
            password (str): Contraseña a verificar
            
        Returns:
            bool: True si credenciales son correctas y usuario activo
        """
        if not usuario_obj.activo:
            return False
        
        return AuthManager.verify_password(password, usuario_obj.hash_password)
