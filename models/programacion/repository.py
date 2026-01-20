"""
Repositorio de programación académica
Responsabilidad: Persistencia (carga y guardado) de datos de programación
"""
import pandas as pd
import os


class ProgramacionRepository:
    """Repositorio para operaciones de persistencia de programación"""
    
    NOMBRE_ARCHIVO = "programacionLimpiaActual.xlsx"
    
    def __init__(self, ruta_data: str = None):
        """
        Inicializa el repositorio
        
        Args:
            ruta_data: Ruta del directorio data. Si es None, se calcula automáticamente
        """
        self.ruta_data = ruta_data or self._obtener_ruta_data()
    
    def _obtener_ruta_data(self) -> str:
        """
        Obtiene la ruta del directorio data
        
        Returns:
            str: Ruta absoluta al directorio data
        """
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        # Preferir carpeta data en la raíz del proyecto
        ruta_proyecto = os.path.dirname(os.path.dirname(ruta_actual))
        ruta_data_principal = os.path.join(ruta_proyecto, "data")
        ruta_data_legacy = os.path.join(os.path.dirname(ruta_actual), "data")

        # Si existe la ruta principal, úsala; si no, cae a la legacy; si ninguna existe, crea en principal
        if os.path.exists(ruta_data_principal):
            return ruta_data_principal
        if os.path.exists(ruta_data_legacy):
            return ruta_data_legacy
        return ruta_data_principal
    
    def cargar_desde_excel(self, ruta_archivo: str) -> tuple[bool, pd.DataFrame, str]:
        """
        Carga un archivo Excel o CSV
        
        Args:
            ruta_archivo: Ruta al archivo
            
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        try:
            if ruta_archivo.endswith('.csv'):
                df = pd.read_csv(ruta_archivo, encoding='utf-8')
            else:
                df = pd.read_excel(ruta_archivo)
            
            return True, df, f"✅ Archivo cargado: {len(df)} registros"
            
        except Exception as e:
            return False, None, f"❌ Error al cargar archivo: {str(e)}"
    
    def cargar_programacion_guardada(self) -> tuple[bool, pd.DataFrame, str]:
        """
        Carga la programación guardada previamente
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        ruta_programacion = os.path.join(self.ruta_data, self.NOMBRE_ARCHIVO)
        
        if not os.path.exists(ruta_programacion):
            return False, None, "❌ No hay programación guardada"
        
        try:
            df = pd.read_excel(ruta_programacion)
            mensaje = f"✅ Programación cargada: {len(df)} registros"
            return True, df, mensaje
        except Exception as e:
            return False, None, f"❌ Error al cargar: {str(e)}"
    
    def guardar_programacion(self, df: pd.DataFrame) -> tuple[bool, str]:
        """
        Guarda la programación limpia
        
        Args:
            df: DataFrame a guardar
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not os.path.exists(self.ruta_data):
                os.makedirs(self.ruta_data)
            
            ruta_archivo = os.path.join(self.ruta_data, self.NOMBRE_ARCHIVO)
            df.to_excel(ruta_archivo, index=False)
            return True, f"✅ Programación guardada: {ruta_archivo}"
            
        except Exception as e:
            return False, f"❌ Error al guardar: {str(e)}"
    
    def existe_programacion_guardada(self) -> bool:
        """
        Verifica si existe una programación guardada
        
        Returns:
            bool: True si existe
        """
        ruta_programacion = os.path.join(self.ruta_data, self.NOMBRE_ARCHIVO)
        return os.path.exists(ruta_programacion)
