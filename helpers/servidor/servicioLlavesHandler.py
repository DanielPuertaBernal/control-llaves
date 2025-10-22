from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from helpers.servidor.logicaLlaves import procesar_entrega, procesar_devolucion


class ServicioLlavesHandler(BaseHTTPRequestHandler):
    """Manejador HTTP para entregar y devolver llaves (puerto único)."""

    def do_GET(self):
        parsed = urlparse(self.path)
        ruta = parsed.path.lower()
        params = parse_qs(parsed.query)
        cedula = params.get('cedula', [None])[0]
        aula = params.get('aula', [None])[0]

        try:
            if ruta == '/entregar':
                if not cedula:
                    return self._responder(400, {'success': False, 'mensaje': 'Falta número de documento'})
                resultado = procesar_entrega(cedula)
            elif ruta == '/devolver':
                if not cedula or not aula:
                    return self._responder(400, {'success': False, 'mensaje': 'Faltan datos para devolución'})
                resultado = procesar_devolucion(cedula, aula)
            else:
                return self._responder(404, {'success': False, 'mensaje': 'Ruta no encontrada'})

            self._responder(200 if resultado['success'] else 400, resultado)

        except Exception as e:
            self._responder(500, {'success': False, 'mensaje': str(e)})

    def do_POST(self):
        parsed = urlparse(self.path)
        ruta = parsed.path.lower()
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length).decode('utf-8')
            try:
                body = json.loads(data)
            except:
                body = parse_qs(data)
                body = {k: v[0] for k, v in body.items()}

            cedula = body.get('cedula')
            aula = body.get('aula')

            if ruta == '/entregar':
                if not cedula:
                    return self._responder(400, {'success': False, 'mensaje': 'Falta número de documento'})
                resultado = procesar_entrega(cedula)
            elif ruta == '/devolver':
                if not cedula or not aula:
                    return self._responder(400, {'success': False, 'mensaje': 'Faltan datos para devolución'})
                resultado = procesar_devolucion(cedula, aula)
            else:
                return self._responder(404, {'success': False, 'mensaje': 'Ruta no encontrada'})

            self._responder(200 if resultado['success'] else 400, resultado)
        except Exception as e:
            self._responder(500, {'success': False, 'mensaje': str(e)})

    def _responder(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def log_message(self, *args):
        pass
