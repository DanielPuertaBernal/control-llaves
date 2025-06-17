import pandas as pd

def limpiar_programacion(df: pd.DataFrame) -> pd.DataFrame:
    df['horario'] = df['horario'].astype(str)
    df['profesor'] = df['profesor'].fillna('').str.strip()
    df['nroidenti'] = df['nroidenti'].astype(str).str.strip()
    df['dia'] = df['dia'].str.lower().str.strip()

    # Separar hora inicio y fin
    df[['hora_ini', 'hora_fin']] = df['horario'].str.split(' a ', expand=True)
    df['hora_ini'] = pd.to_datetime(df['hora_ini'], errors='coerce').dt.time
    df['hora_fin'] = pd.to_datetime(df['hora_fin'], errors='coerce').dt.time

    # Agrupar por clase con misma info para unificar franjas
    agrupado = df.groupby([
        'nroidenti', 'profesor', 'materia', 'aula', 'dia'
    ]).agg({
        'hora_ini': 'min',
        'hora_fin': 'max',
        'nro_estudiantes': 'sum',
        'grupo': 'first',
        'nivel_grupo': 'first'
    }).reset_index()

    # Reconstruir columna horario
    agrupado['horario'] = agrupado['hora_ini'].astype(str) + ' a ' + agrupado['hora_fin'].astype(str)
    return agrupado
