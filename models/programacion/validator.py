"""
Validador de programación académica
Responsabilidad: Validar estructura y datos de la programación
"""
import pandas as pd


class ProgramacionValidator:
    """Validador de datos de programación académica"""
    
    COLUMNAS_REQUERIDAS = ['nroidenti', 'profesor', 'aula']
    
    @staticmethod
    def validar_columnas(df: pd.DataFrame) -> bool:
        """
        Valida que el DataFrame tenga las columnas requeridas
        
        Args:
            df: DataFrame a validar
            
        Returns:
            bool: True si tiene todas las columnas requeridas
        """
        return all(col in df.columns for col in ProgramacionValidator.COLUMNAS_REQUERIDAS)
    
    @staticmethod
    def validar_formato_horario(horario: str) -> bool:
        """
        Valida que el horario tenga el formato correcto "HH:MM A HH:MM"
        
        Args:
            horario: String con el horario
            
        Returns:
            bool: True si el formato es válido
        """
        if not horario or not isinstance(horario, str):
            return False
        
        horario_upper = horario.upper()
        return ' A ' in horario_upper or ' a ' in horario
    
    @staticmethod
    def validar_dataframe(df: pd.DataFrame) -> tuple[bool, str]:
        """
        Valida el DataFrame completo
        
        Args:
            df: DataFrame a validar
            
        Returns:
            tuple: (es_valido, mensaje_error)
        """
        if df is None or df.empty:
            return False, "El DataFrame está vacío"
        
        if not ProgramacionValidator.validar_columnas(df):
            columnas_faltantes = [
                col for col in ProgramacionValidator.COLUMNAS_REQUERIDAS 
                if col not in df.columns
            ]
            return False, f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}"
        
        return True, ""
