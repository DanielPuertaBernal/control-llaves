from datetime import datetime
import pandas as pd
import os

RUTA_REGISTRO = 'data/registros_llaves.xlsx'

def inicializar_registro():
    """Inicializa el archivo de registro si no existe"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    if not os.path.exists(RUTA_REGISTRO):
        df = pd.DataFrame(columns=[
            'nroidenti', 'profesor', 'materia', 'aula',
            'dia', 'horario', 'estado', 'hora_entrega', 'hora_devolucion',
            'programa', 'grupo', 'nro_estudiantes'
        ])
        df.to_excel(RUTA_REGISTRO, index=False)

def registrar_entrega(info_clase):
    """Registra la entrega de una llave"""
    try:
        df = pd.read_excel(RUTA_REGISTRO)
    except FileNotFoundError:
        inicializar_registro()
        df = pd.read_excel(RUTA_REGISTRO)
    
    nueva = {
        **info_clase,
        'estado': 'Entregada',
        'hora_entrega': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'hora_devolucion': ''
    }
    df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
    df.to_excel(RUTA_REGISTRO, index=False)
    return True

def registrar_devolucion(nroidenti, materia, aula):
    """Registra la devolución de una llave"""
    try:
        df = pd.read_excel(RUTA_REGISTRO)
        
        # Buscar la llave entregada más reciente
        mask = (
            (df['nroidenti'] == str(nroidenti)) & 
            (df['materia'] == materia) & 
            (df['aula'] == aula) & 
            (df['estado'] == 'Entregada')
        )
        
        if mask.any():
            # Encontrar el índice de la entrega más reciente
            indices = df[mask].index
            ultimo_indice = indices[-1]  # Último registro encontrado
            
            df.loc[ultimo_indice, 'estado'] = 'Devuelta'
            df.loc[ultimo_indice, 'hora_devolucion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.to_excel(RUTA_REGISTRO, index=False)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al registrar devolución: {e}")
        return False

def filtrar_llaves(estado=None):
    """Filtra las llaves por estado"""
    try:
        df = pd.read_excel(RUTA_REGISTRO)
        if estado:
            return df[df['estado'] == estado]
        return df
    except FileNotFoundError:
        inicializar_registro()
        return pd.DataFrame()

def verificar_llave_entregada(nroidenti, materia, aula):
    """Verifica si ya hay una llave entregada para esta clase"""
    try:
        df = pd.read_excel(RUTA_REGISTRO)
        mask = (
            (df['nroidenti'] == str(nroidenti)) & 
            (df['materia'] == materia) & 
            (df['aula'] == aula) & 
            (df['estado'] == 'Entregada')
        )
        return mask.any()
    except:
        return False

def obtener_llaves_pendientes():
    """Obtiene todas las llaves que están entregadas (pendientes de devolución)"""
    return filtrar_llaves('Entregada')
