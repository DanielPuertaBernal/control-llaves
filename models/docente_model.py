"""
Modelo para la gestión de información de docentes
Maneja la carga, validación y almacenamiento de datos de docentes
"""
import pandas as pd
import os
from openpyxl import Workbook, load_workbook


class DocenteModel:
    """Modelo para gestionar información de docentes"""
    
    NOMBRE_ARCHIVO = "docentes.xlsx"
    
    def __init__(self):
        self.ruta_data = self._obtener_ruta_data()
        self.ruta_archivo = os.path.join(self.ruta_data, self.NOMBRE_ARCHIVO)
    
    def _obtener_ruta_data(self):
        """Obtiene la ruta del directorio data"""
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_proyecto = os.path.dirname(ruta_actual)
        return os.path.join(ruta_proyecto, "data")
    
    def cargar_desde_excel(self, ruta_archivo):
        """
        Carga información de docentes desde un archivo Excel
        
        Args:
            ruta_archivo (str): Ruta al archivo Excel con datos de docentes
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        try:
            # Leer archivo según extensión
            if ruta_archivo.endswith('.csv'):
                df = pd.read_csv(ruta_archivo, encoding='utf-8')
            elif ruta_archivo.endswith('.ods'):
                df = pd.read_excel(ruta_archivo, engine='odf')
            elif ruta_archivo.endswith('.xls'):
                df = pd.read_excel(ruta_archivo, engine='xlrd')
            else:
                # Intentar con openpyxl primero para .xlsx
                try:
                    df = pd.read_excel(ruta_archivo, engine='openpyxl')
                except Exception as e:
                    # Si falla, intentar con otros engines
                    try:
                        df = pd.read_excel(ruta_archivo, engine='xlrd')
                    except:
                        try:
                            df = pd.read_excel(ruta_archivo, engine='odf')
                        except:
                            return False, None, f"❌ Error: El archivo no tiene un formato Excel válido.\nDetalles: {str(e)}"
            
            # Validar columnas requeridas
            columnas_requeridas = [
                'Numero de documento', 'Nombre', 'Facultad', 'Correo', 'Id Carnet'
            ]
            
            # Normalizar nombres de columnas (por si tienen mayúsculas/minúsculas diferentes)
            df.columns = df.columns.str.strip()
            
            # Verificar si todas las columnas requeridas están presentes
            columnas_faltantes = []
            for col in columnas_requeridas:
                if col not in df.columns:
                    # Buscar variaciones del nombre
                    col_normalizada = col.lower().replace(' ', '')
                    encontrada = False
                    for df_col in df.columns:
                        if df_col.lower().replace(' ', '') == col_normalizada:
                            # Renombrar columna a formato estándar
                            df.rename(columns={df_col: col}, inplace=True)
                            encontrada = True
                            break
                    
                    if not encontrada:
                        columnas_faltantes.append(col)
            
            if columnas_faltantes:
                return False, None, f"❌ Faltan columnas requeridas: {', '.join(columnas_faltantes)}"
            
            # Limpiar y validar datos
            df = self._limpiar_datos(df)
            
            # Guardar en archivo local
            exito, mensaje = self._guardar_docentes(df)
            
            if exito:
                return True, df, f"✅ Docentes cargados exitosamente: {len(df)} registros"
            else:
                return False, None, mensaje
            
        except Exception as e:
            return False, None, f"❌ Error al cargar archivo: {str(e)}"
    
    def _limpiar_datos(self, df):
        """Limpia y normaliza los datos de docentes"""
        # Eliminar filas con documento vacío
        df = df[df['Numero de documento'].notna()]
        
        # Limpiar número de documento (quitar decimales .0)
        df['Numero de documento'] = df['Numero de documento'].astype(str).str.replace('.0', '', regex=False)
        
        # Limpiar espacios en blanco
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        
        # Eliminar duplicados por número de documento
        df = df.drop_duplicates(subset=['Numero de documento'], keep='first')
        
        return df
    
    def _guardar_docentes(self, df):
        """
        Guarda la información de docentes en el archivo local
        
        Args:
            df (pd.DataFrame): DataFrame con información de docentes
        
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not os.path.exists(self.ruta_data):
                os.makedirs(self.ruta_data)
            
            # Guardar DataFrame en Excel
            df.to_excel(self.ruta_archivo, index=False, engine='openpyxl')
            
            return True, f"✅ Información guardada en: {self.ruta_archivo}"
            
        except Exception as e:
            return False, f"❌ Error al guardar: {str(e)}"
    
    def obtener_docentes(self):
        """
        Obtiene la información de docentes guardada
        
        Returns:
            pd.DataFrame: DataFrame con información de docentes o DataFrame vacío
        """
        try:
            if not os.path.exists(self.ruta_archivo):
                return pd.DataFrame()
            
            df = pd.read_excel(self.ruta_archivo)
            return df
            
        except Exception as e:
            print(f"Error al obtener docentes: {e}")
            return pd.DataFrame()
    
    def buscar_docente_por_documento(self, numero_documento):
        """
        Busca un docente por número de documento
        
        Args:
            numero_documento (str): Número de documento a buscar
        
        Returns:
            dict: Información del docente o None si no existe
        """
        try:
            df = self.obtener_docentes()
            
            if df.empty:
                return None
            
            # Limpiar documento de búsqueda
            doc_limpio = str(numero_documento).replace('.0', '').strip()
            
            # Buscar en el DataFrame
            resultado = df[df['Numero de documento'].astype(str) == doc_limpio]
            
            if not resultado.empty:
                return resultado.iloc[0].to_dict()
            
            return None
            
        except Exception as e:
            print(f"Error al buscar docente: {e}")
            return None
    
    def buscar_docente_por_carnet(self, id_carnet):
        """
        Busca un docente por ID de carnet NFC
        
        Args:
            id_carnet (str): ID del carnet NFC
        
        Returns:
            dict: Información del docente o None si no existe
        """
        try:
            df = self.obtener_docentes()
            
            if df.empty:
                return None
            
            # Limpiar ID de carnet
            carnet_limpio = str(id_carnet).strip()
            
            # Buscar en el DataFrame
            resultado = df[df['Id Carnet'].astype(str) == carnet_limpio]
            
            if not resultado.empty:
                return resultado.iloc[0].to_dict()
            
            return None
            
        except Exception as e:
            print(f"Error al buscar docente por carnet: {e}")
            return None
