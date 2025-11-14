"""
Configuración centralizada de la aplicación
Define constantes y parámetros globales
"""
import os


class Config:
    """Configuración general de la aplicación"""
    
    # Información de la aplicación
    APP_NAME = "Sistema de Control de Llaves"
    APP_VERSION = "2.0.0"
    APP_AUTHOR = "Sistema MVC"
    
    # Configuración de ventana principal
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 1000
    WINDOW_MIN_HEIGHT = 600
    
    # Rutas de datos
    DATA_DIR = "data"
    REGISTRO_LLAVES = "registrosLlaves.xlsx"
    PROGRAMACION_ACTUAL = "programacionLimpiaActual.xlsx"
    
    # Configuración de paginación
    ITEMS_POR_PAGINA = 15
    
    # Configuración de actualización automática
    INTERVALO_ACTUALIZACION_ENTREGA = 600000  # 10 minutos en ms
    INTERVALO_ACTUALIZACION_HISTORIAL = 30000  # 30 segundos en ms
    DEBOUNCE_BUSQUEDA = 300  # 300ms para búsqueda
    
    # Días de la semana
    DIAS_SEMANA = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
    
    # Configuración de colores (tema)
    COLOR_PRIMARIO = "#2E7D32"      # Verde oscuro
    COLOR_SECUNDARIO = "#4CAF50"    # Verde claro
    COLOR_ACENTO = "#81C784"        # Verde muy claro
    COLOR_FONDO = "#F5F5F5"         # Gris claro
    COLOR_TEXTO = "#212121"         # Gris oscuro
    COLOR_BLANCO = "#FFFFFF"
    COLOR_EXITO = "#2e7d32"         # Verde
    COLOR_ERROR = "#d32f2f"         # Rojo
    COLOR_ADVERTENCIA = "#f57c00"   # Naranja
    
    # Fuentes
    FONT_FAMILIA = "Segoe UI"
    FONT_TITULO_SIZE = 18
    FONT_SUBTITULO_SIZE = 14
    FONT_NORMAL_SIZE = 10
    
    @classmethod
    def obtener_ruta_data(cls):
        """Obtiene la ruta absoluta del directorio de datos"""
        ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(ruta_base, cls.DATA_DIR)
    
    @classmethod
    def obtener_ruta_archivo(cls, nombre_archivo):
        """Obtiene la ruta completa de un archivo en el directorio data"""
        return os.path.join(cls.obtener_ruta_data(), nombre_archivo)
