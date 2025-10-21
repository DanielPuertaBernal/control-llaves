from tkinter import Tk
from ui.interfaz import App
from assets.estiloTkinter import ConfigurarVentanaPrincipal
from helpers.servidorNFC import iniciar_servidor_nfc
import atexit
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

servidor_nfc = None

def main():
    global servidor_nfc

    root = Tk()
    root.title("Sistema de Control de Llaves")
    root.geometry("1000x700")

    try:
        ConfigurarVentanaPrincipal(root)
    except Exception:
        pass

    app = App(root)

    # Configuración
    nfc_port = int(os.getenv('NFC_PORT', '8080'))
    start_nfc = os.getenv('START_NFC', 'true').lower() in ('1', 'true', 'yes', 'y')
    use_ngrok = os.getenv('NFC_USE_NGROK', '0').lower() in ('1', 'true', 'yes', 'y')

    if start_nfc:
        try:
            if use_ngrok:
                print("🌐 Iniciando servidor NFC con túnel ngrok...")
                servidor_nfc = iniciar_servidor_nfc(puerto=nfc_port, usar_ngrok=True)
            else:
                print("🔐 Iniciando servidor NFC local...")
                servidor_nfc = iniciar_servidor_nfc(puerto=nfc_port)
            print("✅ Servidor NFC iniciado correctamente")
        except Exception as e:
            print(f"⚠️ No se pudo iniciar el servidor NFC: {e}")
            print("La aplicación funcionará sin funcionalidad NFC")
    else:
        print("ℹ️ START_NFC deshabilitado; no se iniciará el servidor NFC")

    def detener_servidor():
        if servidor_nfc:
            try:
                servidor_nfc.detener()
            except Exception:
                pass

    atexit.register(detener_servidor)
    root.protocol("WM_DELETE_WINDOW", lambda: [detener_servidor(), root.destroy()])

    root.mainloop()

if __name__ == "__main__":
    main()
