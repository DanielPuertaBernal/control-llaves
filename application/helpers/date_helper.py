"""
Helper para manejo de fechas
Conversiones, validaciones y utilidades para trabajar con fechas
"""
from datetime import datetime
from typing import Optional
import pandas as pd


class DateHelper:
    """Utilidades para manejo y validación de fechas"""
    
    DATE_FORMAT = '%Y-%m-%d'
    
    @staticmethod
    def validar_formato(fecha_str: str, formato: str = None) -> bool:
        """
        Valida si una fecha tiene el formato correcto
        
        Args:
            fecha_str: String de fecha a validar
            formato: Formato esperado (default: YYYY-MM-DD)
            
        Returns:
            True si es válida, False si no
        """
        if not fecha_str or not fecha_str.strip():
            return True  # Fecha vacía es válida (opcional)
        
        formato = formato or DateHelper.DATE_FORMAT
        
        try:
            datetime.strptime(fecha_str.strip(), formato)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def to_datetime(fecha_str: str) -> Optional[datetime]:
        """
        Convierte string a datetime
        
        Args:
            fecha_str: String de fecha en formato YYYY-MM-DD
            
        Returns:
            Objeto datetime o None si es inválido
        """
        if not fecha_str or not fecha_str.strip():
            return None
        
        try:
            return datetime.strptime(fecha_str.strip(), DateHelper.DATE_FORMAT)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def to_string(fecha_dt: datetime, formato: str = None) -> str:
        """
        Convierte datetime a string
        
        Args:
            fecha_dt: Objeto datetime
            formato: Formato de salida (default: YYYY-MM-DD)
            
        Returns:
            String formateado
        """
        if fecha_dt is None:
            return ""
        
        formato = formato or DateHelper.DATE_FORMAT
        
        try:
            return fecha_dt.strftime(formato)
        except (ValueError, TypeError, AttributeError):
            return ""
    
    @staticmethod
    def filtrar_por_rango(
        df: pd.DataFrame,
        columna_fecha: str,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filtra un DataFrame por rango de fechas
        
        Args:
            df: DataFrame a filtrar
            columna_fecha: Nombre de la columna con fechas
            fecha_inicio: Fecha inicial (YYYY-MM-DD) o None
            fecha_fin: Fecha final (YYYY-MM-DD) o None
            
        Returns:
            DataFrame filtrado
        """
        if df.empty or columna_fecha not in df.columns:
            return df
        
        if not fecha_inicio and not fecha_fin:
            return df
        
        resultado = df.copy()
        
        try:
            # Convertir columna a datetime
            resultado['_fecha_temp'] = pd.to_datetime(
                resultado[columna_fecha], 
                errors='coerce'
            )
            
            # Aplicar filtro de fecha inicio
            if fecha_inicio:
                fecha_inicio_dt = pd.to_datetime(fecha_inicio)
                resultado = resultado[resultado['_fecha_temp'] >= fecha_inicio_dt]
            
            # Aplicar filtro de fecha fin
            if fecha_fin:
                fecha_fin_dt = pd.to_datetime(fecha_fin)
                resultado = resultado[resultado['_fecha_temp'] <= fecha_fin_dt]
            
            # Eliminar columna temporal
            resultado = resultado.drop('_fecha_temp', axis=1)
            
            return resultado
            
        except Exception as e:
            print(f"Error al filtrar por fechas: {e}")
            return df
    
    @staticmethod
    def hoy() -> str:
        """
        Retorna la fecha actual en formato YYYY-MM-DD
        
        Returns:
            String con fecha actual
        """
        return datetime.now().strftime(DateHelper.DATE_FORMAT)
