"""Interfaz de repositorio de programación"""
from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class ProgramacionRepository(ABC):
    @abstractmethod
    def cargar_programacion_guardada(self):
        raise NotImplementedError

    @abstractmethod
    def obtener_programacion_actual(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def obtener_clases_del_dia(self, dia: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def guardar_programacion(self, df: pd.DataFrame):
        raise NotImplementedError
