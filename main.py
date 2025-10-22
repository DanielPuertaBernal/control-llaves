from tkinter import Tk
from ui.interfaz import App
from assets.estiloTkinter import ConfigurarVentanaPrincipal
from helpers.servidorNFC import iniciar_servidor_nfc
import atexit

# Variable global para el servidor
servidor_nfc = None

def main():
    global servidor_nfc
    
    root = Tk()
    root.title("Sistema de Control de Llaves")
    root.geometry("1000x700")
    
    # Aplicar configuración de ventana
    try:
        ConfigurarVentanaPrincipal(root)
    except:
        pass  # Si falla la configuración, continuar sin ella
    
    # Crear la aplicación
    app = App(root)
    
    # Iniciar servidor NFC en segundo plano
    try:
        servidor_nfc = iniciar_servidor_nfc(puerto=8080)
        print("✅ Servidor NFC iniciado correctamente")
    except Exception as e:
        print(f"⚠️ No se pudo iniciar el servidor NFC: {e}")
        print("La aplicación funcionará sin funcionalidad NFC")
    
    # Registrar función para detener servidor al cerrar
    def detener_servidor():
        if servidor_nfc:
            servidor_nfc.detener()
    
    atexit.register(detener_servidor)
    root.protocol("WM_DELETE_WINDOW", lambda: [detener_servidor(), root.destroy()])
    
    # Iniciar el loop principal
    root.mainloop()

if __name__ == "__main__":
    main()