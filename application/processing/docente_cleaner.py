"""Limpieza de datos de docentes"""
import pandas as pd
import re


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['Numero de documento'].notna()]
    df['Numero de documento'] = df['Numero de documento'].astype(str).str.replace('.0', '', regex=False)

    if 'Id Carnet' in df.columns:
        df['Id Carnet'] = df['Id Carnet'].apply(normalizar_carnet)
        df['Id Carnet'] = df['Id Carnet'].apply(lambda v: None if v == '' else v)

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()

    df = df.drop_duplicates(subset=['Numero de documento'], keep='first')
    return df


def normalizar_carnet(valor):
    try:
        if pd.isna(valor):
            return ''
        s = str(valor).strip().upper()
        if s.endswith('.0'):
            s = s[:-2]
        s = re.sub(r'[^0-9A-Z]', '', s)
        return s
    except Exception:
        return str(valor)
