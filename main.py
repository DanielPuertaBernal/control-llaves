"""
Sistema de Control de Llaves - Arquitectura MVC
Punto de entrada principal de la aplicación
"""
from tkinter import Tk
from presentation.views import MainView
from presentation.views.login_view import mostrar_login
from presentation.assets.estiloTkinter import ConfigurarVentanaPrincipal, AplicarEstilo
from application.auth.session_manager import SessionManager


def main():
    """Función principal de la aplicación"""
    
    # Autenticación
    login_exitoso, usuario = mostrar_login()
    if not login_exitoso:
        return
    
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
    
    # Vista principal
    app = MainView(root, usuario)
    root.mainloop()
    
    # Cerrar sesión
    SessionManager().cerrar_sesion()


if __name__ == "__main__":
    main()
