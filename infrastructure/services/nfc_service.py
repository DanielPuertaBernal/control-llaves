"""
Servicio para lectura de carnets NFC/RFID mediante Arduino
Maneja la comunicación serial y eventos de lectura automática
"""
import serial
import serial.tools.list_ports
import threading
import time


class NFCService:
    """Servicio de lectura NFC/RFID"""
    
    def __init__(self, baudrate=9600, timeout=1):
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.is_listening = False
        self.listen_thread = None
        self.callback = None
        self.ultimo_id_leido = None
        self.tiempo_ultimo_id = 0
        self.debounce_time = 2  # Segundos para ignorar lecturas duplicadas
    
    def buscar_puerto_arduino(self):
        """
        Busca automáticamente el puerto del Arduino
        Prioriza /dev/ttyACM0 en Linux para compatibilidad
        
        Returns:
            str: Puerto encontrado o None
        """
        import platform
        
        # En Linux, priorizar /dev/ttyACM0
        if platform.system() == 'Linux':
            import os
            if os.path.exists('/dev/ttyACM0'):
                return '/dev/ttyACM0'
        
        # Buscar en todos los puertos disponibles
        puertos = serial.tools.list_ports.comports()
        
        # Buscar puertos que contengan "Arduino" o "CH340" o "USB"
        for puerto in puertos:
            descripcion = puerto.description.lower()
            if 'arduino' in descripcion or 'ch340' in descripcion or 'usb' in descripcion:
                return puerto.device
        
        # Si no encuentra, retornar el primer puerto disponible
        if puertos:
            return puertos[0].device
        
        return None
    
    def conectar(self, puerto=None):
        """
        Conecta con el Arduino en el puerto especificado
        
        Args:
            puerto (str): Puerto serial (ej: '/dev/ttyUSB0', 'COM3')
                         Si es None, busca automáticamente
        
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if self.serial_connection and self.serial_connection.is_open:
                return True, "Ya está conectado"
            
            # Si no se especifica puerto, buscar automáticamente
            if puerto is None:
                puerto = self.buscar_puerto_arduino()
                if puerto is None:
                    return False, "❌ No se encontró ningún dispositivo Arduino"
            
            # Intentar conectar
            self.serial_connection = serial.Serial(
                port=puerto,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            # Esperar a que Arduino se inicialice
            time.sleep(2)
            
            # Limpiar buffer
            self.serial_connection.reset_input_buffer()
            
            return True, f"✅ Conectado al puerto: {puerto}"
            
        except serial.SerialException as e:
            return False, f"❌ Error al conectar: {str(e)}"
        except Exception as e:
            return False, f"❌ Error inesperado: {str(e)}"
    
    def desconectar(self):
        """Cierra la conexión serial"""
        try:
            self.detener_escucha()
            
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                return True, "✅ Desconectado"
            
            return True, "No había conexión activa"
            
        except Exception as e:
            return False, f"❌ Error al desconectar: {str(e)}"
    
    def leer_carnet(self):
        """
        Lee un ID de carnet del Arduino (lectura única)
        
        Returns:
            str: ID del carnet leído o None
        """
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                return None
            
            # Limpiar buffer antes de leer
            self.serial_connection.reset_input_buffer()
            
            # Esperar hasta 5 segundos por una lectura
            inicio = time.time()
            while time.time() - inicio < 5:
                if self.serial_connection.in_waiting > 0:
                    linea = self.serial_connection.readline().decode('utf-8').strip()
                    if linea:
                        return linea.upper()
                time.sleep(0.1)
            
            return None
            
        except Exception as e:
            print(f"Error al leer carnet: {e}")
            return None
    
    def _loop_escucha(self):
        """Loop de escucha continua (ejecutado en thread separado)"""
        print("[NFC] Iniciando loop de escucha...")
        while self.is_listening:
            try:
                if self.serial_connection and self.serial_connection.is_open:
                    if self.serial_connection.in_waiting > 0:
                        linea = self.serial_connection.readline().decode('utf-8').strip()
                        print(f"[NFC] Datos recibidos: {linea}")
                        
                        if linea:
                            # Normalizar formato: reemplazar comillas simples por guiones
                            # INV'12'012 → INV-12-012
                            id_carnet = linea.replace("'", "-").upper()
                            print(f"[NFC] ID normalizado: {id_carnet}")
                            tiempo_actual = time.time()
                            
                            print(f"[NFC] ID carnet: {id_carnet}, Último: {self.ultimo_id_leido}")
                            
                            # Debounce: ignorar si es el mismo ID en menos de N segundos
                            if (id_carnet == self.ultimo_id_leido and 
                                tiempo_actual - self.tiempo_ultimo_id < self.debounce_time):
                                print(f"[NFC] Ignorado por debounce")
                                continue
                            
                            # Actualizar último ID leído
                            self.ultimo_id_leido = id_carnet
                            self.tiempo_ultimo_id = tiempo_actual
                            
                            # Llamar callback si existe
                            if self.callback:
                                print(f"[NFC] Ejecutando callback con ID: {id_carnet}")
                                self.callback(id_carnet)
                            else:
                                print(f"[NFC] ⚠️ No hay callback configurado!")
                
                time.sleep(0.1)  # Pequeña pausa para no saturar CPU
                
            except Exception as e:
                print(f"[NFC] Error en loop de escucha: {e}")
                time.sleep(1)  # Esperar un poco antes de reintentar
    
    def iniciar_escucha(self, callback):
        """
        Inicia escucha continua de carnets
        
        Args:
            callback (function): Función a llamar cuando se lee un carnet
                                Recibe el ID del carnet como parámetro
        
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if self.is_listening:
                return True, "Ya está escuchando"
            
            if not self.serial_connection or not self.serial_connection.is_open:
                return False, "❌ No hay conexión activa. Conecte primero el lector."
            
            self.callback = callback
            self.is_listening = True
            
            # Iniciar thread de escucha
            self.listen_thread = threading.Thread(target=self._loop_escucha, daemon=True)
            self.listen_thread.start()
            
            return True, "✅ Escucha de carnets iniciada"
            
        except Exception as e:
            return False, f"❌ Error al iniciar escucha: {str(e)}"
    
    def detener_escucha(self):
        """Detiene la escucha continua"""
        self.is_listening = False
        
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
            self.listen_thread = None
        
        self.callback = None
        return True, "✅ Escucha detenida"
    
    def esta_conectado(self):
        """Verifica si hay conexión activa"""
        return self.serial_connection and self.serial_connection.is_open
    
    def esta_escuchando(self):
        """Verifica si está escuchando carnets"""
        return self.is_listening
    
    def obtener_estado(self):
        """
        Obtiene el estado actual del servicio
        
        Returns:
            dict: Información del estado
        """
        return {
            'conectado': self.esta_conectado(),
            'escuchando': self.esta_escuchando(),
            'puerto': self.serial_connection.port if self.serial_connection else None
        }
