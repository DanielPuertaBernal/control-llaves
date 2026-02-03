"""Importador de Excel/CSV para programación"""
import pandas as pd


def cargar_programacion_desde_archivo(ruta_archivo: str) -> pd.DataFrame:
    if ruta_archivo.endswith('.csv'):
        return pd.read_csv(ruta_archivo, encoding='utf-8')
    return pd.read_excel(ruta_archivo)
