import pandas as pd
import os
from datetime import datetime
from helpers.limpiezaProgramacion import LimpiarProgramacion

class GestorProgramacion:
    """
    Lógica de negocio para la gestión de programación académica
    Separada de la interfaz de usuario
    """
    
    def __init__(self):
        self.programacion_original = None
        self.programacion_limpia = None
        self.ruta_data = self._ObtenerRutaData()
    
    def _ObtenerRutaData(self):
        """Obtiene la ruta correcta del directorio data"""
        ruta_actual = os.path.dirname(os.path.abspath(__file__))  # helpers
        ruta_proyecto = os.path.dirname(ruta_actual)  # proyecto raíz
        return os.path.join(ruta_proyecto, "data")
    
    def _ObtenerRutaArchivo(self, nombre_archivo):
        """Obtiene la ruta completa de un archivo en el directorio data"""
        return os.path.join(self.ruta_data, nombre_archivo)
    
    def VerificarProgramacionExistente(self):
        """
        Verifica si existe una programación guardada y la carga
        
        Returns:
            tuple: (existe, datos, mensaje)
        """
        ruta_programacion = self._ObtenerRutaArchivo("programacionLimpiaActual.xlsx")
        
        if os.path.exists(ruta_programacion):
            try:
                df = pd.read_excel(ruta_programacion)
                self.programacion_limpia = df
                
                mensaje = f"✅ Programación cargada automáticamente: {len(df)} registros procesados"
                return True, df, mensaje
                
            except Exception as e:
                return False, None, f"Error al cargar programación existente: {str(e)}"
        
        return False, None, "❌ No hay archivo cargado"
    
    def CargarYProcesarArchivo(self, ruta_archivo):
        """
        Carga y procesa un archivo de programación
        
        Args:
            ruta_archivo (str): Ruta al archivo a procesar
            
        Returns:
            tuple: (exito, datos_procesados, mensaje)
        """
        try:
            # Cargar archivo según extensión
            if ruta_archivo.endswith('.csv'):
                df = pd.read_csv(ruta_archivo, encoding='utf-8')
            else:
                df = pd.read_excel(ruta_archivo)
            
            # Verificar columnas requeridas
            resultado_validacion = self._ValidarColumnas(df)
            if not resultado_validacion[0]:
                return False, None, resultado_validacion[1]
            
            # Guardar original
            self.programacion_original = df
            
            # Limpiar y procesar
            programacion_limpia = LimpiarProgramacion(df)
            self.programacion_limpia = programacion_limpia
            
            # Guardar automáticamente
            resultado_guardado = self._GuardarProgramacionLimpia(programacion_limpia)
            if not resultado_guardado[0]:
                return False, None, resultado_guardado[1]
            
            mensaje = f"✅ Archivo procesado exitosamente: {len(programacion_limpia)} registros listos"
            return True, programacion_limpia, mensaje
            
        except Exception as e:
            return False, None, f"Error al cargar archivo: {str(e)}"
    
    def _ValidarColumnas(self, df):
        """
        Valida que el DataFrame tenga las columnas requeridas
        
        Args:
            df: DataFrame a validar
            
        Returns:
            tuple: (es_valido, mensaje)
        """
        columnas_requeridas = ['nroidenti', 'profesor', 'aula']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            mensaje = f"El archivo debe contener las columnas: {', '.join(columnas_faltantes)}"
            return False, mensaje
        
        return True, "Columnas válidas"
    
    def _GuardarProgramacionLimpia(self, programacion_limpia):
        """
        Guarda la programación limpia en el archivo de trabajo
        
        Args:
            programacion_limpia: DataFrame con datos procesados
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            ruta_guardado = self._ObtenerRutaArchivo("programacionLimpiaActual.xlsx")
            os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
            programacion_limpia.to_excel(ruta_guardado, index=False)
            
            return True, "Programación guardada exitosamente"
            
        except Exception as e:
            return False, f"Error al guardar programación: {str(e)}"
    
    def ExportarProgramacion(self, ruta_destino):
        """
        Exporta la programación actual a un archivo específico
        
        Args:
            ruta_destino (str): Ruta donde guardar el archivo
            
        Returns:
            tuple: (exito, mensaje)
        """
        if self.programacion_limpia is None or self.programacion_limpia.empty:
            return False, "No hay programación cargada para exportar"
        
        try:
            self.programacion_limpia.to_excel(ruta_destino, index=False)
            total_registros = len(self.programacion_limpia)
            
            mensaje = (f"📊 Programación exportada correctamente\n\n"
                      f"📁 Archivo: {os.path.basename(ruta_destino)}\n"
                      f"📍 Ubicación: {os.path.dirname(ruta_destino)}\n"
                      f"🔢 Registros exportados: {total_registros}")
            
            return True, mensaje
            
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"
    
    def ObtenerEstadisticas(self):
        """
        Obtiene estadísticas de la programación cargada
        
        Returns:
            dict: Estadísticas o None si no hay datos
        """
        if self.programacion_limpia is None or self.programacion_limpia.empty:
            return None
        
        df = self.programacion_limpia
        
        estadisticas = {
            'total_registros': len(df),
            'total_docentes': df['Docente'].nunique() if 'Docente' in df.columns else 0,
            'total_aulas': df['Aula'].nunique() if 'Aula' in df.columns else 0,
            'dias_semana': df['Día'].nunique() if 'Día' in df.columns else 0,
            'tiene_datos': True
        }
        
        return estadisticas
    
    def ObtenerProgramacionActual(self):
        """
        Retorna la programación limpia actual
        
        Returns:
            DataFrame o None
        """
        return self.programacion_limpia
    
    def GenerarNombreArchivoExportacion(self):
        """
        Genera un nombre sugerido para el archivo de exportación
        
        Returns:
            str: Nombre del archivo con timestamp
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"programacionLimpia_{timestamp}.xlsx"