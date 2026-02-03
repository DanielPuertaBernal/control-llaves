"""Importador de Excel/CSV para docentes"""
import pandas as pd


def cargar_docentes_desde_archivo(ruta_archivo: str) -> pd.DataFrame:
    if ruta_archivo.endswith('.csv'):
        return pd.read_csv(ruta_archivo, encoding='utf-8')
    if ruta_archivo.endswith('.ods'):
        return pd.read_excel(ruta_archivo, engine='odf')
    if ruta_archivo.endswith('.xls'):
        return pd.read_excel(ruta_archivo, engine='xlrd')

    try:
        return pd.read_excel(ruta_archivo, engine='openpyxl')
    except Exception:
        try:
            return pd.read_excel(ruta_archivo, engine='xlrd')
        except Exception:
            return pd.read_excel(ruta_archivo, engine='odf')
