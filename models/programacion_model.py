"""
Modelo para la gestión de programación académica
Maneja toda la lógica de datos relacionada con la carga y limpieza de programación
"""
import pandas as pd
import os
from datetime import datetime


class ProgramacionModel:
    """Modelo para gestionar la programación académica"""
    
    def __init__(self):
        self.programacion_original = None
        self.programacion_limpia = None
        self.ruta_data = self._obtener_ruta_data()
    
    def _obtener_ruta_data(self):
        """Obtiene la ruta del directorio data"""
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_proyecto = os.path.dirname(ruta_actual)
        return os.path.join(ruta_proyecto, "data")
    
    def cargar_programacion_guardada(self):
        """
        Carga la programación guardada previamente
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        ruta_programacion = os.path.join(self.ruta_data, "programacionLimpiaActual.xlsx")
        
        if os.path.exists(ruta_programacion):
            try:
                df = pd.read_excel(ruta_programacion)
                self.programacion_limpia = df
                mensaje = f"✅ Programación cargada: {len(df)} registros"
                return True, df, mensaje
            except Exception as e:
                return False, None, f"Error al cargar: {str(e)}"
        
        return False, None, "❌ No hay programación guardada"
    
    def cargar_desde_archivo(self, ruta_archivo):
        """
        Carga y procesa un archivo de programación
        
        Args:
            ruta_archivo (str): Ruta al archivo Excel/CSV
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        try:
            # Cargar archivo según extensión
            if ruta_archivo.endswith('.csv'):
                df = pd.read_csv(ruta_archivo, encoding='utf-8')
            else:
                df = pd.read_excel(ruta_archivo)
            
            # Validar columnas requeridas
            if not self._validar_columnas(df):
                return False, None, "❌ El archivo no tiene las columnas requeridas (nroidenti, profesor, aula)"
            
            self.programacion_original = df
            
            # Limpiar programación
            df_limpio = self._limpiar_programacion(df)
            self.programacion_limpia = df_limpio
            
            # Guardar automáticamente
            if not self._guardar_programacion(df_limpio):
                return False, None, "❌ Error al guardar la programación procesada"
            
            mensaje = f"✅ Procesado exitosamente: {len(df_limpio)} registros"
            return True, df_limpio, mensaje
            
        except Exception as e:
            return False, None, f"❌ Error al cargar archivo: {str(e)}"
    
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
    
    def _validar_columnas(self, df):
        """Valida que el DataFrame tenga las columnas requeridas"""
        columnas_requeridas = ['nroidenti', 'profesor', 'aula']
        return all(col in df.columns for col in columnas_requeridas)
    
    def _limpiar_programacion(self, df):
        """
        Limpia y consolida la programación académica
        
        Args:
            df: DataFrame con programación original
        
        Returns:
            DataFrame limpio y consolidado
        """
        try:
            # Crear copia para no modificar el original
            df_limpio = df.copy()
            
            # Normalizar nombres de columnas
            df_limpio.columns = df_limpio.columns.str.strip()
            
            # Consolidar clases duplicadas (mismo docente, aula, materia)
            columnas_agrupar = []
            if 'nroidenti' in df_limpio.columns:
                columnas_agrupar.append('nroidenti')
            if 'profesor' in df_limpio.columns:
                columnas_agrupar.append('profesor')
            if 'aula' in df_limpio.columns:
                columnas_agrupar.append('aula')
            if 'dia' in df_limpio.columns:
                columnas_agrupar.append('dia')
            
            # Si hay columnas para agrupar, consolidar
            if columnas_agrupar:
                # Agrupar y tomar el primer registro de cada grupo
                df_limpio = df_limpio.groupby(columnas_agrupar, as_index=False).first()
            
            # Crear columna de horario si no existe
            if 'horario' not in df_limpio.columns:
                if 'hora_ini' in df_limpio.columns and 'hora_fin' in df_limpio.columns:
                    df_limpio['horario'] = df_limpio['hora_ini'].astype(str) + ' - ' + df_limpio['hora_fin'].astype(str)
                else:
                    df_limpio['horario'] = 'No especificado'
            
            # Renombrar columnas a formato estándar
            df_limpio = self._renombrar_columnas(df_limpio)
            
            # Ordenar por día y horario
            if 'Día' in df_limpio.columns and 'Hora Inicio' in df_limpio.columns:
                df_limpio = df_limpio.sort_values(['Día', 'Hora Inicio'])
            
            return df_limpio
            
        except Exception as e:
            print(f"Error al limpiar programación: {e}")
            return df
    
    def _renombrar_columnas(self, df):
        """Renombra columnas a formato estándar"""
        mapeo = {
            'nroidenti': 'Número de Documento',
            'profesor': 'Docente',
            'dia': 'Día',
            'hora_ini': 'Hora Inicio',
            'hora_fin': 'Hora Fin',
            'horario': 'Horario',
            'aula': 'Aula',
            'materia': 'Materia de la Clase',
            'PROGRAMA': 'Facultad',
            'descripcion': 'Facultad',
            'grupo': 'Grupo',
            'nivel_grupo': 'Nivel del Grupo'
        }
        
        for col_original, col_nuevo in mapeo.items():
            if col_original in df.columns:
                df.rename(columns={col_original: col_nuevo}, inplace=True)
        
        return df
    
    def _guardar_programacion(self, df):
        """Guarda la programación limpia"""
        try:
            if not os.path.exists(self.ruta_data):
                os.makedirs(self.ruta_data)
            
            ruta_archivo = os.path.join(self.ruta_data, "programacionLimpiaActual.xlsx")
            df.to_excel(ruta_archivo, index=False)
            return True
        except Exception as e:
            print(f"Error al guardar programación: {e}")
            return False
    
    @staticmethod
    def _obtener_dia_actual():
        """Obtiene el día actual en español"""
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        return dias[datetime.now().weekday()]
