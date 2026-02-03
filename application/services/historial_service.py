"""Casos de uso para historial de llaves"""
import pandas as pd
from interfaces.llave_repository import LlaveRepository


class HistorialService:
    def __init__(self, repository: LlaveRepository):
        self.repository = repository

    def obtener_historial_completo(self):
        return self.repository.obtener_historial_completo()

    def obtener_prestamos_activos(self):
        return self.repository.obtener_llaves_pendientes()

    def buscar_en_historial(self, termino, historial_df=None):
        if historial_df is None:
            historial_df = self.repository.obtener_historial_completo()

        if historial_df.empty or not termino:
            return historial_df

        termino = termino.strip().lower()
        mascara_busqueda = pd.Series([False] * len(historial_df))

        columnas_busqueda = ['Número de Documento', 'Docente', 'Aula', 'Materia de la Clase']

        for columna in columnas_busqueda:
            if columna in historial_df.columns:
                mascara_busqueda |= historial_df[columna].astype(str).str.lower().str.contains(termino, na=False)

        return historial_df[mascara_busqueda]

    def filtrar_por_estado(self, estado, historial_df=None):
        if historial_df is None:
            historial_df = self.repository.obtener_historial_completo()

        if historial_df.empty or 'Estado' not in historial_df.columns:
            return historial_df

        return historial_df[historial_df['Estado'] == estado]

    def filtrar_por_fecha(self, fecha_inicio, fecha_fin, historial_df=None):
        if historial_df is None:
            historial_df = self.repository.obtener_historial_completo()

        if historial_df.empty or 'Fecha de entrega' not in historial_df.columns:
            return historial_df

        try:
            historial_df['fecha_temp'] = pd.to_datetime(historial_df['Fecha de entrega'], errors='coerce')
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            fecha_fin_dt = pd.to_datetime(fecha_fin)

            resultado = historial_df[
                (historial_df['fecha_temp'] >= fecha_inicio_dt) &
                (historial_df['fecha_temp'] <= fecha_fin_dt)
            ].drop('fecha_temp', axis=1)

            return resultado

        except Exception as e:
            print(f"Error al filtrar por fecha: {e}")
            return historial_df

    def obtener_estadisticas(self):
        historial = self.repository.obtener_historial_completo()
        prestamos_activos = self.repository.obtener_llaves_pendientes()

        return {
            'total_registros': len(historial),
            'prestamos_activos': len(prestamos_activos),
            'llaves_devueltas': len(historial[historial['Estado'] == 'Devuelta']) if not historial.empty else 0,
            'docentes_unicos': historial['Docente'].nunique() if not historial.empty else 0
        }
