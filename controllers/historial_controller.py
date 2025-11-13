"""
Controlador para la gestión de historial de llaves
Maneja la lógica de negocio de consultas y reportes
"""
from models import LlaveModel
import pandas as pd


class HistorialController:
    """Controlador para gestionar historial de préstamos"""
    
    def __init__(self):
        self.model = LlaveModel()
    
    def obtener_historial_completo(self):
        """
        Obtiene el historial completo de préstamos
        
        Returns:
            pd.DataFrame: Historial completo
        """
        return self.model.obtener_historial_completo()
    
    def obtener_prestamos_activos(self):
        """
        Obtiene solo los préstamos activos (llaves no devueltas)
        
        Returns:
            list: Lista de préstamos activos
        """
        return self.model.obtener_llaves_pendientes()
    
    def buscar_en_historial(self, termino, historial_df=None):
        """
        Busca en el historial por término
        
        Args:
            termino (str): Término de búsqueda
            historial_df: DataFrame del historial (opcional)
        
        Returns:
            pd.DataFrame: Resultados filtrados
        """
        if historial_df is None:
            historial_df = self.model.obtener_historial_completo()
        
        if historial_df.empty or not termino:
            return historial_df
        
        # Normalizar término
        termino = termino.strip().lower()
        
        # Buscar en múltiples columnas
        mascara_busqueda = pd.Series([False] * len(historial_df))
        
        columnas_busqueda = ['Número de Documento', 'Docente', 'Aula', 'Materia de la Clase']
        
        for columna in columnas_busqueda:
            if columna in historial_df.columns:
                mascara_busqueda |= historial_df[columna].astype(str).str.lower().str.contains(termino, na=False)
        
        return historial_df[mascara_busqueda]
    
    def filtrar_por_estado(self, estado, historial_df=None):
        """
        Filtra el historial por estado
        
        Args:
            estado (str): Estado a filtrar ('En Préstamo', 'Devuelta', etc.)
            historial_df: DataFrame del historial (opcional)
        
        Returns:
            pd.DataFrame: Historial filtrado
        """
        if historial_df is None:
            historial_df = self.model.obtener_historial_completo()
        
        if historial_df.empty or 'Estado' not in historial_df.columns:
            return historial_df
        
        return historial_df[historial_df['Estado'] == estado]
    
    def filtrar_por_fecha(self, fecha_inicio, fecha_fin, historial_df=None):
        """
        Filtra el historial por rango de fechas
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
            historial_df: DataFrame del historial (opcional)
        
        Returns:
            pd.DataFrame: Historial filtrado
        """
        if historial_df is None:
            historial_df = self.model.obtener_historial_completo()
        
        if historial_df.empty or 'Fecha de entrega' not in historial_df.columns:
            return historial_df
        
        try:
            # Convertir fechas a datetime
            historial_df['fecha_temp'] = pd.to_datetime(historial_df['Fecha de entrega'], errors='coerce')
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            fecha_fin_dt = pd.to_datetime(fecha_fin)
            
            # Filtrar
            resultado = historial_df[
                (historial_df['fecha_temp'] >= fecha_inicio_dt) & 
                (historial_df['fecha_temp'] <= fecha_fin_dt)
            ].drop('fecha_temp', axis=1)
            
            return resultado
            
        except Exception as e:
            print(f"Error al filtrar por fecha: {e}")
            return historial_df
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas del historial
        
        Returns:
            dict: Diccionario con estadísticas
        """
        historial = self.model.obtener_historial_completo()
        prestamos_activos = self.model.obtener_llaves_pendientes()
        
        return {
            'total_registros': len(historial),
            'prestamos_activos': len(prestamos_activos),
            'llaves_devueltas': len(historial[historial['Estado'] == 'Devuelta']) if not historial.empty else 0,
            'docentes_unicos': historial['Docente'].nunique() if not historial.empty else 0
        }
