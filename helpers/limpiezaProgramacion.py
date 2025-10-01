import pandas as pd
from datetime import datetime
import os

# Obtener la ruta del directorio llaves_control
def ObtenerRutaData():
    """Obtiene la ruta correcta del directorio data dentro de llaves_control"""
    ruta_actual = os.path.dirname(os.path.abspath(__file__))  # helpers
    ruta_llaves_control = os.path.dirname(ruta_actual)  # llaves_control
    return os.path.join(ruta_llaves_control, "data")

def ObtenerRutaArchivo(nombre_archivo):
    """Obtiene la ruta completa de un archivo en el directorio data"""
    return os.path.join(ObtenerRutaData(), nombre_archivo)

def RenombrarColumnasExportacion(df):
    """
    Renombra las columnas para la exportación final con nombres descriptivos y buena ortografía
    """
    mapeo_columnas = {
        'semestre': 'Semestre',
        'materia': 'Código de la Materia', 
        'inp': 'INP',
        'grupo': 'Grupo',
        'nivel_grupo': 'Nivel del Grupo',
        'semanas': 'Semanas',
        'nro_horas': 'Número de Horas',
        'fecha_inicio': 'Fecha Inicio',
        'fecha_fin': 'Fecha Fin', 
        'nro_estudiantes_premat': 'Estudiantes Prematriculados',
        'nro_estudiantes': 'Estudiantes Matriculados',
        'total_estudiantes': 'Total de Estudiantes',
        'Total Estudiantes': 'Total de Estudiantes',
        'TOTAL': 'Total de Estudiantes',
        'nroidenti': 'Número de Documento',
        'profesor': 'Docente',
        'dia': 'Día',
        'hora_ini': 'Hora Inicio',
        'hora_fin': 'Hora Fin',
        'horario': 'Horario',
        'aula': 'Aula',
        'Facultad': 'Facultad',
        'PROGRAMA': 'Facultad',
        'descripcion': 'Facultad',
        'Materia de la clase': 'Materia de la Clase',
        'MATERIA': 'Materia de la Clase',
        'descripcion.1': 'Materia de la Clase'
    }
    
    # Lista de columnas a eliminar porque causan problemas o son duplicadas
    # NOTA: Ya no eliminamos descripcion.1 porque la necesitamos
    columnas_a_eliminar = []
    
    # Crear DataFrame con columnas renombradas
    df_renamed = df.copy()
    
    # Eliminar columnas problemáticas PRIMERO
    for col_eliminar in columnas_a_eliminar:
        if col_eliminar in df_renamed.columns:
            df_renamed.drop(columns=[col_eliminar], inplace=True)
    
    # Renombrar columnas que existan
    for col_original, col_nuevo in mapeo_columnas.items():
        if col_original in df_renamed.columns:
            df_renamed.rename(columns={col_original: col_nuevo}, inplace=True)
    
    # IMPORTANTE: Eliminar columnas duplicadas que puedan causar conflictos
    # Si hay múltiples columnas de total, conservar solo una
    if 'Total de Estudiantes' in df_renamed.columns:
        # Si hay duplicados de esta columna, eliminar los extras
        cols_totales = [col for col in df_renamed.columns if col == 'Total de Estudiantes']
        if len(cols_totales) > 1:
            # Mantener solo la primera y eliminar las demás
            indices_duplicados = []
            primera_encontrada = False
            for i, col in enumerate(df_renamed.columns):
                if col == 'Total de Estudiantes':
                    if primera_encontrada:
                        indices_duplicados.append(i)
                    else:
                        primera_encontrada = True
            # Eliminar columnas duplicadas por índice
            df_renamed = df_renamed.iloc[:, [i for i in range(len(df_renamed.columns)) if i not in indices_duplicados]]
    
    # Agregar columna de observaciones si no existe
    if 'Observaciones' not in df_renamed.columns:
        df_renamed['Observaciones'] = ''
    
    # Definir orden de columnas deseado (sin las columnas que se deben ocultar)
    orden_columnas = [
        'Código de la Materia', 'Grupo', 'Nivel del Grupo', 
        'Estudiantes Prematriculados', 'Estudiantes Matriculados', 'Total de Estudiantes',
        'Número de Documento', 'Docente', 'Día', 'Hora Inicio', 'Hora Fin', 'Horario',
        'Aula', 'Facultad', 'Materia de la Clase', 'Observaciones'
    ]
    
    # Reordenar columnas (solo las que existan y no estén en la lista de exclusión)
    columnas_excluidas = ['Semestre', 'INP', 'Semanas', 'Número de Horas', 'Fecha Inicio', 'Fecha Fin']
    columnas_existentes = [col for col in orden_columnas if col in df_renamed.columns]
    columnas_extra = [col for col in df_renamed.columns 
                     if col not in columnas_existentes and col not in columnas_excluidas]
    
    # Combinar columnas en el orden deseado (excluyendo las no deseadas)
    orden_final = columnas_existentes + columnas_extra
    
    return df_renamed[orden_final]

def LimpiarProgramacion(archivo_o_df):
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
            # Intentar leer con pandas primero (más robusto)
            if archivo_o_df.lower().endswith('.xlsx'):
                # Para archivos Excel, usar engine openpyxl con configuraciones robustas
                df = pd.read_excel(archivo_o_df, engine='openpyxl')
            elif archivo_o_df.lower().endswith('.xls'):
                # Para archivos Excel antiguos, usar xlrd
                df = pd.read_excel(archivo_o_df, engine='xlrd')
            else:
                # Para otros formatos
                df = pd.read_excel(archivo_o_df)
                
        except Exception as e:
            print(f"Error al leer archivo Excel con pandas: {e}")
            try:
                # Intentar método alternativo con openpyxl directamente
                import openpyxl
                wb = openpyxl.load_workbook(archivo_o_df, data_only=True)
                ws = wb.active
                data = []
                headers = []
                
                for i, row in enumerate(ws.iter_rows(values_only=True)):
                    if i == 0:
                        headers = [str(cell) if cell is not None else f'Col_{i}' for i, cell in enumerate(row)]
                    else:
                        data.append(row)
                
                df = pd.DataFrame(data, columns=headers)
                wb.close()
                
            except Exception as e2:
                print(f"Error con método alternativo: {e2}")
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

        # --- NUEVO: Procesar datos de estudiantes manteniendo columnas separadas ---
        # Asegurar que existan las columnas base
        if 'nro_estudiantes_premat' not in df.columns:
            df['nro_estudiantes_premat'] = 0
        if 'nro_estudiantes' not in df.columns:
            df['nro_estudiantes'] = 0
            
        # Limpiar valores NaN y convertir a números
        df['nro_estudiantes_premat'] = pd.to_numeric(df['nro_estudiantes_premat'], errors='coerce').fillna(0)
        df['nro_estudiantes'] = pd.to_numeric(df['nro_estudiantes'], errors='coerce').fillna(0)
        
        # SIEMPRE calcular el total sumando prematriculados + matriculados
        df['total_estudiantes'] = df['nro_estudiantes_premat'] + df['nro_estudiantes']
        
        # Si existe columna TOTAL en los datos originales, la ignoramos ya que calculamos nuestro propio total

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
        # IMPORTANTE: Incluir 'grupo' para evitar unificar clases de grupos diferentes
        columnas_agrupacion = ['nroidenti', 'profesor', 'materia', 'aula', 'dia', 'grupo']

        # Verificar que todas las columnas existan
        columnas_disponibles = [col for col in columnas_agrupacion if col in df.columns]
        
        # Solo procesar si tenemos las columnas básicas
        if len(columnas_disponibles) >= 4:  # Al menos nroidenti, profesor, aula, dia
            
            # NUEVA LÓGICA: Evaluar gaps de tiempo antes de unificar
            def evaluar_clases_continuas(grupo_df):
                """
                Evalúa si las clases de un grupo pueden unificarse o deben mantenerse separadas
                basándose en el gap de tiempo entre ellas
                """
                if len(grupo_df) <= 1:
                    return grupo_df
                
                # Ordenar por hora de inicio
                grupo_df = grupo_df.sort_values('hora_ini')
                
                # Convertir horas a datetime para calcular diferencias
                try:
                    from datetime import datetime, timedelta
                    
                    clases_separadas = []
                    clase_actual = [grupo_df.iloc[0]]
                    
                    for i in range(1, len(grupo_df)):
                        fila_anterior = grupo_df.iloc[i-1]
                        fila_actual = grupo_df.iloc[i]
                        
                        # Calcular gap entre fin de clase anterior y inicio de actual
                        if pd.notna(fila_anterior['hora_fin']) and pd.notna(fila_actual['hora_ini']):
                            try:
                                fin_anterior = datetime.combine(datetime.today(), fila_anterior['hora_fin'])
                                inicio_actual = datetime.combine(datetime.today(), fila_actual['hora_ini'])
                                gap = inicio_actual - fin_anterior
                                
                                # Si el gap es mayor a 30 minutos, es una clase separada
                                if gap > timedelta(minutes=30):
                                    # Guardar clase actual como grupo separado
                                    clases_separadas.append(pd.DataFrame(clase_actual))
                                    clase_actual = [fila_actual]
                                else:
                                    # Continuar con la misma clase
                                    clase_actual.append(fila_actual)
                            except:
                                # Si hay error en conversión, mantener separadas
                                clases_separadas.append(pd.DataFrame(clase_actual))
                                clase_actual = [fila_actual]
                        else:
                            clase_actual.append(fila_actual)
                    
                    # Agregar la última clase
                    clases_separadas.append(pd.DataFrame(clase_actual))
                    
                    # Unificar horarios dentro de cada clase continua
                    resultado = []
                    for clase_df in clases_separadas:
                        if len(clase_df) > 1:
                            # Unificar horarios de esta clase continua
                            clase_unificada = clase_df.iloc[0].copy()
                            clase_unificada['hora_ini'] = clase_df['hora_ini'].min()
                            clase_unificada['hora_fin'] = clase_df['hora_fin'].max()
                            resultado.append(clase_unificada)
                        else:
                            resultado.append(clase_df.iloc[0])
                    
                    return pd.DataFrame(resultado)
                    
                except Exception as e:
                    print(f"Error evaluando clases continuas: {e}")
                    return grupo_df
            
            # Aplicar la nueva lógica grupo por grupo
            if 'hora_ini' in df.columns and 'hora_fin' in df.columns:
                grupos_procesados = []
                for nombre_grupo, grupo_df in df.groupby(columnas_disponibles):
                    grupo_procesado = evaluar_clases_continuas(grupo_df)
                    grupos_procesados.append(grupo_procesado)
                
                # Combinar todos los grupos procesados
                if grupos_procesados:
                    agrupado = pd.concat(grupos_procesados, ignore_index=True)
                    
                    # Reconstruir columna horario
                    agrupado['horario'] = agrupado['hora_ini'].astype(str) + ' a ' + agrupado['hora_fin'].astype(str)
                    
                    # Aplicar renombrado de columnas para exportación
                    return RenombrarColumnasExportacion(agrupado)
            
            # LÓGICA FALLBACK: Si no se puede evaluar gaps, usar método original
            # Preparar diccionario de agregación dinámicamente
            agg_dict = {}
            
            # Agregar columnas de hora si existen
            if 'hora_ini' in df.columns:
                agg_dict['hora_ini'] = 'min'
            if 'hora_fin' in df.columns:
                agg_dict['hora_fin'] = 'max'
            
            # Agregar columnas de estudiantes si existen
            for col_estudiantes in ['nro_estudiantes_premat', 'nro_estudiantes', 'total_estudiantes']:
                if col_estudiantes in df.columns:
                    agg_dict[col_estudiantes] = 'first'
            
            # Agregar otras columnas opcionales (grupo ya está en columnas_agrupacion)
            for col in ['nivel_grupo', 'semestre', 'PROGRAMA']:
                if col in df.columns:
                    agg_dict[col] = 'first'
            
            if agg_dict:  # Solo agrupar si tenemos algo que agregar
                agrupado = df.groupby(columnas_disponibles).agg(agg_dict).reset_index()
                
                # Reconstruir columna horario si tenemos hora_ini y hora_fin
                if 'hora_ini' in agrupado.columns and 'hora_fin' in agrupado.columns:
                    agrupado['horario'] = agrupado['hora_ini'].astype(str) + ' a ' + agrupado['hora_fin'].astype(str)
                
                # Aplicar renombrado de columnas para exportación
                return RenombrarColumnasExportacion(agrupado)
            else:
                # Si no podemos agrupar, aplicar renombrado básico
                return RenombrarColumnasExportacion(df)
        else:
            # Si no podemos agrupar, devolver el DataFrame con columnas renombradas
            return RenombrarColumnasExportacion(df)
            
    except Exception as e:
        print(f"Error al procesar programación: {e}")
        return df  # Devolver datos básicos si falla el procesamiento avanzado

def GuardarProgramacionLimpia(df_original: pd.DataFrame, ruta_salida: str = None) -> str:
    """
    Limpia la programación y guarda el archivo corregido
    """
    if ruta_salida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = ObtenerRutaArchivo(f"programacionLimpia_{timestamp}.xlsx")
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    # Limpiar y guardar
    df_limpio = LimpiarProgramacion(df_original)
    
    # Guardar con configuraciones robustas para evitar advertencias
    try:
        with pd.ExcelWriter(ruta_salida, engine='openpyxl', mode='w') as writer:
            df_limpio.to_excel(writer, index=False, sheet_name='Programacion')
        print(f"Programación guardada exitosamente en: {ruta_salida}")
    except Exception as e:
        print(f"Error al guardar programación: {e}")
        # Intentar método alternativo
        try:
            df_limpio.to_excel(ruta_salida, index=False)
            print(f"Programación guardada con método alternativo en: {ruta_salida}")
        except Exception as e2:
            print(f"Error con método alternativo: {e2}")
            return ""
    
    return ruta_salida

def GuardarProgramacionActual(df_limpio: pd.DataFrame, ruta_base: str = "data") -> str:
    """
    Guarda la programación limpia como la versión actual para cargas posteriores
    """
    ruta_actual = os.path.join(ruta_base, "programacionLimpiaActual.xlsx")
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(ruta_actual), exist_ok=True)
    
    # Guardar como versión actual con configuraciones robustas
    try:
        with pd.ExcelWriter(ruta_actual, engine='openpyxl', mode='w') as writer:
            df_limpio.to_excel(writer, index=False, sheet_name='Programacion')
        print(f"Programación actual guardada exitosamente en: {ruta_actual}")
    except Exception as e:
        print(f"Error al guardar programación actual: {e}")
        # Intentar método alternativo
        try:
            df_limpio.to_excel(ruta_actual, index=False)
            print(f"Programación actual guardada con método alternativo")
        except Exception as e2:
            print(f"Error con método alternativo: {e2}")
            return ""
    
    return ruta_actual

def VerificarProgramacionGuardada(ruta_base: str = "data") -> str:
    """
    Verifica si existe una programación limpia guardada previamente
    """
    ruta_actual = os.path.join(ruta_base, "programacionLimpiaActual.xlsx")
    return ruta_actual if os.path.exists(ruta_actual) else None
