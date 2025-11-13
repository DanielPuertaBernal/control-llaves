"""
Sistema de Control de Llaves - Arquitectura MVC
Punto de entrada principal de la aplicación
"""
from tkinter import Tk
from views import MainView
from assets.estiloTkinter import ConfigurarVentanaPrincipal, AplicarEstilo


def main():
    """Función principal de la aplicación"""
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
    
    # Inicializar vista principal (MVC)
    app = MainView(root)
    
    # Iniciar loop de la aplicación
    root.mainloop()


if __name__ == "__main__":
    main()
