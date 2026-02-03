"""Validador de programación académica"""
import pandas as pd


class ProgramacionValidator:
    COLUMNAS_REQUERIDAS = ['nroidenti', 'profesor', 'aula']

    @staticmethod
    def validar_columnas(df: pd.DataFrame) -> bool:
        return all(col in df.columns for col in ProgramacionValidator.COLUMNAS_REQUERIDAS)

    @staticmethod
    def validar_formato_horario(horario: str) -> bool:
        if not horario or not isinstance(horario, str):
            return False
        horario_upper = horario.upper()
        return ' A ' in horario_upper or ' a ' in horario

    @staticmethod
    def validar_dataframe(df: pd.DataFrame) -> tuple[bool, str]:
        if df is None or df.empty:
            return False, "El DataFrame está vacío"

        if not ProgramacionValidator.validar_columnas(df):
            columnas_faltantes = [
                col for col in ProgramacionValidator.COLUMNAS_REQUERIDAS
                if col not in df.columns
            ]
            return False, f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}"

        return True, ""
