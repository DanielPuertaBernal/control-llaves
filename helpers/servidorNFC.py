from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import threading
from datetime import datetime
import pandas as pd
from helpers.gestionExcel import RegistrarEntrega, VerificarLlaveEntregada, LimpiarNumeroDocumento
from helpers.limpiezaProgramacion import ObtenerRutaArchivo
import os
from pyngrok import ngrok 

class NFCHandler(BaseHTTPRequestHandler):
    """Manejador de peticiones HTTP para lecturas NFC"""

    def do_GET(self):
        """Maneja peticiones GET desde NFC Tools"""
        try:
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            cedula = params.get('cedula', params.get('documento', [None]))[0]

            print("\n🟢 [GET] Petición recibida.")
            print(f"🔗 Ruta: {self.path}")

            if not cedula:
                self._enviar_respuesta(400, {'success': False, 'mensaje': 'No se proporcionó número de documento'})
                return

            resultado = self._procesar_entrega_nfc(cedula)
            self._mostrar_resumen(resultado)

            codigo = 200 if resultado['success'] else 400
            self._enviar_respuesta(codigo, resultado)

        except Exception as e:
            print(f"❌ Error procesando GET: {e}")
            self._enviar_respuesta(500, {'success': False, 'mensaje': f'Error en el servidor: {str(e)}'})

    def do_POST(self):
        """Maneja peticiones POST desde NFC Tools"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            print("\n🟢 [POST] Petición recibida.")
            print(f"📏 Longitud: {content_length} bytes")

            # Intentar parsear como JSON
            try:
                data = json.loads(post_data)
                cedula = data.get('cedula') or data.get('documento')
            except json.JSONDecodeError:
                # Si no es JSON, intentar como formulario
                params = parse_qs(post_data)
                cedula = params.get('cedula', params.get('documento', [None]))[0]

            if not cedula:
                self._enviar_respuesta(400, {'success': False, 'mensaje': 'No se proporcionó número de documento'})
                return

            resultado = self._procesar_entrega_nfc(cedula)
            self._mostrar_resumen(resultado)

            codigo = 200 if resultado['success'] else 400
            self._enviar_respuesta(codigo, resultado)

        except Exception as e:
            print(f"❌ Error procesando POST: {e}")
            self._enviar_respuesta(500, {'success': False, 'mensaje': f'Error en el servidor: {str(e)}'})

    def _mostrar_resumen(self, resultado):
        """Imprime un resumen corto de la operación"""
        if resultado['success']:
            print(f"✅ Entrega registrada correctamente para {resultado.get('docente', 'Desconocido')} - Aula {resultado.get('aula', 'N/A')}")
            print(f"🕓 {resultado.get('horario', '')} | Materia: {resultado.get('materia', '')}")
        else:
            print(f"⚠️ No se pudo registrar entrega: {resultado.get('mensaje', '')}")

    def _procesar_entrega_nfc(self, cedula):
        """Procesa la entrega automática basada en el número de documento NFC"""
        try:
            cedula_limpia = LimpiarNumeroDocumento(cedula)

            if VerificarLlaveEntregada(cedula_limpia):
                return {'success': False, 'mensaje': 'El docente ya tiene una llave entregada', 'documento': cedula_limpia}

            clase_actual = self._buscar_clase_actual(cedula_limpia)
            if not clase_actual:
                return {'success': False, 'mensaje': 'No se encontró clase activa para este documento', 'documento': cedula_limpia}

            if RegistrarEntrega(clase_actual):
                return {
                    'success': True,
                    'mensaje': 'Llave entregada exitosamente',
                    'documento': cedula_limpia,
                    'docente': clase_actual.get('profesor'),
                    'aula': clase_actual.get('aula'),
                    'horario': clase_actual.get('horario'),
                    'materia': clase_actual.get('materia'),
                    'fecha_entrega': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {'success': False, 'mensaje': 'Error al registrar la entrega', 'documento': cedula_limpia}

        except Exception as e:
            return {'success': False, 'mensaje': f'Error al procesar entrega: {str(e)}', 'documento': cedula}

    def _buscar_clase_actual(self, cedula):
        """Busca la clase actual del docente según día y hora"""
        try:
            ruta_programacion = ObtenerRutaArchivo("programacionLimpiaActual.xlsx")
            df = pd.read_excel(ruta_programacion)
            ahora = datetime.now()
            dia_numero = ahora.weekday()
            dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            dia_actual = dias_espanol[dia_numero]
            hora_actual = ahora.time()

            df['Número de Documento'] = df['Número de Documento'].astype(str).apply(LimpiarNumeroDocumento)
            df_docente = df[(df['Número de Documento'] == cedula) & (df['Día'] == dia_actual)]

            if df_docente.empty:
                return None

            for _, fila in df_docente.iterrows():
                try:
                    horario = str(fila['Horario'])
                    if ' a ' in horario.lower():
                        hora_ini_str, hora_fin_str = horario.lower().split(' a ')
                        hora_ini = datetime.strptime(hora_ini_str.strip(), '%H:%M:%S').time()
                        hora_fin = datetime.strptime(hora_fin_str.strip(), '%H:%M:%S').time()

                        from datetime import timedelta
                        hora_ini_dt = datetime.combine(datetime.today(), hora_ini)
                        ventana_inicio = (hora_ini_dt - timedelta(minutes=30)).time()

                        if ventana_inicio <= hora_actual <= hora_fin:
                            return {
                                'nroidenti': cedula,
                                'profesor': str(fila['Docente']),
                                'dia': dia_actual,
                                'horario': horario,
                                'aula': str(fila['Aula']),
                                'materia': str(fila['Materia de la Clase'])
                            }
                except Exception:
                    continue

            return None

        except Exception as e:
            print(f"Error buscando clase actual: {e}")
            return None

    def _enviar_respuesta(self, codigo, datos):
        """Envía respuesta HTTP en formato JSON"""
        self.send_response(codigo)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(datos, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Silenciar logs del servidor HTTP


class ServidorNFC:
    def __init__(self, host='0.0.0.0', puerto=8080, usar_ngrok=False):
        self.host = host
        self.puerto = puerto
        self.usar_ngrok = usar_ngrok
        self.servidor = None
        self.tunnel = None
        self.thread = None
        self.corriendo = False

    def iniciar(self):
        if self.corriendo:
            print("El servidor ya está corriendo")
            return

        try:
            self.servidor = HTTPServer((self.host, self.puerto), NFCHandler)
            self.corriendo = True

            if self.usar_ngrok:
                token = os.getenv("NGROK_AUTH_TOKEN")
                if token:
                    ngrok.set_auth_token(token)
                self.tunnel = ngrok.connect(self.puerto, "http")
                print(f"🌍 URL pública: {self.tunnel.public_url}")

            self.thread = threading.Thread(target=self.servidor.serve_forever, daemon=True)
            self.thread.start()

            print(f"✅ Servidor NFC escuchando en {self.host}:{self.puerto}")
        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
            self.corriendo = False

    def detener(self):
        if self.servidor:
            self.servidor.shutdown()
        if self.tunnel:
            ngrok.disconnect(self.tunnel.public_url)
        self.corriendo = False
        print("🛑 Servidor NFC detenido")


def iniciar_servidor_nfc(puerto=8080, usar_ngrok=False):
    servidor = ServidorNFC(puerto=puerto, usar_ngrok=usar_ngrok)
    servidor.iniciar()
    return servidor
