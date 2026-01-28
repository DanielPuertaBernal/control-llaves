"""
Controlador para la gestión de información de docentes
Maneja la lógica de negocio de carga y consulta de docentes
"""
from models.docente_model import DocenteModel


class DocenteController:
    """Controlador para gestionar información de docentes"""
    
    def __init__(self):
        self.model = DocenteModel()
    
    def cargar_informacion_docentes(self, ruta_archivo):
        """
        Carga información de docentes desde un archivo Excel
        
        Args:
            ruta_archivo (str): Ruta al archivo Excel con datos de docentes
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        return self.model.cargar_desde_excel(ruta_archivo)
    
    def obtener_docentes(self):
        """
        Obtiene todos los docentes registrados
        
        Returns:
            pd.DataFrame: DataFrame con información de docentes
        """
        return self.model.obtener_docentes()
    
    def buscar_docente_por_documento(self, numero_documento):
        """
        Busca un docente por número de documento
        
        Args:
            numero_documento (str): Número de documento
        
        Returns:
            dict: Información del docente o None
        """
        return self.model.buscar_docente_por_documento(numero_documento)
    
    def buscar_docente_por_carnet(self, id_carnet):
        """
        Busca un docente por ID de carnet NFC
        
        Args:
            id_carnet (str): ID del carnet NFC
        
        Returns:
            dict: Información del docente o None
        """
        return self.model.buscar_docente_por_carnet(id_carnet)
    
    def verificar_docentes_cargados(self):
        """
        Verifica si hay docentes cargados en el sistema
        
        Returns:
            tuple: (hay_docentes, total_docentes)
        """
        df = self.model.obtener_docentes()
        return not df.empty, len(df)
