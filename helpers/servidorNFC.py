from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import threading
from datetime import datetime
import pandas as pd
from helpers.gestionExcel import RegistrarEntrega, VerificarLlaveEntregada, LimpiarNumeroDocumento
from helpers.limpiezaProgramacion import ObtenerRutaArchivo

class NFCHandler(BaseHTTPRequestHandler):
    """Manejador de peticiones HTTP para lecturas NFC"""
    
    def do_GET(self):
        """Maneja peticiones GET desde NFC Tools"""
        try:
            # Parsear la URL para obtener parámetros
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            
            # Obtener número de documento desde el parámetro 'cedula' o 'documento'
            cedula = params.get('cedula', params.get('documento', [None]))[0]
            
            if not cedula:
                self._enviar_respuesta(400, {
                    'success': False,
                    'mensaje': 'No se proporcionó número de documento'
                })
                return
            
            # Procesar la entrega automática
            resultado = self._procesar_entrega_nfc(cedula)
            
            # Enviar respuesta
            codigo = 200 if resultado['success'] else 400
            self._enviar_respuesta(codigo, resultado)
            
        except Exception as e:
            self._enviar_respuesta(500, {
                'success': False,
                'mensaje': f'Error en el servidor: {str(e)}'
            })
    
    def do_POST(self):
        """Maneja peticiones POST desde NFC Tools"""
        try:
            # Leer el cuerpo de la petición
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Intentar parsear como JSON
            try:
                data = json.loads(post_data.decode('utf-8'))
                cedula = data.get('cedula') or data.get('documento')
            except:
                # Si no es JSON, intentar como form data
                params = parse_qs(post_data.decode('utf-8'))
                cedula = params.get('cedula', params.get('documento', [None]))[0]
            
            if not cedula:
                self._enviar_respuesta(400, {
                    'success': False,
                    'mensaje': 'No se proporcionó número de documento'
                })
                return
            
            # Procesar la entrega automática
            resultado = self._procesar_entrega_nfc(cedula)
            
            # Enviar respuesta
            codigo = 200 if resultado['success'] else 400
            self._enviar_respuesta(codigo, resultado)
            
        except Exception as e:
            self._enviar_respuesta(500, {
                'success': False,
                'mensaje': f'Error en el servidor: {str(e)}'
            })
    
    def _procesar_entrega_nfc(self, cedula):
        """
        Procesa la entrega automática basada en el número de documento NFC
        
        Args:
            cedula: Número de documento del docente
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Limpiar número de documento
            cedula_limpia = LimpiarNumeroDocumento(cedula)
            
            # Verificar si ya tiene una llave entregada
            if VerificarLlaveEntregada(cedula_limpia):
                return {
                    'success': False,
                    'mensaje': 'El docente ya tiene una llave entregada',
                    'documento': cedula_limpia
                }
            
            # Cargar programación del día
            clase_actual = self._buscar_clase_actual(cedula_limpia)
            
            if not clase_actual:
                return {
                    'success': False,
                    'mensaje': 'No se encontró clase activa para este documento en este momento',
                    'documento': cedula_limpia
                }
            
            # Registrar la entrega
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
                return {
                    'success': False,
                    'mensaje': 'Error al registrar la entrega',
                    'documento': cedula_limpia
                }
                
        except Exception as e:
            return {
                'success': False,
                'mensaje': f'Error al procesar entrega: {str(e)}',
                'documento': cedula
            }
    
    def _buscar_clase_actual(self, cedula):
        """
        Busca la clase actual del docente basándose en día y hora
        
        Args:
            cedula: Número de documento limpio
            
        Returns:
            dict: Información de la clase o None
        """
        try:
            # Cargar programación
            ruta_programacion = ObtenerRutaArchivo("programacionLimpiaActual.xlsx")
            df = pd.read_excel(ruta_programacion)
            
            # Obtener día y hora actual
            ahora = datetime.now()
            dia_numero = ahora.weekday()
            dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            dia_actual = dias_espanol[dia_numero]
            hora_actual = ahora.time()
            
            # Filtrar por documento y día
            df['Número de Documento'] = df['Número de Documento'].astype(str).apply(LimpiarNumeroDocumento)
            df_docente = df[
                (df['Número de Documento'] == cedula) & 
                (df['Día'] == dia_actual)
            ]
            
            if df_docente.empty:
                return None
            
            # Buscar clase activa (en este momento o próxima en las siguientes 2 horas)
            for _, fila in df_docente.iterrows():
                try:
                    # Parsear horario
                    horario = str(fila['Horario'])
                    if ' a ' in horario.lower():
                        hora_ini_str, hora_fin_str = horario.lower().split(' a ')
                        hora_ini = datetime.strptime(hora_ini_str.strip(), '%H:%M:%S').time()
                        hora_fin = datetime.strptime(hora_fin_str.strip(), '%H:%M:%S').time()
                        
                        # Ventana de tiempo: 30 minutos antes hasta que termine la clase
                        from datetime import timedelta, time
                        
                        # Calcular 30 minutos antes
                        hora_ini_datetime = datetime.combine(datetime.today(), hora_ini)
                        ventana_inicio = (hora_ini_datetime - timedelta(minutes=30)).time()
                        
                        # Verificar si estamos en la ventana de tiempo
                        if ventana_inicio <= hora_actual <= hora_fin:
                            return {
                                'nroidenti': cedula,
                                'profesor': str(fila['Docente']),
                                'dia': dia_actual,
                                'horario': horario,
                                'aula': str(fila['Aula']),
                                'facultad': str(fila.get('Facultad', 'No especificada')),
                                'materia': str(fila['Materia de la Clase'])
                            }
                except Exception as e:
                    print(f"Error procesando horario: {e}")
                    continue
            
            # Si no hay clase activa, buscar la próxima del día
            for _, fila in df_docente.iterrows():
                try:
                    horario = str(fila['Horario'])
                    if ' a ' in horario.lower():
                        hora_ini_str, _ = horario.lower().split(' a ')
                        hora_ini = datetime.strptime(hora_ini_str.strip(), '%H:%M:%S').time()
                        
                        # Si la clase es en las próximas 2 horas
                        if hora_ini > hora_actual:
                            hora_ini_datetime = datetime.combine(datetime.today(), hora_ini)
                            ahora_datetime = datetime.combine(datetime.today(), hora_actual)
                            diferencia = (hora_ini_datetime - ahora_datetime).total_seconds() / 3600
                            
                            if diferencia <= 2:  # Menos de 2 horas
                                return {
                                    'nroidenti': cedula,
                                    'profesor': str(fila['Docente']),
                                    'dia': dia_actual,
                                    'horario': horario,
                                    'aula': str(fila['Aula']),
                                    'facultad': str(fila.get('Facultad', 'No especificada')),
                                    'materia': str(fila['Materia de la Clase'])
                                }
                except Exception as e:
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
        
        respuesta = json.dumps(datos, ensure_ascii=False, indent=2)
        self.wfile.write(respuesta.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Sobrescribir para personalizar logs"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")


class ServidorNFC:
    """Clase para manejar el servidor HTTP NFC"""
    
    def __init__(self, host='0.0.0.0', puerto=8080):
        self.host = host
        self.puerto = puerto
        self.servidor = None
        self.thread = None
        self.corriendo = False
    
    def iniciar(self):
        """Inicia el servidor en un thread separado"""
        if self.corriendo:
            print("El servidor ya está corriendo")
            return
        
        try:
            self.servidor = HTTPServer((self.host, self.puerto), NFCHandler)
            self.corriendo = True
            
            # Iniciar en thread separado
            self.thread = threading.Thread(target=self._ejecutar_servidor, daemon=True)
            self.thread.start()
            
            print(f"\n{'='*60}")
            print(f"🔐 SERVIDOR NFC INICIADO")
            print(f"{'='*60}")
            print(f"📡 Escuchando en: http://{self.host}:{self.puerto}")
            print(f"📱 URL para NFC Tools:")
            print(f"   http://[TU_IP]:{self.puerto}/entrega?cedula=[CEDULA]")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
            self.corriendo = False
    
    def _ejecutar_servidor(self):
        """Ejecuta el servidor (método interno)"""
        try:
            self.servidor.serve_forever()
        except Exception as e:
            print(f"Error en servidor: {e}")
            self.corriendo = False
    
    def detener(self):
        """Detiene el servidor"""
        if self.servidor:
            self.servidor.shutdown()
            self.corriendo = False
            print("\n🛑 Servidor NFC detenido")
    
    def esta_corriendo(self):
        """Verifica si el servidor está corriendo"""
        return self.corriendo


# Función helper para usar en main.py
def iniciar_servidor_nfc(puerto=8080):
    """
    Inicia el servidor NFC automáticamente
    
    Args:
        puerto: Puerto donde escuchar (default 8080)
        
    Returns:
        ServidorNFC: Instancia del servidor
    """
    servidor = ServidorNFC(puerto=puerto)
    servidor.iniciar()
    return servidor