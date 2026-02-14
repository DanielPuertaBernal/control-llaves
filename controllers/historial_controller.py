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

    def exportar_excel(self, historial_df, ruta_guardado: str):
        """Exporta el DataFrame a Excel"""
        return self.service.exportar_excel(historial_df, ruta_guardado)
