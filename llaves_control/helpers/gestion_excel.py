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
            'dia', 'horario', 'nro_estudiantes',
            'fecha_entrega', 'hora_entrega', 'fecha_devolucion', 'hora_devolucion',
            'estado', 'observaciones'
        ])
        df.to_excel(RUTA_REGISTRO, index=False)

def limpiar_numero_documento(doc):
    """Limpia el número de documento eliminando .0 si existe"""
    doc_str = str(doc)
    if doc_str.endswith('.0'):
        return doc_str[:-2]
    return doc_str

def registrar_entrega(info_clase):
    """Registra la entrega de una llave con persistencia completa"""
    try:
        # Verificar si el archivo existe, si no crearlo
        if not os.path.exists(RUTA_REGISTRO):
            inicializar_registro()
        
        # Leer archivo existente
        try:
            df = pd.read_excel(RUTA_REGISTRO)
        except:
            # Si falla, crear uno nuevo
            inicializar_registro()
            df = pd.read_excel(RUTA_REGISTRO)
        
        # Limpiar el número de documento
        nroidenti_limpio = limpiar_numero_documento(info_clase['nroidenti'])
        
        # Verificar si ya tiene una llave prestada
        prestada_existente = df[
            (df['nroidenti'].astype(str) == nroidenti_limpio) & 
            (df['estado'] == 'Entregada')
        ]
        
        if not prestada_existente.empty:
            return False  # Ya tiene una llave prestada
        
        # Preparar nuevo registro
        ahora = datetime.now()
        nuevo_registro = {
            'nroidenti': nroidenti_limpio,
            'profesor': info_clase.get('profesor', ''),
            'materia': info_clase.get('materia', ''),
            'aula': info_clase.get('aula', ''),
            'dia': info_clase.get('dia', ''),
            'horario': info_clase.get('horario', ''),
            'nro_estudiantes': info_clase.get('nro_estudiantes', 0),
            'fecha_entrega': ahora.strftime('%Y-%m-%d'),
            'hora_entrega': ahora.strftime('%H:%M:%S'),
            'fecha_devolucion': '',
            'hora_devolucion': '',
            'estado': 'Entregada',
            'observaciones': ''
        }
        
        # Agregar registro
        df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        
        # Guardar con manejo de errores
        try:
            df.to_excel(RUTA_REGISTRO, index=False)
            return True
        except Exception as e:
            print(f"Error al guardar registro: {e}")
            return False
            
    except Exception as e:
        print(f"Error general en registrar_entrega: {e}")
        return False

def registrar_devolucion(nroidenti):
    """Registra la devolución de una llave por número de documento"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            return False
            
        df = pd.read_excel(RUTA_REGISTRO)
        
        # Limpiar el número de documento
        nroidenti_limpio = limpiar_numero_documento(nroidenti)
        
        # Buscar la llave entregada más reciente para este documento
        mask = (
            (df['nroidenti'].astype(str) == nroidenti_limpio) & 
            (df['estado'] == 'Entregada')
        )
        
        if mask.any():
            # Obtener el índice de la entrega más reciente
            registros_entregados = df[mask]
            ultimo_indice = registros_entregados.index[-1]
            
            # Actualizar registro
            ahora = datetime.now()
            df.loc[ultimo_indice, 'estado'] = 'Devuelta'
            df.loc[ultimo_indice, 'fecha_devolucion'] = ahora.strftime('%Y-%m-%d')
            df.loc[ultimo_indice, 'hora_devolucion'] = ahora.strftime('%H:%M:%S')
            
            # Guardar
            df.to_excel(RUTA_REGISTRO, index=False)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error al registrar devolución: {e}")
        return False

def obtener_llaves_pendientes():
    """Obtiene todas las llaves que están entregadas (pendientes de devolución)"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            return pd.DataFrame()
            
        df = pd.read_excel(RUTA_REGISTRO)
        
        # Filtrar solo las entregadas
        pendientes = df[df['estado'] == 'Entregada']
        
        # Limpiar números de documento
        if not pendientes.empty:
            pendientes = pendientes.copy()
            pendientes['nroidenti'] = pendientes['nroidenti'].apply(limpiar_numero_documento)
        
        return pendientes
        
    except Exception as e:
        print(f"Error al obtener llaves pendientes: {e}")
        return pd.DataFrame()

def obtener_historial_completo():
    """Obtiene el historial completo de entregas y devoluciones"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            return pd.DataFrame()
            
        df = pd.read_excel(RUTA_REGISTRO)
        
        # Limpiar números de documento
        if not df.empty:
            df = df.copy()
            df['nroidenti'] = df['nroidenti'].apply(limpiar_numero_documento)
        
        return df
        
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return pd.DataFrame()

def verificar_llave_entregada(nroidenti):
    """Verifica si un profesor ya tiene una llave entregada"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            return False
            
        df = pd.read_excel(RUTA_REGISTRO)
        
        # Limpiar el número de documento
        nroidenti_limpio = limpiar_numero_documento(nroidenti)
        
        # Verificar si tiene llaves entregadas
        mask = (
            (df['nroidenti'].astype(str) == nroidenti_limpio) & 
            (df['estado'] == 'Entregada')
        )
        
        return mask.any()
        
    except Exception as e:
        print(f"Error al verificar llave entregada: {e}")
        return False

def generar_respaldo():
    """Genera un respaldo del archivo de registros"""
    try:
        if os.path.exists(RUTA_REGISTRO):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ruta_respaldo = f'data/respaldo_registros_{timestamp}.xlsx'
            
            df = pd.read_excel(RUTA_REGISTRO)
            df.to_excel(ruta_respaldo, index=False)
            
            return ruta_respaldo
        return None
        
    except Exception as e:
        print(f"Error al generar respaldo: {e}")
        return None
