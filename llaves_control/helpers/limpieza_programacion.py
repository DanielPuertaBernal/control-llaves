import pandas as pd
from datetime import datetime
import os

def limpiar_programacion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y consolida la programación académica, unificando clases largas
    que están divididas en múltiples registros
    """
    # Limpiar datos básicos
    df['horario'] = df['horario'].astype(str)
    df['profesor'] = df['profesor'].fillna('').str.strip()
    # Convertir nroidenti a string y limpiar formato
    df['nroidenti'] = pd.to_numeric(df['nroidenti'], errors='coerce').fillna(0).astype(int).astype(str)
    df['dia'] = df['dia'].str.upper().str.strip()
    
    # Limpiar nombres de materias
    if 'MATERIA' in df.columns:
        df['materia'] = df['MATERIA'].fillna('').str.strip()
    elif 'materia' not in df.columns:
        df['materia'] = df.get('materia', '').fillna('').str.strip()

    # Separar hora inicio y fin con diferentes formatos posibles
    if ' A ' in df['horario'].iloc[0].upper():
        df[['hora_ini', 'hora_fin']] = df['horario'].str.upper().str.split(' A ', expand=True)
    else:
        df[['hora_ini', 'hora_fin']] = df['horario'].str.split(' a ', expand=True)
    
    # Convertir horas a formato time
    df['hora_ini'] = pd.to_datetime(df['hora_ini'], format='%H:%M', errors='coerce').dt.time
    df['hora_fin'] = pd.to_datetime(df['hora_fin'], format='%H:%M', errors='coerce').dt.time

    # Agrupar por clase con misma información para unificar franjas horarias
    columnas_agrupacion = ['nroidenti', 'profesor', 'materia', 'aula', 'dia']
    
    # Verificar que todas las columnas existan
    columnas_disponibles = [col for col in columnas_agrupacion if col in df.columns]
    
    agrupado = df.groupby(columnas_disponibles).agg({
        'hora_ini': 'min',
        'hora_fin': 'max',
        'nro_estudiantes': 'first',  # Tomar el primer valor, no sumar
        **{col: 'first' for col in ['grupo', 'nivel_grupo', 'semestre', 'PROGRAMA'] if col in df.columns}
    }).reset_index()

    # Reconstruir columna horario
    agrupado['horario'] = agrupado['hora_ini'].astype(str) + ' a ' + agrupado['hora_fin'].astype(str)
    
    return agrupado

def guardar_programacion_limpia(df_original: pd.DataFrame, ruta_salida: str = None) -> str:
    """
    Limpia la programación y guarda el archivo corregido
    """
    if ruta_salida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = f"data/programacion_limpia_{timestamp}.xlsx"
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    # Limpiar programación
    df_limpio = limpiar_programacion(df_original)
    
    # Guardar archivo limpio
    df_limpio.to_excel(ruta_salida, index=False)
    
    return ruta_salida
