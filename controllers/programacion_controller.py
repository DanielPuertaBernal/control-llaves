"""
Controlador para la gestión de programación académica
Maneja la lógica de negocio de carga y procesamiento de programación
"""
from application.programacion_service import ProgramacionService
from application.llave_service import LlaveService
from infrastructure.repositories.programacion_mongo_repository import ProgramacionMongoRepository
from infrastructure.repositories.llave_mongo_repository import LlaveMongoRepository


class ProgramacionController:
    """Controlador para gestionar programación académica"""
    
    def __init__(self):
        llave_service = LlaveService(LlaveMongoRepository())
        self.service = ProgramacionService(ProgramacionMongoRepository(), llave_service)
    
    def cargar_programacion_inicial(self):
        """
        Carga la programación guardada al iniciar la aplicación
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        return self.service.cargar_programacion_inicial()
    
    def cargar_desde_archivo(self, ruta_archivo):
        """
        Carga y procesa un nuevo archivo de programación
        
        Args:
            ruta_archivo (str): Ruta al archivo
        
        Returns:
            tuple: (exito, dataframe, mensaje)
        """
        return self.service.cargar_desde_archivo(ruta_archivo)
    
    def obtener_clases_del_dia(self, dia=None, incluir_pasadas=False):
        """
        Obtiene las clases del día actual o especificado
        
        Args:
            dia (str): Día de la semana (opcional)
            incluir_pasadas (bool): Si True, incluye clases que ya terminaron (útil para fin de jornada)
        
        Returns:
            pd.DataFrame: Clases del día
        """
        return self.service.obtener_clases_del_dia(dia, incluir_pasadas)
    
    def obtener_programacion_completa(self):
        """
        Obtiene la programación completa actual
        
        Returns:
            pd.DataFrame: Programación completa
        """
        return self.service.obtener_programacion_completa()
    
    def buscar_en_programacion(self, termino, programacion_df=None):
        """
        Busca en la programación por término
        
        Args:
            termino (str): Término de búsqueda
            programacion_df: DataFrame donde buscar (opcional)
        
        Returns:
            pd.DataFrame: Resultados de búsqueda
        """
        return self.service.buscar_en_programacion(termino, programacion_df)
    
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
        return self.service.obtener_facultad_desde_programacion(documento, docente, aula, materia)
    
    def exportar_programacion(self, df, ruta_destino):
        """
        Exporta el DataFrame de programación a un archivo Excel
        
        Args:
            df: DataFrame con la programación a exportar
            ruta_destino: Ruta completa donde guardar el archivo
        
        Returns:
            tuple: (exito, mensaje)
        """
        return self.service.exportar_programacion(df, ruta_destino)
