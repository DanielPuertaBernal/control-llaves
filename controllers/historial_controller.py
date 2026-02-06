"""
Controlador para la gestión de historial de llaves
Maneja la lógica de negocio de consultas y reportes
"""
from application.services.historial_service import HistorialService


class HistorialController:
    """Controlador para gestionar historial de préstamos"""
    
    def __init__(self, historial_service: HistorialService):
        self.service = historial_service
    
    def obtener_historial_completo(self):
        """
        Obtiene el historial completo de préstamos
        
        Returns:
            pd.DataFrame: Historial completo
        """
        return self.service.obtener_historial_completo()
    
    def obtener_prestamos_activos(self):
        """
        Obtiene solo los préstamos activos (llaves no devueltas)
        
        Returns:
            list: Lista de préstamos activos
        """
        return self.service.obtener_prestamos_activos()
    
    def buscar_en_historial(self, termino, historial_df=None):
        """
        Busca en el historial por término
        
        Args:
            termino (str): Término de búsqueda
            historial_df: DataFrame del historial (opcional)
        
        Returns:
            pd.DataFrame: Resultados filtrados
        """
        return self.service.buscar_en_historial(termino, historial_df)
    
    def filtrar_por_estado(self, estado, historial_df=None):
        """
        Filtra el historial por estado
        
        Args:
            estado (str): Estado a filtrar ('En Préstamo', 'Devuelta', etc.)
            historial_df: DataFrame del historial (opcional)
        
        Returns:
            pd.DataFrame: Historial filtrado
        """
        return self.service.filtrar_por_estado(estado, historial_df)
    
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
        return self.service.filtrar_por_fecha(fecha_inicio, fecha_fin, historial_df)

    def filtrar_historial(self, fecha_inicio=None, fecha_fin=None, facultad=None, docente=None, historial_df=None):
        """Filtra historial por fecha, facultad y/o docente"""
        return self.service.filtrar_historial(fecha_inicio, fecha_fin, facultad, docente, historial_df)

    def obtener_estadisticas_avanzadas(self, historial_df=None):
        """Obtiene estadísticas avanzadas para analítica"""
        return self.service.obtener_estadisticas_avanzadas(historial_df)

    def obtener_facultades(self, historial_df=None):
        """Obtiene lista de facultades disponibles"""
        return self.service.obtener_facultades(historial_df)

    def obtener_docentes_en_historial(self, historial_df=None):
        """Obtiene lista de docentes disponibles en el historial de prestamos"""
        return self.service.obtener_docentes_en_historial(historial_df)

    def exportar_excel(self, historial_df, ruta_guardado: str):
        """Exporta el DataFrame a Excel"""
        return self.service.exportar_excel(historial_df, ruta_guardado)
