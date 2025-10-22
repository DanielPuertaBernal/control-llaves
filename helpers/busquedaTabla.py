from datetime import datetime
import pandas as pd
from helpers.gestionExcel import LimpiarNumeroDocumento, ObtenerLlavesPendientes

class BusquedaTabla:
    """
    Componente de búsqueda reutilizable para tablas de datos
    Proporciona funcionalidad de búsqueda avanzada por múltiples criterios
    """
    
    def __init__(self):
        """
        Inicializa el componente de búsqueda
        """
        self.cache_docentes_con_llaves = set()
        self.cache_timestamp = None
        self.cache_valid_duration = 10  # Cache válido por 10 segundos
    
    def NormalizarBusquedaSalon(self, texto):
        """
        Normaliza el texto para búsqueda de salones eliminando guiones y espacios
        
        Args:
            texto (str): Texto a normalizar
            
        Returns:
            str: Texto normalizado
        """
        if not texto:
            return ""
        # Convertir a minúsculas, eliminar guiones, espacios y otros caracteres especiales
        return texto.lower().replace('-', '').replace('_', '').replace(' ', '').strip()
    
    def BuscarEnDataFrame(self, df, termino_busqueda, columnas_busqueda=None):
        """
        Busca en un DataFrame por múltiples criterios
        
        Args:
            df (pd.DataFrame): DataFrame donde buscar
            termino_busqueda (str): Término de búsqueda
            columnas_busqueda (list): Lista de columnas donde buscar. Si es None, usa columnas por defecto
            
        Returns:
            pd.DataFrame: DataFrame filtrado con los resultados de búsqueda
        """
        if df.empty or not termino_busqueda or termino_busqueda.strip() == "":
            return df.copy()
        
        # Columnas por defecto si no se especifican
        if columnas_busqueda is None:
            columnas_busqueda = ['Número de Documento', 'Docente', 'Aula', 'Horario', 'Materia de la Clase']
        
        try:
            # Crear una copia del DataFrame para no modificar el original
            df_busqueda = df.copy()
            
            # Limpiar término de búsqueda
            termino = termino_busqueda.strip()
            
            # Lista para almacenar máscaras de búsqueda
            mascaras_busqueda = []
            
            # Buscar por número de documento
            if 'Número de Documento' in df_busqueda.columns:
                df_busqueda['nroidenti_limpio'] = df_busqueda['Número de Documento'].astype(str).apply(LimpiarNumeroDocumento)
                mascara_documento = df_busqueda['nroidenti_limpio'].str.contains(termino, na=False, case=False)
                mascaras_busqueda.append(mascara_documento)
            
            # Buscar por docente
            if 'Docente' in df_busqueda.columns:
                mascara_docente = df_busqueda['Docente'].astype(str).str.contains(termino, na=False, case=False)
                mascaras_busqueda.append(mascara_docente)
            
            # Buscar por aula/salón con normalización
            if 'Aula' in df_busqueda.columns:
                termino_normalizado = self.NormalizarBusquedaSalon(termino)
                
                # Crear columna temporal con aulas normalizadas para comparación
                df_busqueda['aula_normalizada'] = df_busqueda['Aula'].astype(str).apply(self.NormalizarBusquedaSalon)
                
                # Buscar tanto en el aula original como en la normalizada
                mascara_aula_exacta = df_busqueda['Aula'].astype(str).str.contains(termino, na=False, case=False)
                mascara_aula_normalizada = df_busqueda['aula_normalizada'].str.contains(termino_normalizado, na=False, case=False)
                mascara_aula = mascara_aula_exacta | mascara_aula_normalizada
                mascaras_busqueda.append(mascara_aula)
            
            # Buscar por horario
            if 'Horario' in df_busqueda.columns:
                mascara_horario = df_busqueda['Horario'].astype(str).str.contains(termino, na=False, case=False)
                mascaras_busqueda.append(mascara_horario)
            
            # Buscar por materia
            if 'Materia de la Clase' in df_busqueda.columns:
                mascara_materia = df_busqueda['Materia de la Clase'].astype(str).str.contains(termino, na=False, case=False)
                mascaras_busqueda.append(mascara_materia)
            
            # Combinar todas las máscaras con OR (cualquiera de las condiciones)
            if mascaras_busqueda:
                mascara_combinada = mascaras_busqueda[0]
                for mascara in mascaras_busqueda[1:]:
                    mascara_combinada = mascara_combinada | mascara
                
                # Aplicar filtro combinado
                resultado = df_busqueda[mascara_combinada].copy()
            else:
                # Si no hay columnas válidas para buscar, retornar DataFrame vacío
                resultado = df_busqueda.iloc[0:0].copy()
            
            # Limpiar columnas temporales
            columnas_temporales = ['nroidenti_limpio', 'aula_normalizada']
            for col_temp in columnas_temporales:
                if col_temp in resultado.columns:
                    resultado = resultado.drop(col_temp, axis=1)
            
            return resultado
            
        except Exception as e:
            print(f"Error en búsqueda: {str(e)}")
            return df.copy()  # Retornar DataFrame original en caso de error
    
    def FiltrarPorDiaActual(self, df, columna_dia='Día'):
        """
        Filtra un DataFrame por el día actual
        
        Args:
            df (pd.DataFrame): DataFrame a filtrar
            columna_dia (str): Nombre de la columna que contiene el día
            
        Returns:
            pd.DataFrame: DataFrame filtrado por día actual
        """
        if df.empty:
            return df
        
        try:
            # Obtener día actual en formato español y mayúsculas
            dia_numero = datetime.now().weekday()  # 0=Monday, 6=Sunday
            dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            dia_actual = dias_espanol[dia_numero]
            
            # Buscar la columna de día (insensible a mayúsculas)
            columna_encontrada = None
            if columna_dia in df.columns:
                columna_encontrada = columna_dia
            else:
                for col in df.columns:
                    if 'día' in col.lower():
                        columna_encontrada = col
                        break
            
            if columna_encontrada is None:
                print(f"No se encontró columna de día. Columnas disponibles: {list(df.columns)}")
                return df  # Retornar todos los datos si no se encuentra la columna
            
            # Filtrar por día actual
            datos_del_dia = df[df[columna_encontrada] == dia_actual].copy()
            
            return datos_del_dia
            
        except Exception as e:
            print(f"Error al filtrar por día actual: {str(e)}")
            return df
    
    def EliminarClasesPasadas(self, df, columna_hora_fin='Hora Fin'):
        """
        Elimina las clases que ya terminaron basándose en la hora actual
        
        Args:
            df (pd.DataFrame): DataFrame a filtrar
            columna_hora_fin (str): Nombre de la columna que contiene la hora de fin
            
        Returns:
            pd.DataFrame: DataFrame sin clases pasadas
        """
        if df.empty:
            return df
        
        try:
            ahora = datetime.now()
            
            # Verificar si existe la columna de hora fin
            if columna_hora_fin not in df.columns:
                return df  # Si no hay columna de hora fin, retornar todos los datos
            
            def ConvertirHoraFin(hora_fin):
                try:
                    # Manejar formato HH:MM:SS
                    if isinstance(hora_fin, str):
                        if len(hora_fin.split(':')) == 3:
                            return datetime.strptime(hora_fin, '%H:%M:%S').time()
                        else:
                            return datetime.strptime(hora_fin, '%H:%M').time()
                    return None
                except ValueError:
                    return None
            
            df_filtrado = df.copy()
            df_filtrado['Hora_Fin_Convertida'] = df_filtrado[columna_hora_fin].apply(ConvertirHoraFin)
            df_filtrado = df_filtrado[df_filtrado['Hora_Fin_Convertida'].notnull()]
            df_filtrado = df_filtrado[df_filtrado['Hora_Fin_Convertida'] > ahora.time()]
            
            # Eliminar columna temporal
            if 'Hora_Fin_Convertida' in df_filtrado.columns:
                df_filtrado = df_filtrado.drop('Hora_Fin_Convertida', axis=1)
            
            return df_filtrado
            
        except Exception as e:
            print(f"Error al eliminar clases pasadas: {str(e)}")
            return df
    
    def ActualizarCacheDocentes(self, forzar_actualizacion=False):
        """
        Actualiza el cache de docentes que tienen llaves entregadas
        
        Args:
            forzar_actualizacion (bool): Si True, fuerza la actualización sin importar el timestamp
        """
        try:
            ahora = datetime.now()
            
            # Verificar si el cache necesita actualización
            if (forzar_actualizacion or
                self.cache_timestamp is None or 
                (ahora - self.cache_timestamp).total_seconds() > self.cache_valid_duration):
                
                # Obtener lista de docentes con llaves pendientes
                llaves_pendientes = ObtenerLlavesPendientes()
                
                # Crear set con los documentos que tienen llaves entregadas
                self.cache_docentes_con_llaves = {
                    LimpiarNumeroDocumento(str(registro.get('Número de Documento', ''))) 
                    for registro in llaves_pendientes
                }
                
                # Actualizar timestamp del cache
                self.cache_timestamp = ahora
                
        except Exception as e:
            print(f"Error al actualizar cache de docentes: {e}")
            # En caso de error, limpiar cache para evitar datos incorrectos
            self.cache_docentes_con_llaves = set()
    
    def FiltrarDocentesSinLlaves(self, df, columna_documento='Número de Documento'):
        """
        Filtra docentes que ya tienen llaves entregadas O que ya entregaron llaves hoy
        
        Args:
            df (pd.DataFrame): DataFrame a filtrar
            columna_documento (str): Nombre de la columna que contiene el número de documento
            
        Returns:
            pd.DataFrame: DataFrame sin docentes que ya tienen llaves o ya entregaron hoy
        """
        if df.empty or columna_documento not in df.columns:
            return df
        
        try:
            from helpers.gestionExcel import ObtenerHistorialCompleto
            from datetime import datetime
            
            # Obtener fecha actual
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            
            # Obtener historial completo (llaves en préstamo + llaves entregadas)
            historial_completo = ObtenerHistorialCompleto()
            
            # Crear set con claves de clase (documento|aula|horario) que ya entregaron llaves HOY
            clases_con_entrega_hoy = set()

            for registro in historial_completo:
                fecha_entrega = registro.get('Fecha de entrega', '')
                if fecha_entrega == fecha_hoy:
                    documento = LimpiarNumeroDocumento(str(registro.get('Número de Documento', '')))
                    aula = str(registro.get('Aula', '')).strip()
                    horario = str(registro.get('Horario', '')).strip()
                    clave = f"{documento}|{aula}|{horario}"
                    clases_con_entrega_hoy.add(clave)

            # Función para determinar si una fila corresponde a una clase que ya entregó llave hoy
            def ClaseSinEntregaHoy(fila):
                try:
                    documento_limpio = LimpiarNumeroDocumento(str(fila[columna_documento]))
                    aula_fila = str(fila.get('Aula', '')).strip()
                    horario_fila = str(fila.get('Horario', '')).strip()
                    clave_fila = f"{documento_limpio}|{aula_fila}|{horario_fila}"
                    return clave_fila not in clases_con_entrega_hoy
                except Exception:
                    # Si hay algún problema con la fila, mantenerla por seguridad
                    return True

            # Aplicar filtro fila a fila para mantener sólo las clases que no fueron entregadas hoy
            mascara_sin_entregas = df.apply(ClaseSinEntregaHoy, axis=1)
            return df[mascara_sin_entregas].copy()
            
        except Exception as e:
            print(f"Error al filtrar docentes sin llaves: {str(e)}")
            return df
    
    def InvalidarCache(self):
        """
        Invalida el cache forzando una actualización en la próxima consulta
        """
        self.cache_timestamp = None
        self.cache_docentes_con_llaves = set()
    
    def OrdenarPorHorario(self, df, columna_horario='Horario'):
        """
        Ordena el DataFrame por horario
        
        Args:
            df (pd.DataFrame): DataFrame a ordenar
            columna_horario (str): Nombre de la columna de horario
            
        Returns:
            pd.DataFrame: DataFrame ordenado por horario
        """
        if df.empty or columna_horario not in df.columns:
            return df
        
        try:
            return df.sort_values(by=columna_horario).copy()
        except Exception as e:
            print(f"Error al ordenar por horario: {str(e)}")
            return df