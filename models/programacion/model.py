"""
Modelo para la gestión de programación académica
Orquesta las operaciones de carga, validación, limpieza y consulta de programación
"""
import pandas as pd
from datetime import datetime
from .validator import ProgramacionValidator
from .cleaner import ProgramacionCleaner
from .repository import ProgramacionRepository


class ProgramacionModel:
    """Modelo principal para gestionar la programación académica"""
    
    def __init__(self):
        self.programacion_original = None
        self.programacion_limpia = None
        self.validator = ProgramacionValidator()
        self.cleaner = ProgramacionCleaner()
        self.repository = ProgramacionRepository()
    
    def cargar_programacion_guardada(self):
        """
        Carga la programación guardada previamente
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        exito, df, mensaje = self.repository.cargar_programacion_guardada()
        
        if exito:
            self.programacion_limpia = df
        
        return exito, df, mensaje
    
    def cargar_desde_archivo(self, ruta_archivo):
        """
        Carga y procesa un archivo de programación
        
        Args:
            ruta_archivo (str): Ruta al archivo Excel/CSV
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        # Cargar archivo
        exito, df, mensaje = self.repository.cargar_desde_excel(ruta_archivo)
        
        if not exito:
            return False, None, mensaje
        
        # Validar columnas requeridas
        es_valido, mensaje_error = self.validator.validar_dataframe(df)
        if not es_valido:
            return False, None, f"❌ {mensaje_error}"
        
        self.programacion_original = df
        
        # Limpiar programación
        df_limpio = self.cleaner.limpiar_programacion(df)
        self.programacion_limpia = df_limpio
        
        # Guardar automáticamente
        exito_guardar, mensaje_guardar = self.repository.guardar_programacion(df_limpio)
        
        if not exito_guardar:
            return False, None, mensaje_guardar
        
        mensaje_final = f"✅ Procesado exitosamente: {len(df_limpio)} registros"
        return True, df_limpio, mensaje_final
    
    def obtener_programacion_actual(self):
        """Retorna la programación actualmente cargada"""
        return self.programacion_limpia
    
    def obtener_clases_del_dia(self, dia=None):
        """
        Obtiene las clases de un día específico
        
        Args:
            dia (str): Día de la semana. Si es None, usa el día actual
        
        Returns:
            pd.DataFrame: Clases del día especificado
        """
        if self.programacion_limpia is None or self.programacion_limpia.empty:
            return pd.DataFrame()
        
        if dia is None:
            dia = self._obtener_dia_actual()
        
        try:
            df_dia = self.programacion_limpia[self.programacion_limpia['Día'] == dia].copy()
            return df_dia
        except Exception as e:
            print(f"Error al obtener clases del día: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def _obtener_dia_actual():
        """Obtiene el día actual en español"""
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        return dias[datetime.now().weekday()]
