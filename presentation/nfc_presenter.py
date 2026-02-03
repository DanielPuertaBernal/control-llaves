"""
Presenter NFC - Coordina entre el hardware NFC y la UI
Maneja callbacks y actualización de vistas
"""
from infrastructure.services.nfc_service import NFCService
from application.use_cases.procesar_lectura_nfc_use_case import ProcesarLecturaNFCUseCase


class NFCPresenter:
    """Coordina la funcionalidad NFC entre infraestructura y presentación"""
    
    def __init__(self, root):
        """
        Args:
            root: Ventana raíz de Tkinter para callbacks temporizados
        """
        self.root = root
        self.nfc_service = NFCService()
        self.use_case = ProcesarLecturaNFCUseCase()
        self.nfc_conectado = False
        
        # Callbacks para coordinar con la UI
        self.callback_actualizar_vistas = None
        self.callback_ir_nfc_view = None
        self.nfc_view = None
    
    def establecer_nfc_view(self, nfc_view):
        """Establece la referencia a la vista NFC para actualizar en tiempo real"""
        self.nfc_view = nfc_view
    
    def establecer_callback_ir_nfc(self, callback):
        """Establece callback para navegar a vista NFC"""
        self.callback_ir_nfc_view = callback
    
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
            
            # Ir a vista NFC automáticamente
            if self.callback_ir_nfc_view:
                self.callback_ir_nfc_view()
            
            # Procesar lectura con el caso de uso
            resultado = self.use_case.ejecutar(id_carnet)
            
            # Actualizar vista NFC si existe
            if self.nfc_view:
                self.nfc_view.actualizar_operacion(resultado)
            
            # Actualizar vistas si hubo éxito en entrega/devolución
            if resultado['accion'] in ['entrega', 'devolucion'] and resultado['exito']:
                if self.callback_actualizar_vistas:
                    self.callback_actualizar_vistas()
        
        except Exception as e:
            print(f"Error en callback NFC: {e}")
    
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
