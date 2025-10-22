from http.server import HTTPServer
from pyngrok import ngrok
import threading
import os

class ServidorHTTP:
    def __init__(self, handler, host='0.0.0.0', puerto=8080, usar_ngrok=False):
        self.host = host
        self.puerto = puerto
        self.usar_ngrok = usar_ngrok
        self.handler = handler
        self.servidor = None
        self.tunnel = None
        self.thread = None
        self.corriendo = False

    def iniciar(self):
        if self.corriendo:
            print("⚠️ El servidor ya está corriendo")
            return

        try:
            self.servidor = HTTPServer((self.host, self.puerto), self.handler)
            self.corriendo = True

            if self.usar_ngrok:
                token = os.getenv("NGROK_AUTH_TOKEN")
                if token:
                    ngrok.set_auth_token(token)
                self.tunnel = ngrok.connect(self.puerto, "http")
                print(f"🌍 URL pública: {self.tunnel.public_url}")

            self.thread = threading.Thread(target=self.servidor.serve_forever, daemon=True)
            self.thread.start()
            print(f"✅ Servidor HTTP escuchando en {self.host}:{self.puerto}")

        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")
            self.corriendo = False

    def detener(self):
        if self.servidor:
            self.servidor.shutdown()
        if self.tunnel:
            ngrok.disconnect(self.tunnel.public_url)
        self.corriendo = False
        print("🛑 Servidor detenido")


def iniciar_servidor(handler, puerto=8080, usar_ngrok=False):
    servidor = ServidorHTTP(handler, puerto=puerto, usar_ngrok=usar_ngrok)
    servidor.iniciar()
    return servidor
