"""Repositorio Mongo para docentes"""
from interfaces.docente_repository import DocenteRepository
from services.mongo_client import MongoClientProvider
import pandas as pd


class DocenteMongoRepository(DocenteRepository):
    def __init__(self):
        self.collection = MongoClientProvider.get_collection("docentes")
        self._asegurar_indices()

    def _asegurar_indices(self):
        try:
            self.collection.create_index("Numero de documento", unique=True)
            self.collection.create_index("Id Carnet", unique=True, sparse=True)
        except Exception:
            pass

    def guardar_docentes(self, df: pd.DataFrame):
        try:
            if df is None or df.empty:
                return False, "❌ No hay datos para guardar"

            registros = df.to_dict('records')
            for docente in registros:
                self.collection.update_one(
                    {"Numero de documento": docente.get("Numero de documento")},
                    {"$set": docente},
                    upsert=True
                )
            return True, f"✅ Información guardada en MongoDB: {len(registros)} registros"
        except Exception as e:
            return False, f"❌ Error al guardar: {str(e)}"

    def obtener_docentes(self) -> pd.DataFrame:
        try:
            registros = list(self.collection.find({}, {"_id": 0}))
            return pd.DataFrame(registros)
        except Exception as e:
            print(f"Error al obtener docentes: {e}")
            return pd.DataFrame()

    def buscar_docente_por_documento(self, numero_documento: str):
        try:
            doc_limpio = str(numero_documento).replace('.0', '').strip()
            docente = self.collection.find_one({"Numero de documento": doc_limpio}, {"_id": 0})
            return docente
        except Exception as e:
            print(f"Error al buscar docente: {e}")
            return None

    def buscar_docente_por_carnet(self, id_carnet: str):
        try:
            carnet_limpio = str(id_carnet).strip().upper()
            docente = self.collection.find_one({"Id Carnet": carnet_limpio}, {"_id": 0})
            return docente
        except Exception as e:
            print(f"Error al buscar docente por carnet: {e}")
            return None
