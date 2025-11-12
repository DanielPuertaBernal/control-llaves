from tkinter import Tk
from ui.interfaz import App
from assets.estiloTkinter import ConfigurarVentanaPrincipal

def main():
    root = Tk()
    root.title("Sistema de Control de Llaves")
    root.geometry("1000x700")

    try:
        ConfigurarVentanaPrincipal(root)
    except Exception as e:
        print(f"No se pudo aplicar configuración visual: {e}")

    app = App(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
