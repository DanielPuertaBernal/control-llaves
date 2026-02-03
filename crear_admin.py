#!/usr/bin/env python3
"""
Script para crear el primer usuario administrador
Uso: python crear_admin.py
"""
from domain.usuario import RolUsuario
from application.auth.auth_manager import AuthManager
from infrastructure.repositories.usuario_mongo_repository import UsuarioMongoRepository


def crear_administrador():
    """Crea el primer usuario administrador del sistema"""
    print("=" * 60)
    print("CREACIÓN DE USUARIO ADMINISTRADOR")
    print("=" * 60)
    
    repo = UsuarioMongoRepository()
    
    # Verificar si ya existe algún admin
    admins = repo.obtener_usuarios_por_rol(RolUsuario.ADMIN_PROG)
    if admins:
        print("\n⚠️  Ya existe al menos un administrador en el sistema:")
        for admin in admins:
            estado = "🟢 Activo" if admin.activo else "🔴 Inactivo"
            print(f"   • {admin.usuario} - {admin.nombre} [{estado}]")
        
        continuar = input("\n¿Desea crear otro administrador? (s/n): ").lower()
        if continuar != 's':
            print("Operación cancelada")
            return
    
    print("\nIngrese los datos del administrador:\n")
    
    # Solicitar datos
    usuario = input("Usuario (único): ").strip().lower()
    nombre = input("Nombre completo: ").strip()
    email = input("Email: ").strip().lower()
    contacto = input("Teléfono/Contacto: ").strip()
    
    # Contraseña con confirmación
    while True:
        password = input("Contraseña (mín. 6 caracteres): ")
        if len(password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres")
            continue
        
        confirmar = input("Confirmar contraseña: ")
        if password != confirmar:
            print("❌ Las contraseñas no coinciden. Intente nuevamente.")
            continue
        
        break
    
    # Crear usuario
    try:
        nuevo_admin = AuthManager.crear_usuario(
            usuario=usuario,
            nombre=nombre,
            email=email,
            contacto=contacto,
            password=password,
            rol=RolUsuario.ADMIN_PROG
        )
        
        repo.crear_usuario(nuevo_admin)
        
        print("\n" + "=" * 60)
        print("✅ ADMINISTRADOR CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"Usuario: {usuario}")
        print(f"Nombre: {nombre}")
        print(f"Email: {email}")
        print(f"Rol: Administrador de Programación")
        print("\n⚠️  IMPORTANTE: Guarde estas credenciales en un lugar seguro")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
    except Exception as e:
        print(f"\n❌ Error al crear administrador: {e}")


if __name__ == "__main__":
    try:
        crear_administrador()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
