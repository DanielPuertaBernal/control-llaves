"""
Implementación del repositorio de Devoluciones con MongoDB
"""
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from domain.devolucion import Devolución
from interfaces.devolucion_repository import DevolucionRepository
from infrastructure.services.mongo_client import MongoClientProvider


class DevolucionMongoRepository(DevolucionRepository):
    """Repositorio de devoluciones en MongoDB"""
    
    COLECCION = "devoluciones"
    
    def __init__(self):
        self.collection = MongoClientProvider.get_collection(self.COLECCION)
    
    def crear(self, devolucion: Devolución) -> Devolución:
        """Crea una nueva devolución"""
        devolucion.fecha_creacion = datetime.now()
        
        resultado = self.collection.insert_one(devolucion.to_dict())
        devolucion.id = resultado.inserted_id
        
        return devolucion

