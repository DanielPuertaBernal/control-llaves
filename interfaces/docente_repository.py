"""Interfaz de repositorio de docentes"""
from abc import ABC, abstractmethod
import pandas as pd


class DocenteRepository(ABC):
    @abstractmethod
    def guardar_docentes(self, df: pd.DataFrame):
        raise NotImplementedError

    @abstractmethod
    def obtener_docentes(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def buscar_docente_por_documento(self, numero_documento: str):
        raise NotImplementedError

    @abstractmethod
    def buscar_docente_por_carnet(self, id_carnet: str):
        raise NotImplementedError
