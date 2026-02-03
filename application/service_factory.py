"""
Service Factory - Patrón Factory para crear servicios con dependencias inyectadas
"""
from application.docente_service import DocenteService
from application.llave_service import LlaveService
from application.historial_service import HistorialService
from application.programacion_service import ProgramacionService
from infrastructure.repositories.docente_mongo_repository import DocenteMongoRepository
from infrastructure.repositories.llave_mongo_repository import LlaveMongoRepository
from infrastructure.repositories.programacion_mongo_repository import ProgramacionMongoRepository


class ServiceFactory:
    """Factory para crear servicios con todas sus dependencias"""
    
    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceFactory, cls).__new__(cls)
            cls._instance._inicializar()
        return cls._instance
    
    def _inicializar(self):
        """Inicializa los servicios una sola vez (singleton)"""
        # Crear repositories
        self._docente_repo = DocenteMongoRepository()
        self._llave_repo = LlaveMongoRepository()
        self._programacion_repo = ProgramacionMongoRepository()
        
        # Crear servicios con inyección de dependencias
        self._services['docente'] = DocenteService(self._docente_repo)
        self._services['llave'] = LlaveService(self._llave_repo)
        
        # HistorialService usa LlaveRepository para traer datos
        self._services['historial'] = HistorialService(self._llave_repo)
        
        # ProgramacionService requiere llave_service
        self._services['programacion'] = ProgramacionService(
            self._programacion_repo,
            self._services['llave']
        )
    
    def get_docente_service(self) -> DocenteService:
        """Obtiene servicio de docentes"""
        return self._services['docente']
    
    def get_llave_service(self) -> LlaveService:
        """Obtiene servicio de llaves"""
        return self._services['llave']
    
    def get_historial_service(self) -> HistorialService:
        """Obtiene servicio de historial"""
        return self._services['historial']
    
    def get_programacion_service(self) -> ProgramacionService:
        """Obtiene servicio de programación"""
        return self._services['programacion']
    
    @classmethod
    def reset(cls):
        """Resetea la instancia (útil para testing)"""
        cls._instance = None
