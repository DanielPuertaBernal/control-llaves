"""
Sistema de Control de Llaves - Arquitectura MVC
Punto de entrada principal de la aplicación
"""
from tkinter import Tk, messagebox
from presentation.views import MainView
from presentation.views.login_view import mostrar_login
from presentation.assets.estiloTkinter import ConfigurarVentanaPrincipal, AplicarEstilo
from domain.usuario import RolUsuario
from application.auth.session_manager import SessionManager
from application.service_factory import ServiceFactory


def crear_usuarios_demo():
    """Crea usuarios de demostración si no existen"""
    try:
        factory = ServiceFactory()
        auth_service = factory.get_auth_service()
        repo = factory._usuario_repo
        
        # Verificar si ya existen
        admin = repo.buscar_por_usuario("admin")
        auxiliar = repo.buscar_por_usuario("auxiliar")
        
        if not admin:
            exito, msg = auth_service.crear_usuario(
                usuario="admin",
                nombre="Administrador",
                email="admin@universidad.edu",
                contacto="+57 300 123 4567",
                password="admin123",
                rol=RolUsuario.ADMIN_PROG
            )
            print(f"Admin: {msg}")
        
        if not auxiliar:
            exito, msg = auth_service.crear_usuario(
                usuario="auxiliar",
                nombre="Auxiliar de Programación",
                email="auxiliar@universidad.edu",
                contacto="+57 300 765 4321",
                password="aux123",
                rol=RolUsuario.AUX_PROG
            )
            print(f"Auxiliar: {msg}")
            
    except Exception as e:
        print(f"⚠️  No se pudieron crear usuarios demo: {e}")


def main():
    """Función principal de la aplicación"""
    # Crear usuarios de demo si no existen
    crear_usuarios_demo()
    
    # Mostrar login
    login_exitoso, usuario = mostrar_login()
    
    if not login_exitoso or not usuario:
        print("❌ Login cancelado")
        return
    
    print(f"✅ Usuario autenticado: {usuario.nombre} ({usuario.rol.value})")
    
    # Crear ventana raíz
    root = Tk()
    root.title("Sistema de Control de Llaves")
    root.geometry("1200x800")
    
    # Aplicar estilos visuales
    try:
        ConfigurarVentanaPrincipal(root)
        AplicarEstilo(root)
    except Exception as e:
        print(f"Advertencia: No se pudo aplicar configuración visual: {e}")
    
    # Inicializar vista principal (MVC) con usuario autenticado
    app = MainView(root, usuario)
    
    # Iniciar loop de la aplicación
    root.mainloop()
    
    # Cerrar sesión al salir
    SessionManager().cerrar_sesion()
    print("✅ Sesión cerrada")


if __name__ == "__main__":
    main()
