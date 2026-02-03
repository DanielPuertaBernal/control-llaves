"""Repositorio Mongo para programación"""
from interfaces.programacion_repository import ProgramacionRepository
from services.mongo_client import MongoClientProvider
from typing import Optional
from datetime import datetime, time
import pandas as pd


class ProgramacionMongoRepository(ProgramacionRepository):
    def __init__(self):
        self.collection = MongoClientProvider.get_collection("programacion")

    def cargar_programacion_guardada(self):
        try:
            registros = list(self.collection.find({}, {"_id": 0}))
            if not registros:
                return False, None, "❌ No hay programación guardada"
            df = pd.DataFrame(registros)
            mensaje = f"✅ Programación cargada: {len(df)} registros"
            return True, df, mensaje
        except Exception as e:
            return False, None, f"❌ Error al cargar: {str(e)}"

    def obtener_programacion_actual(self) -> pd.DataFrame:
        try:
            registros = list(self.collection.find({}, {"_id": 0}))
            return pd.DataFrame(registros)
        except Exception as e:
            print(f"Error al obtener programación: {e}")
            return pd.DataFrame()

    def obtener_clases_del_dia(self, dia: Optional[str] = None) -> pd.DataFrame:
        df = self.obtener_programacion_actual()
        if df.empty:
            return df
        if dia is None:
            return df
        try:
            return df[df['Día'] == dia].copy()
        except Exception:
            return pd.DataFrame()

    def guardar_programacion(self, df: pd.DataFrame):
        try:
            if df is None or df.empty:
                return False, "❌ No hay programación para guardar"

            registros = df.to_dict('records')
            version_carga = datetime.utcnow()
            for registro in registros:
                for key, value in list(registro.items()):
                    if isinstance(value, time):
                        registro[key] = value.strftime('%H:%M:%S')
                    elif isinstance(value, datetime):
                        registro[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                registro["version_carga"] = version_carga

            self.collection.delete_many({})
            if registros:
                self.collection.insert_many(registros)

            return True, f"✅ Programación guardada en MongoDB: {len(registros)} registros"
        except Exception as e:
            return False, f"❌ Error al guardar: {str(e)}"
