"""
Usuario MongoDB Repository - Persistencia de usuarios
"""
from typing import List, Optional
from domain.usuario import Usuario, RolUsuario
from infrastructure.services.mongo_client import MongoClientProvider


class UsuarioMongoRepository:
    """Repository para gestionar usuarios en MongoDB"""
    
    def __init__(self):
        """Inicializa conexión a MongoDB"""
        self.db = MongoClientProvider.get_db()
        self.collection = self.db['usuarios']
        
        # Crear índices para unicidad
        self.collection.create_index([("usuario", 1)], unique=True)
        self.collection.create_index([("email", 1)], unique=True)
    
    def crear_usuario(self, usuario: Usuario) -> bool:
        """
        Crea un nuevo usuario
        
        Args:
            usuario (Usuario): Usuario a crear
            
        Returns:
            bool: True si se creó exitosamente
            
        Raises:
            Exception: Si el usuario ya existe
        """
        try:
            # Verificar que no exista
            if self.collection.find_one({"usuario": usuario.usuario}):
                raise ValueError(f"Usuario '{usuario.usuario}' ya existe")
            
            if self.collection.find_one({"email": usuario.email}):
                raise ValueError(f"Email '{usuario.email}' ya está registrado")
            
            # Insertar
            resultado = self.collection.insert_one(usuario.a_dict())
            return resultado.acknowledged
            
        except Exception as e:
            raise Exception(f"Error al crear usuario: {str(e)}")
    
    def buscar_por_usuario(self, usuario: str) -> Optional[Usuario]:
        """
        Busca un usuario por nombre de usuario
        
        Args:
            usuario (str): Nombre de usuario
            
        Returns:
            Usuario: Objeto Usuario o None si no existe
        """
        try:
            datos = self.collection.find_one({"usuario": usuario.lower()})
            return Usuario.desde_dict(datos) if datos else None
        except Exception as e:
            raise Exception(f"Error al buscar usuario: {str(e)}")
    
    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """
        Busca un usuario por email
        
        Args:
            email (str): Email del usuario
            
        Returns:
            Usuario: Objeto Usuario o None
        """
        try:
            datos = self.collection.find_one({"email": email.lower()})
            return Usuario.desde_dict(datos) if datos else None
        except Exception as e:
            raise Exception(f"Error al buscar por email: {str(e)}")
    
    def obtener_usuarios_por_rol(self, rol: RolUsuario) -> List[Usuario]:
        """
        Obtiene todos los usuarios de un rol específico
        
        Args:
            rol (RolUsuario): Rol a filtrar
            
        Returns:
            List[Usuario]: Lista de usuarios del rol
        """
        try:
            usuarios = []
            for datos in self.collection.find({"rol": rol.value, "activo": True}):
                usuarios.append(Usuario.desde_dict(datos))
            return usuarios
        except Exception as e:
            raise Exception(f"Error al obtener usuarios: {str(e)}")
    
    def obtener_todos_activos(self) -> List[Usuario]:
        """
        Obtiene todos los usuarios activos
        
        Returns:
            List[Usuario]: Lista de usuarios activos
        """
        try:
            usuarios = []
            for datos in self.collection.find({"activo": True}):
                usuarios.append(Usuario.desde_dict(datos))
            return usuarios
        except Exception as e:
            raise Exception(f"Error al obtener usuarios: {str(e)}")
    
    def actualizar_usuario(self, usuario: Usuario) -> bool:
        """
        Actualiza un usuario existente
        
        Args:
            usuario (Usuario): Usuario con datos actualizados
            
        Returns:
            bool: True si se actualizó
        """
        try:
            resultado = self.collection.update_one(
                {"usuario": usuario.usuario},
                {"$set": usuario.a_dict()}
            )
            return resultado.modified_count > 0
        except Exception as e:
            raise Exception(f"Error al actualizar usuario: {str(e)}")
    
    def desactivar_usuario(self, nombre_usuario: str) -> bool:
        """
        Desactiva un usuario (soft delete)
        
        Args:
            nombre_usuario (str): Nombre de usuario
            
        Returns:
            bool: True si se desactivó
        """
        try:
            resultado = self.collection.update_one(
                {"usuario": nombre_usuario},
                {"$set": {"activo": False}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            raise Exception(f"Error al desactivar usuario: {str(e)}")
    
    def eliminar_usuario(self, nombre_usuario: str) -> bool:
        """
        Elimina un usuario (hard delete - solo ADMIN)
        
        Args:
            nombre_usuario (str): Nombre de usuario
            
        Returns:
            bool: True si se eliminó
        """
        try:
            resultado = self.collection.delete_one({"usuario": nombre_usuario})
            return resultado.deleted_count > 0
        except Exception as e:
            raise Exception(f"Error al eliminar usuario: {str(e)}")
    
    def contar_usuarios(self, rol: Optional[RolUsuario] = None) -> int:
        """
        Cuenta los usuarios (opcionalmente por rol)
        
        Args:
            rol (RolUsuario): Rol opcional para filtrar
            
        Returns:
            int: Cantidad de usuarios
        """
        try:
            if rol:
                return self.collection.count_documents({"rol": rol.value, "activo": True})
            return self.collection.count_documents({"activo": True})
        except Exception as e:
            raise Exception(f"Error al contar usuarios: {str(e)}")
