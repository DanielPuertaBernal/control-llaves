"""
Service Factory - Patrón Singleton para gestión de servicios
Implementa inyección de dependencias centralizada
"""
from application.services.docente_service import DocenteService
from application.services.llave_service import LlaveService
from application.services.historial_service import HistorialService
from application.services.programacion_service import ProgramacionService
from application.services.auth_service import AuthService
from application.services.equipo_service import EquipoService
from application.services.prestamo_service import PréstamoService
from application.services.devolucion_service import DevolucionService
from infrastructure.repositories.docente_mongo_repository import DocenteMongoRepository
from infrastructure.repositories.llave_mongo_repository import LlaveMongoRepository
from infrastructure.repositories.programacion_mongo_repository import ProgramacionMongoRepository
from infrastructure.repositories.usuario_mongo_repository import UsuarioMongoRepository
from infrastructure.repositories.equipo_mongo_repository import EquipoMongoRepository
from infrastructure.repositories.prestamo_mongo_repository import PréstamoMongoRepository
from infrastructure.repositories.devolucion_mongo_repository import DevolucionMongoRepository


class ServiceFactory:
    """Singleton Factory para crear servicios con dependencias inyectadas"""
    
    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceFactory, cls).__new__(cls)
            cls._instance._inicializar()
        return cls._instance
    
    def _inicializar(self):
        """Inicializa repositorios y servicios (ejecutado una sola vez)"""
        # Crear repositories
        self._docente_repo = DocenteMongoRepository()
        self._llave_repo = LlaveMongoRepository()
        self._programacion_repo = ProgramacionMongoRepository()
        self._usuario_repo = UsuarioMongoRepository()
        self._equipo_repo = EquipoMongoRepository()
        self._prestamo_repo = PréstamoMongoRepository()
        self._devolucion_repo = DevolucionMongoRepository()
        
        # Crear servicios con inyección de dependencias
        self._services['docente'] = DocenteService(self._docente_repo)
        self._services['llave'] = LlaveService(self._llave_repo)
        self._services['auth'] = AuthService(self._usuario_repo)
        self._services['historial'] = HistorialService(self._llave_repo)
        
        # ProgramacionService depende de llave_service
        self._services['programacion'] = ProgramacionService(
            self._programacion_repo,
            self._services['llave']
        )
        
        # Servicios de equipos
        self._services['equipo'] = EquipoService(self._equipo_repo)
        self._services['prestamo'] = PréstamoService(self._prestamo_repo, self._equipo_repo)
        self._services['devolucion'] = DevolucionService(
            self._devolucion_repo, 
            self._prestamo_repo, 
            self._equipo_repo
        )
    
    def get_docente_service(self) -> DocenteService:
        return self._services['docente']
    
    def get_llave_service(self) -> LlaveService:
        return self._services['llave']
    
    def get_historial_service(self) -> HistorialService:
        return self._services['historial']
    
    def get_auth_service(self) -> AuthService:
        return self._services['auth']
    
    def get_programacion_service(self) -> ProgramacionService:
        return self._services['programacion']
    
    def get_equipo_service(self) -> EquipoService:
        return self._services['equipo']
    
    def get_prestamo_service(self) -> PréstamoService:
        return self._services['prestamo']
    
    def get_devolucion_service(self) -> DevolucionService:
        return self._services['devolucion']

    
    def get_devolucion_service(self) -> DevolucionService:
        return self._services['devolucion']
    
    @classmethod
    def reset(cls):
        """Resetea la instancia (útil para testing)"""
        cls._instance = None
