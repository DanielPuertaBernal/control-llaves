"""
Implementación del repositorio de Equipos con MongoDB
"""
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from domain.equipo import Equipo
from interfaces.equipo_repository import EquipoRepository
from infrastructure.services.mongo_client import MongoClient


class EquipoMongoRepository(EquipoRepository):
    """Repositorio de equipos en MongoDB"""
    
    COLECCION = "equipos"
    
    def __init__(self, mongo_client: MongoClient = None):
        self.client = mongo_client or MongoClient()
        self.db = self.client.get_database()
        self.collection = self.db[self.COLECCION]
    
    def crear(self, equipo: Equipo) -> Equipo:
        """Crea un nuevo equipo"""
        equipo.fecha_creacion = datetime.now()
        equipo.fecha_actualizacion = datetime.now()
        
        resultado = self.collection.insert_one(equipo.to_dict())
        equipo.id = resultado.inserted_id
        
        return equipo
    
    def obtener_por_id(self, equipo_id: ObjectId) -> Optional[Equipo]:
        """Obtiene un equipo por ID"""
        doc = self.collection.find_one({"_id": equipo_id})
        return Equipo.from_dict(doc) if doc else None
    
    def obtener_por_codigo(self, codigo_inventario: str) -> Optional[Equipo]:
        """Obtiene un equipo por código de inventario"""
        doc = self.collection.find_one({"codigo_inventario": codigo_inventario})
        return Equipo.from_dict(doc) if doc else None
    
    def obtener_todos(self) -> List[Equipo]:
        """Obtiene todos los equipos"""
        docs = self.collection.find({"estado": "activo"}).sort("nombre", 1)
        return [Equipo.from_dict(doc) for doc in docs]
    
    def obtener_disponibles(self) -> List[Equipo]:
        """Obtiene solo equipos disponibles"""
        docs = self.collection.find({
            "estado": "activo",
            "cantidad_disponible": {"$gt": 0}
        }).sort("nombre", 1)
        return [Equipo.from_dict(doc) for doc in docs]
    
    def actualizar(self, equipo: Equipo) -> bool:
        """Actualiza un equipo"""
        equipo.fecha_actualizacion = datetime.now()
        
        resultado = self.collection.update_one(
            {"_id": equipo.id},
            {"$set": equipo.to_dict()}
        )
        
        return resultado.modified_count > 0
    
    def eliminar(self, equipo_id: ObjectId) -> bool:
        """Marca un equipo como inactivo (soft delete)"""
        resultado = self.collection.update_one(
            {"_id": equipo_id},
            {
                "$set": {
                    "estado": "descartado",
                    "fecha_actualizacion": datetime.now()
                }
            }
        )
        
        return resultado.modified_count > 0
    
    def buscar(self, criterios: dict) -> List[Equipo]:
        """Busca equipos según criterios"""
        criterios_bd = {**criterios, "estado": "activo"}
        docs = self.collection.find(criterios_bd).sort("nombre", 1)
        return [Equipo.from_dict(doc) for doc in docs]
