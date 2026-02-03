"""
Cliente MongoDB centralizado
Gestiona conexión y acceso a la base de datos
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient


# Carga automática desde .env (sin rutas hardcodeadas)
load_dotenv()


class MongoClientProvider:
    """Singleton para cliente Mongo"""

    _client = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI no está configurado.")
            cls._client = MongoClient(mongo_uri)
        return cls._client

    @classmethod
    def get_db(cls):
        db_name = os.getenv("MONGO_DB")
        if not db_name:
            raise ValueError("MONGO_DB no está configurado.")
        return cls.get_client()[db_name]

    @classmethod
    def get_collection(cls, name: str):
        return cls.get_db()[name]
