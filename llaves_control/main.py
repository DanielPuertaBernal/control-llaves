"""
Sistema de Control de Llaves
Aplicación para gestionar la entrega y devolución de llaves de aulas
"""
from tkinter import Tk
from ui.interfaz import App
from assets.estilo_tkinter import configurar_ventana_principal

def main():
    """Función principal de la aplicación"""
    root = Tk()
    root.title("Sistema de Control de Llaves")
    root.geometry("1000x700")
    
    # Aplicar configuración de ventana
    try:
        configurar_ventana_principal(root)
    except:
        pass  # Si falla la configuración, continuar sin ella
    
    # Crear la aplicación
    app = App(root)
    
    # Iniciar el loop principal
    root.mainloop()

if __name__ == "__main__":
    main()
