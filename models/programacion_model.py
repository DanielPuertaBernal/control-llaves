"""
Modelo para la gestión de programación académica
Maneja toda la lógica de datos relacionada con la carga y limpieza de programación
"""
import pandas as pd
import os
from datetime import datetime


class ProgramacionModel:
    """Modelo para gestionar la programación académica"""
    
    def __init__(self):
        self.programacion_original = None
        self.programacion_limpia = None
        self.ruta_data = self._obtener_ruta_data()
    
    def _obtener_ruta_data(self):
        """Obtiene la ruta del directorio data"""
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_proyecto = os.path.dirname(ruta_actual)
        return os.path.join(ruta_proyecto, "data")
    
    def cargar_programacion_guardada(self):
        """
        Carga la programación guardada previamente
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        ruta_programacion = os.path.join(self.ruta_data, "programacionLimpiaActual.xlsx")
        
        if os.path.exists(ruta_programacion):
            try:
                df = pd.read_excel(ruta_programacion)
                self.programacion_limpia = df
                mensaje = f"✅ Programación cargada: {len(df)} registros"
                return True, df, mensaje
            except Exception as e:
                return False, None, f"Error al cargar: {str(e)}"
        
        return False, None, "❌ No hay programación guardada"
    
    def cargar_desde_archivo(self, ruta_archivo):
        """
        Carga y procesa un archivo de programación
        
        Args:
            ruta_archivo (str): Ruta al archivo Excel/CSV
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        try:
            # Cargar archivo según extensión
            if ruta_archivo.endswith('.csv'):
                df = pd.read_csv(ruta_archivo, encoding='utf-8')
            else:
                df = pd.read_excel(ruta_archivo)
            
            # Validar columnas requeridas
            if not self._validar_columnas(df):
                return False, None, "❌ El archivo no tiene las columnas requeridas (nroidenti, profesor, aula)"
            
            self.programacion_original = df
            
            # Limpiar programación
            df_limpio = self._limpiar_programacion(df)
            self.programacion_limpia = df_limpio
            
            # Guardar automáticamente
            if not self._guardar_programacion(df_limpio):
                return False, None, "❌ Error al guardar la programación procesada"
            
            mensaje = f"✅ Procesado exitosamente: {len(df_limpio)} registros"
            return True, df_limpio, mensaje
            
        except Exception as e:
            return False, None, f"❌ Error al cargar archivo: {str(e)}"
    
    def obtener_programacion_actual(self):
        """Retorna la programación actualmente cargada"""
        return self.programacion_limpia
    
    def obtener_clases_del_dia(self, dia=None):
        """
        Obtiene las clases de un día específico
        
        Args:
            dia (str): Día de la semana. Si es None, usa el día actual
        
        Returns:
            pd.DataFrame: Clases del día especificado
        """
        if self.programacion_limpia is None or self.programacion_limpia.empty:
            return pd.DataFrame()
        
        if dia is None:
            dia = self._obtener_dia_actual()
        
        try:
            df_dia = self.programacion_limpia[self.programacion_limpia['Día'] == dia].copy()
            return df_dia
        except Exception as e:
            print(f"Error al obtener clases del día: {e}")
            return pd.DataFrame()
    
    def _validar_columnas(self, df):
        """Valida que el DataFrame tenga las columnas requeridas"""
        columnas_requeridas = ['nroidenti', 'profesor', 'aula']
        return all(col in df.columns for col in columnas_requeridas)
    
    def _evaluar_clases_continuas(self, grupo_df):
        """
        Evalúa si las clases de un grupo pueden unificarse o deben mantenerse separadas
        basándose en el gap de tiempo entre ellas
        """
        if len(grupo_df) <= 1:
            return grupo_df
        
        # Ordenar por hora de inicio
        grupo_df = grupo_df.sort_values('hora_ini')
        
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
    
    def _limpiar_programacion(self, df):
        """
        Limpia y consolida la programación académica, unificando clases largas
        que están divididas en múltiples registros.
        
        Args:
            df: DataFrame con programación original
        
        Returns:
            DataFrame limpio y consolidado
        """
        if df.empty:
            return df
        
        try:
            # Crear copia para no modificar el original
            df_limpio = df.copy()
            
            # Normalizar nombres de columnas
            df_limpio.columns = df_limpio.columns.str.strip()
            
            # Limpiar datos básicos
            df_limpio['horario'] = df_limpio['horario'].astype(str) if 'horario' in df_limpio.columns else ''
            df_limpio['profesor'] = df_limpio['profesor'].fillna('').str.strip() if 'profesor' in df_limpio.columns else ''
            
            # Convertir nroidenti a string limpio sin .0
            def limpiar_documento(doc):
                doc_str = str(doc)
                if doc_str.endswith('.0'):
                    return doc_str[:-2]
                return doc_str
            
            if 'nroidenti' in df_limpio.columns:
                df_limpio['nroidenti'] = df_limpio['nroidenti'].apply(limpiar_documento)
            
            if 'dia' in df_limpio.columns:
                df_limpio['dia'] = df_limpio['dia'].str.upper().str.strip()
            
            # Limpiar nombres de materias
            if 'MATERIA' in df_limpio.columns:
                df_limpio['materia'] = df_limpio['MATERIA'].fillna('').str.strip()
            elif 'materia' not in df_limpio.columns:
                df_limpio['materia'] = df_limpio.get('materia', '').fillna('').str.strip()
            
            # Procesar datos de estudiantes
            if 'nro_estudiantes_premat' not in df_limpio.columns:
                df_limpio['nro_estudiantes_premat'] = 0
            if 'nro_estudiantes' not in df_limpio.columns:
                df_limpio['nro_estudiantes'] = 0
            
            df_limpio['nro_estudiantes_premat'] = pd.to_numeric(df_limpio['nro_estudiantes_premat'], errors='coerce').fillna(0)
            df_limpio['nro_estudiantes'] = pd.to_numeric(df_limpio['nro_estudiantes'], errors='coerce').fillna(0)
            df_limpio['total_estudiantes'] = df_limpio['nro_estudiantes_premat'] + df_limpio['nro_estudiantes']
            
            # Separar hora inicio y fin con formato "HH:MM A HH:MM"
            if 'horario' in df_limpio.columns and len(df_limpio) > 0:
                # El formato estándar es siempre con "A" (mayúscula o minúscula)
                horario_ejemplo = str(df_limpio['horario'].iloc[0]).upper()
                
                if ' A ' in horario_ejemplo:
                    df_limpio[['hora_ini', 'hora_fin']] = df_limpio['horario'].str.upper().str.split(' A ', expand=True)
                elif ' a ' in str(df_limpio['horario'].iloc[0]):
                    df_limpio[['hora_ini', 'hora_fin']] = df_limpio['horario'].str.split(' a ', expand=True)
                else:
                    # Si no tiene el formato esperado, usar horario completo
                    df_limpio['hora_ini'] = df_limpio['horario']
                    df_limpio['hora_fin'] = df_limpio['horario']
            
            # Convertir horas a formato time
            try:
                if 'hora_ini' in df_limpio.columns:
                    df_limpio['hora_ini'] = pd.to_datetime(df_limpio['hora_ini'], format='%H:%M', errors='coerce').dt.time
                if 'hora_fin' in df_limpio.columns:
                    df_limpio['hora_fin'] = pd.to_datetime(df_limpio['hora_fin'], format='%H:%M', errors='coerce').dt.time
            except:
                pass
            
            # Normalizar minutos a :00 para horas como 13:01 -> 13:00
            def normalizar_minutos_a_hora_exacta(hora_time):
                if pd.isna(hora_time) or not hasattr(hora_time, 'minute'):
                    return hora_time
                
                if 1 <= hora_time.minute <= 9:
                    from datetime import time
                    return time(hora_time.hour, 0)
                
                return hora_time
            
            if 'hora_ini' in df_limpio.columns:
                df_limpio['hora_ini'] = df_limpio['hora_ini'].apply(normalizar_minutos_a_hora_exacta)
            if 'hora_fin' in df_limpio.columns:
                df_limpio['hora_fin'] = df_limpio['hora_fin'].apply(normalizar_minutos_a_hora_exacta)
            
            # Agrupar por clase con misma información
            columnas_agrupacion = ['nroidenti', 'profesor', 'materia', 'aula', 'dia', 'grupo']
            columnas_disponibles = [col for col in columnas_agrupacion if col in df_limpio.columns]
            
            # Evaluar clases continuas
            if len(columnas_disponibles) >= 4 and 'hora_ini' in df_limpio.columns and 'hora_fin' in df_limpio.columns:
                grupos_procesados = []
                
                for nombre_grupo, grupo_df in df_limpio.groupby(columnas_disponibles):
                    grupo_procesado = self._evaluar_clases_continuas(grupo_df)
                    grupos_procesados.append(grupo_procesado)
                
                if grupos_procesados:
                    df_limpio = pd.concat(grupos_procesados, ignore_index=True)
                    
                    # Reconstruir columna horario con formato estandarizado "HH:MM A HH:MM"
                    df_limpio['horario'] = df_limpio['hora_ini'].astype(str) + ' A ' + df_limpio['hora_fin'].astype(str)
            
            # Renombrar columnas a formato estándar
            df_limpio = self._renombrar_columnas(df_limpio)
            
            # Ordenar por día y horario
            if 'Día' in df_limpio.columns and 'Hora Inicio' in df_limpio.columns:
                df_limpio = df_limpio.sort_values(['Día', 'Hora Inicio'])
            
            return df_limpio
            
        except Exception as e:
            print(f"Error al limpiar programación: {e}")
            return df
    
    def _renombrar_columnas(self, df):
        """Renombra columnas a formato estándar"""
        mapeo = {
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
            'nroidenti': 'Número de Documento',
            'profesor': 'Docente',
            'dia': 'Día',
            'hora_ini': 'Hora Inicio',
            'hora_fin': 'Hora Fin',
            'horario': 'Horario',
            'aula': 'Aula',
            'descripcion': 'Facultad',
            'descripcion.1': 'Materia de la Clase'
        }
        
        for col_original, col_nuevo in mapeo.items():
            if col_original in df.columns:
                df.rename(columns={col_original: col_nuevo}, inplace=True)
        
        # Agregar columna de observaciones si no existe
        if 'Observaciones' not in df.columns:
            df['Observaciones'] = ''
        
        # Definir orden de columnas deseado
        orden_columnas = [
            'Código de la Materia', 'Grupo', 'Nivel del Grupo', 
            'Estudiantes Prematriculados', 'Estudiantes Matriculados', 'Total de Estudiantes',
            'Número de Documento', 'Docente', 'Día', 'Hora Inicio', 'Hora Fin', 'Horario',
            'Aula', 'Facultad', 'Materia de la Clase', 'Observaciones'
        ]
        
        # Reordenar columnas (solo las que existan)
        columnas_existentes = [col for col in orden_columnas if col in df.columns]
        columnas_extra = [col for col in df.columns if col not in columnas_existentes]
        
        orden_final = columnas_existentes + columnas_extra
        
        return df[orden_final]
    
    def _guardar_programacion(self, df):
        """Guarda la programación limpia"""
        try:
            if not os.path.exists(self.ruta_data):
                os.makedirs(self.ruta_data)
            
            ruta_archivo = os.path.join(self.ruta_data, "programacionLimpiaActual.xlsx")
            df.to_excel(ruta_archivo, index=False)
            return True
        except Exception as e:
            print(f"Error al guardar programación: {e}")
            return False
    
    @staticmethod
    def _obtener_dia_actual():
        """Obtiene el día actual en español"""
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        return dias[datetime.now().weekday()]
