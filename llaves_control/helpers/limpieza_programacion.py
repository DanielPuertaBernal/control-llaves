import pandas as pd
from datetime import datetime
import os

def limpiar_programacion(archivo_o_df):
    """
    Limpia y consolida la programación académica, unificando clases largas
    que están divididas en múltiples registros.
    
    Args:
        archivo_o_df: Puede ser una ruta de archivo Excel o un DataFrame de pandas
    
    Returns:
        DataFrame limpio y consolidado
    """
    # Verificar si es archivo o DataFrame
    if isinstance(archivo_o_df, str):
        # Es una ruta de archivo
        try:
            df = pd.read_excel(archivo_o_df)
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return pd.DataFrame()
    elif isinstance(archivo_o_df, pd.DataFrame):
        # Es un DataFrame
        df = archivo_o_df.copy()
    else:
        print(f"Tipo no soportado: {type(archivo_o_df)}")
        return pd.DataFrame()
    
    if df.empty:
        return df
    
    try:
        # Limpiar datos básicos
        df['horario'] = df['horario'].astype(str)
        df['profesor'] = df['profesor'].fillna('').str.strip()

        # Convertir nroidenti a string limpio sin .0
        def limpiar_documento(doc):
            doc_str = str(doc)
            if doc_str.endswith('.0'):
                return doc_str[:-2]
            return doc_str
        df['nroidenti'] = df['nroidenti'].apply(limpiar_documento)
        df['dia'] = df['dia'].str.upper().str.strip()

        # Limpiar nombres de materias
        if 'MATERIA' in df.columns:
            df['materia'] = df['MATERIA'].fillna('').str.strip()
        elif 'materia' not in df.columns:
            df['materia'] = df.get('materia', '').fillna('').str.strip()

        # --- NUEVO: Calcular nro_estudiantes ---
        if 'TOTAL' in df.columns:
            df['nro_estudiantes'] = df['TOTAL']
        else:
            premat = df['nro_estudiantes_premat'] if 'nro_estudiantes_premat' in df.columns else 0
            mat = df['nro_estudiantes'] if 'nro_estudiantes' in df.columns else 0
            # Si ambos existen, sumarlos; si solo uno, usar ese
            if isinstance(premat, pd.Series) and isinstance(mat, pd.Series):
                df['nro_estudiantes'] = premat.fillna(0).astype(float) + mat.fillna(0).astype(float)
            elif isinstance(premat, pd.Series):
                df['nro_estudiantes'] = premat.fillna(0).astype(float)
            elif isinstance(mat, pd.Series):
                df['nro_estudiantes'] = mat.fillna(0).astype(float)
            else:
                df['nro_estudiantes'] = 0

        # Separar hora inicio y fin con diferentes formatos posibles
        if len(df) > 0 and ' A ' in str(df['horario'].iloc[0]).upper():
            df[['hora_ini', 'hora_fin']] = df['horario'].str.upper().str.split(' A ', expand=True)
        else:
            # Intentar diferentes separadores
            if ' a ' in str(df['horario'].iloc[0]):
                df[['hora_ini', 'hora_fin']] = df['horario'].str.split(' a ', expand=True)
            elif '-' in str(df['horario'].iloc[0]):
                df[['hora_ini', 'hora_fin']] = df['horario'].str.split('-', expand=True)
            else:
                # Si no hay separador reconocible, usar horario completo
                df['hora_ini'] = df['horario']
                df['hora_fin'] = df['horario']

        # Convertir horas a formato time (con manejo de errores)
        try:
            df['hora_ini'] = pd.to_datetime(df['hora_ini'], format='%H:%M', errors='coerce').dt.time
            df['hora_fin'] = pd.to_datetime(df['hora_fin'], format='%H:%M', errors='coerce').dt.time
        except:
            # Si falla, mantener como string
            pass

        # Agrupar por clase con misma información para unificar franjas horarias
        columnas_agrupacion = ['nroidenti', 'profesor', 'materia', 'aula', 'dia']

        # Verificar que todas las columnas existan
        columnas_disponibles = [col for col in columnas_agrupacion if col in df.columns]
        
        # Solo procesar si tenemos las columnas básicas
        if len(columnas_disponibles) >= 4:  # Al menos nroidenti, profesor, aula, dia
            # Preparar diccionario de agregación dinámicamente
            agg_dict = {}
            
            # Agregar columnas de hora si existen
            if 'hora_ini' in df.columns:
                agg_dict['hora_ini'] = 'min'
            if 'hora_fin' in df.columns:
                agg_dict['hora_fin'] = 'max'
            
            # Agregar columnas opcionales solo si existen
            if 'nro_estudiantes' in df.columns:
                agg_dict['nro_estudiantes'] = 'first'
            
            # Agregar otras columnas opcionales
            for col in ['grupo', 'nivel_grupo', 'semestre', 'PROGRAMA']:
                if col in df.columns:
                    agg_dict[col] = 'first'
            
            if agg_dict:  # Solo agrupar si tenemos algo que agregar
                agrupado = df.groupby(columnas_disponibles).agg(agg_dict).reset_index()
                
                # Reconstruir columna horario si tenemos hora_ini y hora_fin
                if 'hora_ini' in agrupado.columns and 'hora_fin' in agrupado.columns:
                    agrupado['horario'] = agrupado['hora_ini'].astype(str) + ' a ' + agrupado['hora_fin'].astype(str)
                
                return agrupado
            else:
                return df
        else:
            # Si no podemos agrupar, devolver el DataFrame limpio básico
            return df
            
    except Exception as e:
        print(f"Error al procesar programación: {e}")
        return df  # Devolver datos básicos si falla el procesamiento avanzado

def guardar_programacion_limpia(df_original: pd.DataFrame, ruta_salida: str = None) -> str:
    """
    Limpia la programación y guarda el archivo corregido
    """
    if ruta_salida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = f"data/programacion_limpia_{timestamp}.xlsx"
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    # Limpiar y guardar
    df_limpio = limpiar_programacion(df_original)
    df_limpio.to_excel(ruta_salida, index=False)
    
    return ruta_salida

def verificar_programacion_guardada(ruta_base: str = "llaves_control/data") -> str:
    """
    Verifica si existe una programación limpia guardada previamente
    """
    ruta_actual = os.path.join(ruta_base, "programacion_limpia_actual.xlsx")
    return ruta_actual if os.path.exists(ruta_actual) else None

def guardar_programacion_actual(df_limpio: pd.DataFrame, ruta_base: str = "llaves_control/data") -> str:
    """
    Guarda la programación limpia como la versión actual para cargas posteriores
    """
    ruta_actual = os.path.join(ruta_base, "programacion_limpia_actual.xlsx")
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(ruta_actual), exist_ok=True)
    
    # Guardar como versión actual
    df_limpio.to_excel(ruta_actual, index=False)
    
    return ruta_actual
