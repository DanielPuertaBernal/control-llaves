"""
Repositorio de programación académica
Responsabilidad: Persistencia (carga y guardado) de datos de programación
"""
import pandas as pd
from datetime import datetime
from services.mongo_client import MongoClientProvider
from datetime import time


class ProgramacionRepository:
    """Repositorio para operaciones de persistencia de programación"""
    
    def __init__(self, ruta_data: str = None):
        """
        Inicializa el repositorio
        
        Args:
            ruta_data: Ruta del directorio data. Si es None, se calcula automáticamente
        """
        self.collection = MongoClientProvider.get_collection("programacion")
    
    def cargar_desde_excel(self, ruta_archivo: str) -> tuple[bool, pd.DataFrame, str]:
        """
        Carga un archivo Excel o CSV
        
        Args:
            ruta_archivo: Ruta al archivo
            
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        try:
            if ruta_archivo.endswith('.csv'):
                df = pd.read_csv(ruta_archivo, encoding='utf-8')
            else:
                df = pd.read_excel(ruta_archivo)
            
            return True, df, f"✅ Archivo cargado: {len(df)} registros"
            
        except Exception as e:
            return False, None, f"❌ Error al cargar archivo: {str(e)}"
    
    def cargar_programacion_guardada(self) -> tuple[bool, pd.DataFrame, str]:
        """
        Carga la programación guardada previamente
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        try:
            registros = list(self.collection.find({}, {"_id": 0}))
            if not registros:
                return False, None, "❌ No hay programación guardada"
            df = pd.DataFrame(registros)
            mensaje = f"✅ Programación cargada: {len(df)} registros"
            return True, df, mensaje
        except Exception as e:
            return False, None, f"❌ Error al cargar: {str(e)}"
    
    def guardar_programacion(self, df: pd.DataFrame) -> tuple[bool, str]:
        """
        Guarda la programación limpia
        
        Args:
            df: DataFrame a guardar
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if df is None or df.empty:
                return False, "❌ No hay programación para guardar"

            registros = df.to_dict('records')
            version_carga = datetime.utcnow()
            for registro in registros:
                # Convertir tiempos a string para MongoDB
                for key, value in list(registro.items()):
                    if isinstance(value, time):
                        registro[key] = value.strftime('%H:%M:%S')
                    elif isinstance(value, datetime):
                        registro[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                registro["version_carga"] = version_carga

            self.collection.delete_many({})
            if registros:
                self.collection.insert_many(registros)

            return True, f"✅ Programación guardada en MongoDB: {len(registros)} registros"
            
        except Exception as e:
            return False, f"❌ Error al guardar: {str(e)}"
    
    def existe_programacion_guardada(self) -> bool:
        """
        Verifica si existe una programación guardada
        
        Returns:
            bool: True si existe
        """
        return self.collection.count_documents({}) > 0
