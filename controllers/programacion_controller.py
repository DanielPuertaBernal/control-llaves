"""
Controlador para la gestión de programación académica
Maneja la lógica de negocio de carga y procesamiento de programación
"""
from models.programacion import ProgramacionModel
from datetime import datetime
import pandas as pd


class ProgramacionController:
    """Controlador para gestionar programación académica"""
    
    def __init__(self):
        self.model = ProgramacionModel()
        self._cache_docentes_con_llaves = set()
        self._cache_timestamp = None
    
    def cargar_programacion_inicial(self):
        """
        Carga la programación guardada al iniciar la aplicación
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        return self.model.cargar_programacion_guardada()
    
    def cargar_desde_archivo(self, ruta_archivo):
        """
        Carga y procesa un nuevo archivo de programación
        
        Args:
            ruta_archivo (str): Ruta al archivo
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        return self.model.cargar_desde_archivo(ruta_archivo)
    
    def obtener_clases_del_dia(self, dia=None):
        """
        Obtiene las clases del día actual o especificado
        
        Args:
            dia (str): Día de la semana (opcional)
        
        Returns:
            pd.DataFrame: Clases del día
        """
        df = self.model.obtener_clases_del_dia(dia)
        
        # Aplicar filtros adicionales
        df = self._filtrar_aulas_invalidas(df)
        df = self._filtrar_clases_pasadas(df)
        df = self._filtrar_docentes_con_llaves(df)
        
        return df
    
    def obtener_programacion_completa(self):
        """
        Obtiene la programación completa actual
        
        Returns:
            pd.DataFrame: Programación completa
        """
        return self.model.obtener_programacion_actual()
    
    def buscar_en_programacion(self, termino, programacion_df=None):
        """
        Busca en la programación por término
        
        Args:
            termino (str): Término de búsqueda
            programacion_df: DataFrame donde buscar (opcional)
        
        Returns:
            pd.DataFrame: Resultados de búsqueda
        """
        if programacion_df is None:
            programacion_df = self.model.obtener_programacion_actual()
        
        if programacion_df is None or programacion_df.empty or not termino:
            return programacion_df
        
        # Buscar en múltiples columnas
        termino = termino.strip().lower()
        mascara_busqueda = pd.Series([False] * len(programacion_df))
        
        columnas_busqueda = ['Número de Documento', 'Docente', 'Aula', 'Materia de la Clase']
        
        for columna in columnas_busqueda:
            if columna in programacion_df.columns:
                mascara_busqueda |= programacion_df[columna].astype(str).str.lower().str.contains(termino, na=False)
        
        return programacion_df[mascara_busqueda]
    
    def obtener_facultad_desde_programacion(self, documento, docente, aula, materia):
        """
        Obtiene la facultad desde la programación
        
        Args:
            documento: Número de documento
            docente: Nombre del docente
            aula: Salón
            materia: Materia de la clase
        
        Returns:
            str: Nombre de la facultad
        """
        programacion = self.model.obtener_programacion_actual()
        
        if programacion is None or programacion.empty:
            return "No especificada"
        
        try:
            documento_str = str(documento).replace('.0', '')
            
            # Buscar por múltiples criterios
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
    
    def _filtrar_aulas_invalidas(self, df):
        """Filtra registros donde el aula es NaN o vacía"""
        if df.empty or 'Aula' not in df.columns:
            return df
        
        try:
            # Filtrar aulas NaN, None, vacías o que contengan 'nan'
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
        """Filtra clases que ya terminaron"""
        if df.empty or 'Hora Fin' not in df.columns:
            return df
        
        try:
            ahora = datetime.now().time()
            
            def es_clase_valida(hora_fin):
                try:
                    if isinstance(hora_fin, str):
                        hora_obj = datetime.strptime(hora_fin.split(':')[0] + ':' + hora_fin.split(':')[1], '%H:%M').time()
                        return hora_obj > ahora
                    return True
                except:
                    return True
            
            return df[df['Hora Fin'].apply(es_clase_valida)].copy()
        except Exception as e:
            print(f"Error al filtrar clases pasadas: {e}")
            return df
    
    def _filtrar_docentes_con_llaves(self, df):
        """Filtra docentes que ya tienen llaves prestadas"""
        if df.empty:
            return df
        
        try:
            # Importar aquí para evitar dependencias circulares
            from controllers.llave_controller import LlaveController
            
            llave_ctrl = LlaveController()
            llaves_prestadas = llave_ctrl.obtener_llaves_en_prestamo()
            
            documentos_con_llaves = {llave['documento'] for llave in llaves_prestadas}
            
            # Filtrar DataFrame
            df_filtrado = df.copy()
            df_filtrado['doc_limpio'] = df_filtrado['Número de Documento'].astype(str).str.replace('.0', '')
            df_filtrado = df_filtrado[~df_filtrado['doc_limpio'].isin(documentos_con_llaves)]
            df_filtrado = df_filtrado.drop('doc_limpio', axis=1)
            
            return df_filtrado
            
        except Exception as e:
            print(f"Error al filtrar docentes con llaves: {e}")
            return df
    
    def exportar_programacion(self, df, ruta_destino):
        """
        Exporta el DataFrame de programación a un archivo Excel
        
        Args:
            df: DataFrame con la programación a exportar
            ruta_destino: Ruta completa donde guardar el archivo
        
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Verificar que el DataFrame no esté vacío
            if df is None or df.empty:
                return False, "No hay datos para exportar"
            
            # Exportar a Excel
            df.to_excel(ruta_destino, index=False, engine='openpyxl')
            
            return True, f"Programación exportada exitosamente en:\n{ruta_destino}"
            
        except PermissionError:
            return False, f"Error: No se puede escribir en el archivo.\nAsegúrese de que el archivo no esté abierto en otra aplicación."
        
        except Exception as e:
            return False, f"Error al exportar programación:\n{str(e)}"
