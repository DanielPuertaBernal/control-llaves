"""Limpiador y transformador de programación académica"""
import pandas as pd
from datetime import datetime, timedelta, time


class ProgramacionCleaner:
    MAPEO_COLUMNAS = {
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

    ORDEN_COLUMNAS = [
        'Código de la Materia', 'Grupo', 'Nivel del Grupo',
        'Estudiantes Prematriculados', 'Estudiantes Matriculados', 'Total de Estudiantes',
        'Número de Documento', 'Docente', 'Día', 'Hora Inicio', 'Hora Fin', 'Horario',
        'Aula', 'Facultad', 'Materia de la Clase', 'Observaciones'
    ]

    GAP_MINIMO_MINUTOS = 30

    @staticmethod
    def limpiar_texto(texto) -> str:
        if pd.isna(texto):
            return ''
        texto_str = str(texto)
        texto_str = texto_str.replace('_x000D_', '')
        texto_str = texto_str.replace('\r', '').replace('\n', ' ')
        texto_str = ' '.join(texto_str.split())
        return texto_str.strip()

    @staticmethod
    def limpiar_documento(doc) -> str:
        doc_str = str(doc)
        if doc_str.endswith('.0'):
            return doc_str[:-2]
        return doc_str

    @staticmethod
    def normalizar_minutos(hora_time) -> time:
        if pd.isna(hora_time) or not hasattr(hora_time, 'minute'):
            return hora_time
        if 1 <= hora_time.minute <= 9:
            return time(hora_time.hour, 0)
        return hora_time

    @staticmethod
    def separar_horario(df: pd.DataFrame) -> pd.DataFrame:
        if 'horario' not in df.columns or len(df) == 0:
            return df

        horario_ejemplo = str(df['horario'].iloc[0]).upper()

        if ' A ' in horario_ejemplo:
            df[['hora_ini', 'hora_fin']] = df['horario'].str.upper().str.split(' A ', expand=True)
        elif ' a ' in str(df['horario'].iloc[0]):
            df[['hora_ini', 'hora_fin']] = df['horario'].str.split(' a ', expand=True)
        else:
            df['hora_ini'] = df['horario']
            df['hora_fin'] = df['horario']

        return df

    @staticmethod
    def convertir_horas_a_time(df: pd.DataFrame) -> pd.DataFrame:
        try:
            if 'hora_ini' in df.columns:
                df['hora_ini'] = pd.to_datetime(df['hora_ini'], format='%H:%M', errors='coerce').dt.time
            if 'hora_fin' in df.columns:
                df['hora_fin'] = pd.to_datetime(df['hora_fin'], format='%H:%M', errors='coerce').dt.time
        except Exception:
            pass
        return df

    @staticmethod
    def procesar_estudiantes(df: pd.DataFrame) -> pd.DataFrame:
        if 'nro_estudiantes_premat' not in df.columns:
            df['nro_estudiantes_premat'] = 0
        if 'nro_estudiantes' not in df.columns:
            df['nro_estudiantes'] = 0

        df['nro_estudiantes_premat'] = pd.to_numeric(df['nro_estudiantes_premat'], errors='coerce').fillna(0)
        df['nro_estudiantes'] = pd.to_numeric(df['nro_estudiantes'], errors='coerce').fillna(0)
        df['total_estudiantes'] = df['nro_estudiantes_premat'] + df['nro_estudiantes']

        return df

    @staticmethod
    def evaluar_clases_continuas(grupo_df: pd.DataFrame) -> pd.DataFrame:
        if len(grupo_df) <= 1:
            return grupo_df

        grupo_df = grupo_df.sort_values('hora_ini')

        try:
            clases_separadas = []
            clase_actual = [grupo_df.iloc[0]]

            for i in range(1, len(grupo_df)):
                fila_anterior = grupo_df.iloc[i-1]
                fila_actual = grupo_df.iloc[i]

                if pd.notna(fila_anterior['hora_fin']) and pd.notna(fila_actual['hora_ini']):
                    try:
                        fin_anterior = datetime.combine(datetime.today(), fila_anterior['hora_fin'])
                        inicio_actual = datetime.combine(datetime.today(), fila_actual['hora_ini'])
                        gap = inicio_actual - fin_anterior

                        if gap > timedelta(minutes=ProgramacionCleaner.GAP_MINIMO_MINUTOS):
                            clases_separadas.append(pd.DataFrame(clase_actual))
                            clase_actual = [fila_actual]
                        else:
                            clase_actual.append(fila_actual)
                    except Exception:
                        clases_separadas.append(pd.DataFrame(clase_actual))
                        clase_actual = [fila_actual]
                else:
                    clase_actual.append(fila_actual)

            clases_separadas.append(pd.DataFrame(clase_actual))

            resultado = []
            for clase_df in clases_separadas:
                if len(clase_df) > 1:
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

    @staticmethod
    def renombrar_columnas(df: pd.DataFrame) -> pd.DataFrame:
        for col_original, col_nuevo in ProgramacionCleaner.MAPEO_COLUMNAS.items():
            if col_original in df.columns:
                df.rename(columns={col_original: col_nuevo}, inplace=True)

        if 'Observaciones' not in df.columns:
            df['Observaciones'] = ''

        columnas_existentes = [col for col in ProgramacionCleaner.ORDEN_COLUMNAS if col in df.columns]
        columnas_extra = [col for col in df.columns if col not in columnas_existentes]
        orden_final = columnas_existentes + columnas_extra

        return df[orden_final]

    @staticmethod
    def limpiar_programacion(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        try:
            df_limpio = df.copy()
            df_limpio.columns = df_limpio.columns.str.strip()

            columnas_texto = ['profesor', 'dia', 'aula', 'materia', 'MATERIA', 'descripcion', 'descripcion.1']
            for col in columnas_texto:
                if col in df_limpio.columns:
                    df_limpio[col] = df_limpio[col].apply(ProgramacionCleaner.limpiar_texto)

            df_limpio['horario'] = df_limpio['horario'].astype(str) if 'horario' in df_limpio.columns else ''
            if 'horario' in df_limpio.columns:
                df_limpio['horario'] = df_limpio['horario'].apply(ProgramacionCleaner.limpiar_texto)

            df_limpio['profesor'] = df_limpio['profesor'].fillna('').str.strip() if 'profesor' in df_limpio.columns else ''

            if 'nroidenti' in df_limpio.columns:
                df_limpio['nroidenti'] = df_limpio['nroidenti'].apply(ProgramacionCleaner.limpiar_documento)

            if 'dia' in df_limpio.columns:
                df_limpio['dia'] = df_limpio['dia'].str.upper().str.strip()

            if 'MATERIA' in df_limpio.columns:
                df_limpio['materia'] = df_limpio['MATERIA'].fillna('').str.strip()
            elif 'materia' not in df_limpio.columns:
                df_limpio['materia'] = df_limpio.get('materia', '').fillna('').str.strip()

            df_limpio = ProgramacionCleaner.procesar_estudiantes(df_limpio)
            df_limpio = ProgramacionCleaner.separar_horario(df_limpio)
            df_limpio = ProgramacionCleaner.convertir_horas_a_time(df_limpio)

            if 'hora_ini' in df_limpio.columns:
                df_limpio['hora_ini'] = df_limpio['hora_ini'].apply(ProgramacionCleaner.normalizar_minutos)
            if 'hora_fin' in df_limpio.columns:
                df_limpio['hora_fin'] = df_limpio['hora_fin'].apply(ProgramacionCleaner.normalizar_minutos)

            columnas_agrupacion = ['nroidenti', 'profesor', 'materia', 'aula', 'dia', 'grupo']
            columnas_disponibles = [col for col in columnas_agrupacion if col in df_limpio.columns]

            if len(columnas_disponibles) >= 4 and 'hora_ini' in df_limpio.columns and 'hora_fin' in df_limpio.columns:
                grupos_procesados = []

                for _, grupo_df in df_limpio.groupby(columnas_disponibles):
                    grupo_procesado = ProgramacionCleaner.evaluar_clases_continuas(grupo_df)
                    grupos_procesados.append(grupo_procesado)

                if grupos_procesados:
                    df_limpio = pd.concat(grupos_procesados, ignore_index=True)
                    df_limpio['horario'] = df_limpio['hora_ini'].astype(str) + ' A ' + df_limpio['hora_fin'].astype(str)

            df_limpio = ProgramacionCleaner.renombrar_columnas(df_limpio)

            if 'Día' in df_limpio.columns and 'Hora Inicio' in df_limpio.columns:
                df_limpio = df_limpio.sort_values(['Día', 'Hora Inicio'])

            return df_limpio

        except Exception as e:
            print(f"Error al limpiar programación: {e}")
            return df
