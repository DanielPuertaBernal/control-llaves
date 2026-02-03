"""Interfaz de repositorio de llaves"""
from abc import ABC, abstractmethod
import pandas as pd


class LlaveRepository(ABC):
    @abstractmethod
    def registrar_entrega(self, info_clase: dict) -> bool:
        raise NotImplementedError

    @abstractmethod
    def registrar_devolucion(self, nroidenti: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def obtener_llaves_pendientes(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def obtener_clases_procesadas_hoy(self, fecha_actual):
        raise NotImplementedError

    @abstractmethod
    def obtener_llaves_prestadas_dia(self, fecha_actual):
        raise NotImplementedError

    @abstractmethod
    def obtener_historial_completo(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def evaluar_retraso_entrega(self, horario: str) -> bool:
        """Evalúa si hay retraso en entrega (> 1 hora después de fin de clase)"""
        raise NotImplementedError
