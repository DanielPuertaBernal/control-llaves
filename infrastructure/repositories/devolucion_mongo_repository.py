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
    
    def obtener_por_id(self, devolucion_id: ObjectId) -> Optional[Devolución]:
        """Obtiene una devolución por ID"""
        doc = self.collection.find_one({"_id": devolucion_id})
        return Devolución.from_dict(doc) if doc else None
    
    def obtener_todos(self) -> List[Devolución]:
        """Obtiene todas las devoluciones"""
        docs = self.collection.find().sort("fecha_devolucion", -1)
        return [Devolución.from_dict(doc) for doc in docs]
    
    def obtener_por_prestamo(self, prestamo_id: ObjectId) -> List[Devolución]:
        """Obtiene todas las devoluciones de un préstamo"""
        docs = self.collection.find({
            "prestamo_id": prestamo_id
        }).sort("fecha_devolucion", -1)
        return [Devolución.from_dict(doc) for doc in docs]
    
    def obtener_por_docente_nfc(self, codigo_nfc: str) -> List[Devolución]:
        """Obtiene todas las devoluciones de un docente"""
        docs = self.collection.find({
            "docente_codigo_nfc": codigo_nfc
        }).sort("fecha_devolucion", -1)
        return [Devolución.from_dict(doc) for doc in docs]
    
    def buscar(self, criterios: dict) -> List[Devolución]:
        """Busca devoluciones según criterios"""
        docs = self.collection.find(criterios).sort("fecha_devolucion", -1)
        return [Devolución.from_dict(doc) for doc in docs]
