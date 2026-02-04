"""
Implementación del repositorio de Préstamos con MongoDB
"""
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from domain.prestamo import Préstamo
from interfaces.prestamo_repository import PréstamoRepository
from infrastructure.services.mongo_client import MongoClient


class PréstamoMongoRepository(PréstamoRepository):
    """Repositorio de préstamos en MongoDB"""
    
    COLECCION = "prestamos"
    
    def __init__(self, mongo_client: MongoClient = None):
        self.client = mongo_client or MongoClient()
        self.db = self.client.get_database()
        self.collection = self.db[self.COLECCION]
    
    def crear(self, prestamo: Préstamo) -> Préstamo:
        """Crea un nuevo préstamo"""
        prestamo.fecha_creacion = datetime.now()
        prestamo.fecha_actualizacion = datetime.now()
        
        resultado = self.collection.insert_one(prestamo.to_dict())
        prestamo.id = resultado.inserted_id
        
        return prestamo
    
    def obtener_por_id(self, prestamo_id: ObjectId) -> Optional[Préstamo]:
        """Obtiene un préstamo por ID"""
        doc = self.collection.find_one({"_id": prestamo_id})
        return Préstamo.from_dict(doc) if doc else None
    
    def obtener_todos(self) -> List[Préstamo]:
        """Obtiene todos los préstamos"""
        docs = self.collection.find().sort("fecha_prestamo", -1)
        return [Préstamo.from_dict(doc) for doc in docs]
    
    def obtener_activos(self) -> List[Préstamo]:
        """Obtiene solo préstamos activos"""
        docs = self.collection.find({
            "estado": {"$in": ["activo", "parcialmente_devuelto"]}
        }).sort("fecha_prestamo", -1)
        return [Préstamo.from_dict(doc) for doc in docs]
    
    def obtener_por_docente_nfc(self, codigo_nfc: str) -> List[Préstamo]:
        """Obtiene todos los préstamos de un docente"""
        docs = self.collection.find({
            "docente_codigo_nfc": codigo_nfc
        }).sort("fecha_prestamo", -1)
        return [Préstamo.from_dict(doc) for doc in docs]
    
    def obtener_activos_por_docente(self, codigo_nfc: str) -> List[Préstamo]:
        """Obtiene préstamos activos de un docente"""
        docs = self.collection.find({
            "docente_codigo_nfc": codigo_nfc,
            "estado": {"$in": ["activo", "parcialmente_devuelto"]}
        }).sort("fecha_prestamo", -1)
        return [Préstamo.from_dict(doc) for doc in docs]
    
    def actualizar(self, prestamo: Préstamo) -> bool:
        """Actualiza un préstamo"""
        prestamo.fecha_actualizacion = datetime.now()
        
        resultado = self.collection.update_one(
            {"_id": prestamo.id},
            {"$set": prestamo.to_dict()}
        )
        
        return resultado.modified_count > 0
    
    def buscar(self, criterios: dict) -> List[Préstamo]:
        """Busca préstamos según criterios"""
        docs = self.collection.find(criterios).sort("fecha_prestamo", -1)
        return [Préstamo.from_dict(doc) for doc in docs]
