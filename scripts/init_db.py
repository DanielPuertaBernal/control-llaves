"""
Script de Inicialización de Base de Datos
Crea el usuario administrador inicial con datos ingresados por el usuario
"""
import sys
import re
from pathlib import Path

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.repositories.usuario_mongo_repository import UsuarioMongoRepository
from domain.usuario import Usuario, RolUsuario
import bcrypt


def validar_email(email: str) -> bool:
    """Valida formato de email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def validar_usuario(usuario: str) -> bool:
    """Valida formato de usuario (solo letras, números, guiones)"""
    patron = r'^[a-zA-Z0-9_-]{3,20}$'
    return re.match(patron, usuario) is not None


def validar_contraseña(contraseña: str) -> bool:
    """Valida contraseña (mínimo 8 caracteres)"""
    return len(contraseña) >= 8


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("🔐 INICIALIZACIÓN DE BASE DE DATOS - CREACIÓN DE ADMIN INICIAL")
    print("=" * 70)
    
    try:
        # Conectar a repositorio
        repo = UsuarioMongoRepository()
        
        # Verificar si ya existe un admin
        admins_existentes = repo.obtener_usuarios_por_rol(RolUsuario.ADMIN_PROG)
        if admins_existentes:
            print("\n⚠️  YA EXISTE UN ADMINISTRADOR EN LA BASE DE DATOS")
            print(f"Usuario: {admins_existentes[0].usuario}")
            print("\nNo se creará otro admin. Si quieres crear uno nuevo,")
            print("elimina el actual manualmente desde MongoDB Atlas.")
            return
        
        print("\n📋 Por favor ingresa los datos del administrador inicial:\n")
        
        # Solicitar usuario
        while True:
            usuario = input("👤 Usuario (3-20 caracteres, letras/números/guiones): ").strip()
            if not validar_usuario(usuario):
                print("   ❌ Usuario inválido. Usa 3-20 caracteres (letras, números, guiones)")
                continue
            
            # Verificar que no exista
            if repo.buscar_por_usuario(usuario):
                print(f"   ❌ El usuario '{usuario}' ya existe en la base de datos")
                continue
            
            break
        
        # Solicitar email
        while True:
            email = input("📧 Email: ").strip()
            if not validar_email(email):
                print("   ❌ Email inválido. Intenta de nuevo")
                continue
            break
        
        # Solicitar nombre
        nombre = input("👨‍💼 Nombre completo (opcional, presiona Enter para omitir): ").strip()
        if not nombre:
            nombre = usuario.capitalize()
        
        # Solicitar teléfono/contacto
        while True:
            contacto = input("📞 Teléfono o contacto: ").strip()
            if not contacto:
                print("   ❌ El contacto es obligatorio")
                continue
            break
        
        # Solicitar contraseña
        while True:
            contraseña = input("🔑 Contraseña (mínimo 8 caracteres): ").strip()
            if not validar_contraseña(contraseña):
                print("   ❌ Contraseña muy corta. Usa al menos 8 caracteres")
                continue
            
            # Confirmar contraseña
            confirmacion = input("🔑 Confirma la contraseña: ").strip()
            if contraseña != confirmacion:
                print("   ❌ Las contraseñas no coinciden")
                continue
            
            break
        
        # Crear usuario
        print("\n⏳ Creando administrador...")
        
        usuario_admin = Usuario(
            usuario=usuario,
            nombre=nombre,
            email=email,
            contacto=contacto,
            rol=RolUsuario.ADMIN_PROG,
            hash_password=bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8'),
            activo=True
        )
        
        # Guardar en base de datos
        print("📝 Guardando en MongoDB...")
        resultado = repo.crear_usuario(usuario_admin)
        
        if not resultado:
            raise Exception("No se pudo guardar el usuario en la base de datos")
        
        print("\n" + "=" * 70)
        print("✅ ¡ADMINISTRADOR CREADO EXITOSAMENTE!")
        print("=" * 70)
        print(f"Usuario: {usuario}")
        print(f"Email: {email}")
        print(f"Rol: Administrador de Programación")
        print("\n🚀 Ahora puedes ejecutar: python main.py")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nVerifica que:")
        print("  • MongoDB Atlas esté disponible")
        print("  • Las credenciales en .env sean correctas")
        print("  • Tu IP esté en la whitelist de Network Access")
        sys.exit(1)


if __name__ == "__main__":
    main()
