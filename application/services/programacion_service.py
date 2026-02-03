"""Casos de uso para programación académica"""
from datetime import datetime
import pandas as pd
from interfaces.programacion_repository import ProgramacionRepository
from application.services.llave_service import LlaveService
from infrastructure.importers.programacion_excel_importer import cargar_programacion_desde_archivo
from application.processing.programacion_validator import ProgramacionValidator
from application.processing.programacion_cleaner import ProgramacionCleaner


class ProgramacionService:
    def __init__(self, repository: ProgramacionRepository, llave_service: LlaveService):
        self.repository = repository
        self.llave_service = llave_service
        self._cache_docentes_con_llaves = set()
        self._cache_timestamp = None

    def cargar_programacion_inicial(self):
        return self.repository.cargar_programacion_guardada()

    def cargar_desde_archivo(self, ruta_archivo):
        """Carga programación desde archivo Excel/CSV: importa → valida → limpia → persiste"""
        try:
            # 1. Importar
            df = cargar_programacion_desde_archivo(ruta_archivo)
            
            # 2. Validar
            es_valido, msg_error = ProgramacionValidator.validar_dataframe(df)
            if not es_valido:
                return False, None, f"❌ Validación fallida: {msg_error}"
            
            # 3. Limpiar
            df_limpio = ProgramacionCleaner.limpiar_programacion(df)
            
            # 4. Persistir
            exito, mensaje = self.repository.guardar_programacion(df_limpio)
            if exito:
                return True, df_limpio, f"✅ Programación cargada exitosamente: {len(df_limpio)} registros"
            return False, None, mensaje
            
        except Exception as e:
            return False, None, f"❌ Error al cargar programación: {str(e)}"

    def obtener_clases_del_dia(self, dia=None, incluir_pasadas=False):
        """Obtiene las clases del día actual (o del día especificado)"""
        from datetime import datetime
        
        # Si no se especifica día, usar el día actual
        if dia is None:
            dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            dia = dias_semana[datetime.now().weekday()]
        
        df = self.repository.obtener_clases_del_dia(dia)

        df = self._filtrar_aulas_invalidas(df)

        if not incluir_pasadas:
            df = self._filtrar_clases_pasadas(df)

        df = self._filtrar_docentes_con_llaves(df)
        return df

    def obtener_programacion_completa(self):
        return self.repository.obtener_programacion_actual()

    def buscar_en_programacion(self, termino, programacion_df=None):
        if programacion_df is None:
            programacion_df = self.repository.obtener_programacion_actual()

        if programacion_df is None or programacion_df.empty or not termino:
            return programacion_df

        termino = termino.strip().lower()
        mascara_busqueda = pd.Series([False] * len(programacion_df))
        columnas_busqueda = ['Número de Documento', 'Docente', 'Aula', 'Materia de la Clase']

        for columna in columnas_busqueda:
            if columna in programacion_df.columns:
                mascara_busqueda |= programacion_df[columna].astype(str).str.lower().str.contains(termino, na=False)

        return programacion_df[mascara_busqueda]

    def obtener_facultad_desde_programacion(self, documento, docente, aula, materia):
        programacion = self.repository.obtener_programacion_actual()
        if programacion is None or programacion.empty:
            return "No especificada"

        try:
            documento_str = str(documento).replace('.0', '')
            mascara = (
                (programacion['Número de Documento'].astype(str).str.replace('.0', '') == documento_str) &
                (programacion['Docente'].astype(str).str.strip() == str(docente).strip()) &
                (programacion['Aula'].astype(str).str.strip() == str(aula).strip())
            )
            registros = programacion[mascara]

            if not registros.empty and 'Facultad' in registros.columns:
                facultad = registros.iloc[0]['Facultad']
                return str(facultad).strip() if facultad and str(facultad) != 'nan' else "No especificada"

            return "No especificada"

        except Exception as e:
            print(f"Error al obtener facultad: {e}")
            return "No especificada"

    def exportar_programacion(self, df, ruta_destino):
        try:
            if df is None or df.empty:
                return False, "No hay datos para exportar"

            df.to_excel(ruta_destino, index=False, engine='openpyxl')
            return True, f"Programación exportada exitosamente en:\n{ruta_destino}"

        except PermissionError:
            return False, f"Error: No se puede escribir en el archivo.\nAsegúrese de que el archivo no esté abierto en otra aplicación."

        except Exception as e:
            return False, f"Error al exportar programación:\n{str(e)}"

    def _filtrar_aulas_invalidas(self, df):
        if df.empty or 'Aula' not in df.columns:
            return df

        try:
            df_filtrado = df.copy()
            df_filtrado = df_filtrado[
                df_filtrado['Aula'].notna() &
                (df_filtrado['Aula'].astype(str).str.strip() != '') &
                (df_filtrado['Aula'].astype(str).str.lower() != 'nan')
            ]
            return df_filtrado
        except Exception as e:
            print(f"Error al filtrar aulas inválidas: {e}")
            return df

    def _filtrar_clases_pasadas(self, df):
        if df.empty or 'Hora Fin' not in df.columns:
            return df

        try:
            ahora = datetime.now().time()

            def es_clase_valida(hora_fin):
                try:
                    if isinstance(hora_fin, str):
                        hora_str = str(hora_fin).strip()
                        if ':' in hora_str:
                            partes = hora_str.split(':')
                            hora_obj = datetime.strptime(f"{partes[0]}:{partes[1]}", '%H:%M').time()
                        else:
                            return True
                    elif isinstance(hora_fin, type(datetime.now().time())):
                        hora_obj = hora_fin
                    else:
                        return True

                    return hora_obj > ahora

                except (ValueError, AttributeError, IndexError):
                    return True

            return df[df['Hora Fin'].apply(es_clase_valida)].copy()
        except Exception as e:
            print(f"Error al filtrar clases pasadas: {e}. Retornando todas las clases.")
            return df

    def _filtrar_docentes_con_llaves(self, df):
        if df.empty:
            return df

        try:
            clases_procesadas = self.llave_service.obtener_clases_procesadas_hoy()
            clases_con_llaves = {
                (str(clase['documento']).replace('.0', ''), str(clase.get('horario', '')).strip())
                for clase in clases_procesadas
            }

            df_filtrado = df.copy()
            df_filtrado['doc_limpio'] = df_filtrado['Número de Documento'].astype(str).str.replace('.0', '')
            df_filtrado['horario_limpio'] = df_filtrado['Horario'].astype(str).str.strip()

            mascara_mantener = ~df_filtrado.apply(
                lambda row: (row['doc_limpio'], row['horario_limpio']) in clases_con_llaves,
                axis=1
            )

            df_filtrado = df_filtrado[mascara_mantener].drop(['doc_limpio', 'horario_limpio'], axis=1)
            return df_filtrado

        except Exception as e:
            print(f"Error al filtrar clases con llaves prestadas: {e}")
            return df
