"""
Gestor de NFC para la aplicación principal
Separa la lógica de inicialización y callbacks NFC
"""
from services.nfc_service import NFCService
from controllers.nfc_controller import NFCController
from views.feedback_view import FeedbackView


class NFCManager:
    """Administrador de funcionalidad NFC para la aplicación"""
    
    def __init__(self, root, llave_controller, programacion_controller):
        """
        Args:
            root: Ventana raíz de Tkinter
            llave_controller: Controlador de llaves
            programacion_controller: Controlador de programación
        """
        self.root = root
        self.nfc_service = NFCService()
        self.nfc_controller = NFCController(llave_controller, programacion_controller)
        self.feedback_view = None
        self.nfc_conectado = False
        self.callback_actualizar_vistas = None
    
    def inicializar(self, callback_actualizar_vistas=None):
        """
        Inicializa el sistema NFC
        
        Args:
            callback_actualizar_vistas: Función a llamar cuando se actualicen datos
        """
        self.callback_actualizar_vistas = callback_actualizar_vistas
        # Intentar conectar después de 1 segundo
        self.root.after(1000, self._conectar_nfc)
    
    def _conectar_nfc(self):
        """Conecta el lector NFC automáticamente"""
        try:
            exito, mensaje = self.nfc_service.conectar()
            
            if exito:
                self.nfc_conectado = True
                # Iniciar escucha automática
                exito_escucha, mensaje_escucha = self.nfc_service.iniciar_escucha(self._on_carnet_leido)
                if exito_escucha:
                    print(f"✅ NFC iniciado: {mensaje}")
                else:
                    print(f"⚠️ NFC conectado pero no escucha: {mensaje_escucha}")
            else:
                print(f"⚠️ NFC no disponible: {mensaje}")
                # Reintentar cada 10 segundos
                self.root.after(10000, self._conectar_nfc)
        
        except Exception as e:
            print(f"Error al inicializar NFC: {e}")
            self.root.after(10000, self._conectar_nfc)
    
    def _on_carnet_leido(self, id_carnet):
        """
        Callback ejecutado cuando se lee un carnet NFC
        
        Args:
            id_carnet: ID del carnet leído
        """
        try:
            print(f"📡 Carnet leído: {id_carnet}")
            
            # Procesar lectura con el controlador NFC
            resultado = self.nfc_controller.procesar_lectura_nfc(id_carnet)
            
            # Crear vista de feedback si no existe
            if not self.feedback_view:
                self.feedback_view = FeedbackView(self.root)
            
            # Mostrar feedback según el resultado
            self._mostrar_feedback(resultado)
            
            # Actualizar vistas si hubo éxito en entrega/devolución
            if resultado['accion'] in ['entrega', 'devolucion'] and resultado['exito']:
                if self.callback_actualizar_vistas:
                    self.callback_actualizar_vistas()
        
        except Exception as e:
            print(f"Error en callback NFC: {e}")
            if self.feedback_view:
                self.feedback_view.mostrar_error(
                    f"❌ Error al procesar carnet:\n{str(e)}",
                    duracion=3000
                )
    
    def _mostrar_feedback(self, resultado):
        """Muestra el feedback visual según el resultado del procesamiento"""
        if resultado['accion'] == 'entrega':
            self.feedback_view.mostrar_entrega(
                resultado['datos_docente'],
                resultado['datos_clase'],
                duracion=2000
            )
        
        elif resultado['accion'] == 'devolucion':
            self.feedback_view.mostrar_devolucion(
                resultado['datos_docente'],
                resultado['hora_devolucion'],
                duracion=2000
            )
        
        elif resultado['accion'] == 'advertencia':
            self.feedback_view.mostrar_advertencia(
                resultado['mensaje'],
                resultado['tiempo_faltante'],
                resultado['callback_confirmar']
            )
        
        elif resultado['accion'] == 'error':
            self.feedback_view.mostrar_error(
                resultado['mensaje'],
                duracion=3000
            )
    
    def desconectar(self):
        """Desconecta el servicio NFC"""
        if self.nfc_conectado:
            self.nfc_service.desconectar()
            self.nfc_conectado = False
    
    def obtener_estado(self):
        """
        Obtiene el estado actual del sistema NFC
        
        Returns:
            dict: Información del estado
        """
        return self.nfc_service.obtener_estado()
