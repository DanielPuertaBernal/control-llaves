from datetime import datetime
import pandas as pd
import os

RUTA_REGISTRO = 'data/registros_llaves.xlsx'

def inicializar_registro():
    if not os.path.exists(RUTA_REGISTRO):
        df = pd.DataFrame(columns=[
            'nroidenti', 'profesor', 'materia', 'aula',
            'dia', 'horario', 'estado', 'hora_entrega', 'hora_devolucion'
        ])
        df.to_excel(RUTA_REGISTRO, index=False)

def registrar_entrega(info_clase):
    df = pd.read_excel(RUTA_REGISTRO)
    nueva = {
        **info_clase,
        'estado': 'Entregada',
        'hora_entrega': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'hora_devolucion': ''
    }
    df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
    df.to_excel(RUTA_REGISTRO, index=False)

def registrar_devolucion(nroidenti, materia, aula):
    df = pd.read_excel(RUTA_REGISTRO)
    idx = (df['nroidenti'] == nroidenti) & (df['materia'] == materia) & (df['aula'] == aula) & (df['estado'] == 'Entregada')
    df.loc[idx, 'estado'] = 'Devuelta'
    df.loc[idx, 'hora_devolucion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.to_excel(RUTA_REGISTRO, index=False)

def filtrar_llaves(estado=None):
    df = pd.read_excel(RUTA_REGISTRO)
    if estado:
        return df[df['estado'] == estado]
    return df
