"""Casos de uso para historial de llaves"""
import pandas as pd
from typing import Optional, List, Dict
from interfaces.llave_repository import LlaveRepository
from application.helpers import TimeHelper, DateHelper


class HistorialService:
    def __init__(self, repository: LlaveRepository):
        self.repository = repository

    def obtener_historial_completo(self):
        return self.repository.obtener_historial_completo()

    def filtrar_por_fecha(self, fecha_inicio, fecha_fin, historial_df=None):
        if historial_df is None:
            historial_df = self.repository.obtener_historial_completo()

        return DateHelper.filtrar_por_rango(
            historial_df,
            'Fecha de entrega',
            fecha_inicio,
            fecha_fin
        )

    def filtrar_historial(
        self,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        facultad: Optional[str] = None,
        docente: Optional[str] = None,
        historial_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Filtra el historial por rango de fechas, facultad y/o docente"""
        if historial_df is None:
            historial_df = self.repository.obtener_historial_completo()

        if historial_df.empty:
            return historial_df

        resultado = historial_df.copy()

        # Filtrado por fechas (sobre Fecha de entrega)
        if fecha_inicio or fecha_fin:
            resultado = DateHelper.filtrar_por_rango(
                resultado,
                'Fecha de entrega',
                fecha_inicio,
                fecha_fin
            )

        # Filtrado por facultad
        if facultad and facultad.strip() and facultad != "Todas":
            if 'Facultad' in resultado.columns:
                resultado = resultado[resultado['Facultad'].astype(str).str.contains(facultad, case=False, na=False)]

        # Filtrado por docente
        if docente and docente.strip():
            if 'Docente' in resultado.columns:
                resultado = resultado[resultado['Docente'].astype(str).str.contains(docente, case=False, na=False)]

        return resultado

    def obtener_facultades(self, historial_df: Optional[pd.DataFrame] = None) -> List[str]:
        if historial_df is None:
            historial_df = self.repository.obtener_historial_completo()
        if historial_df.empty or 'Facultad' not in historial_df.columns:
            return []
        return sorted([f for f in historial_df['Facultad'].dropna().unique().tolist() if str(f).strip()])

    def exportar_excel(self, historial_df: pd.DataFrame, ruta_guardado: str) -> None:
        """Exporta el DataFrame a Excel"""
        historial_df.to_excel(ruta_guardado, index=False, engine='openpyxl')

    def obtener_estadisticas_avanzadas(self, historial_df: Optional[pd.DataFrame] = None) -> Dict[str, object]:
        """Calcula estadísticas avanzadas a partir del historial"""
        if historial_df is None:
            historial_df = self.repository.obtener_historial_completo()

        if historial_df.empty:
            return {
                'total_registros': 0,
                'prestamos_activos': 0,
                'promedio_retraso_entrega_min': 0,
                'porcentaje_puntual': 0,
                'facultades_puntuales': [],
                'docentes_deben': [],
                'docentes_impuntuales': []
            }

        total_registros = len(historial_df)
        prestamos_activos = len(historial_df[historial_df.get('Estado', '') == 'En Préstamo']) if 'Estado' in historial_df.columns else 0

        # Promedio de retraso en entrega (Tiempo de retraso HH:MM:SS)
        promedio_retraso_min = 0
        if 'Tiempo de retraso' in historial_df.columns:
            retrasos_seg = []
            for valor in historial_df['Tiempo de retraso'].astype(str).tolist():
                segundos = TimeHelper.hhmmss_to_seconds(valor)
                if segundos is not None:
                    retrasos_seg.append(segundos)
            if retrasos_seg:
                promedio_retraso_min = round((sum(retrasos_seg) / len(retrasos_seg)) / 60, 2)

        # Puntualidad general
        porcentaje_puntual = 0
        if 'Se reclamó a tiempo' in historial_df.columns:
            serie = historial_df['Se reclamó a tiempo'].astype(str).str.strip().str.lower()
            puntuales = serie == 'sí'
            if len(serie) > 0:
                porcentaje_puntual = round((puntuales.sum() / len(serie)) * 100, 2)

        # Facultades más puntuales
        facultades_puntuales = []
        if 'Facultad' in historial_df.columns and 'Se reclamó a tiempo' in historial_df.columns:
            df_fac = historial_df.copy()
            df_fac['puntual'] = df_fac['Se reclamó a tiempo'].astype(str).str.strip().str.lower() == 'sí'
            agrupado = df_fac.groupby('Facultad')['puntual'].agg(['mean', 'count']).reset_index()
            agrupado['puntualidad'] = (agrupado['mean'] * 100).round(2)
            agrupado = agrupado.sort_values(by='puntualidad', ascending=False)
            facultades_puntuales = [
                {
                    'facultad': row['Facultad'],
                    'puntualidad': row['puntualidad'],
                    'total': int(row['count'])
                }
                for _, row in agrupado.iterrows()
            ]

        # Docentes con llaves pendientes
        docentes_deben = []
        if 'Estado' in historial_df.columns and 'Docente' in historial_df.columns:
            df_pend = historial_df[historial_df['Estado'] == 'En Préstamo']
            if not df_pend.empty:
                top_deben = df_pend.groupby('Docente').size().sort_values(ascending=False)
                docentes_deben = [
                    {'docente': idx, 'pendientes': int(cant)}
                    for idx, cant in top_deben.items()
                ]

        # Docentes más impuntuales (por promedio de retraso)
        docentes_impuntuales = []
        if 'Docente' in historial_df.columns and 'Tiempo de retraso' in historial_df.columns:
            # Calcular promedio de retraso por docente
            df_con_retraso = historial_df.copy()
            
            # Convertir tiempo de retraso a segundos
            df_con_retraso['retraso_segundos'] = df_con_retraso['Tiempo de retraso'].apply(
                lambda x: TimeHelper.hhmmss_to_seconds(str(x)) if pd.notna(x) else None
            )
            
            # Filtrar solo registros con retraso válido (mayor a 0)
            df_con_retraso = df_con_retraso[
                (df_con_retraso['retraso_segundos'].notna()) & 
                (df_con_retraso['retraso_segundos'] > 0)
            ]
            
            if not df_con_retraso.empty:
                # Calcular promedio de retraso en minutos por docente
                promedio_por_docente = df_con_retraso.groupby('Docente')['retraso_segundos'].agg(['mean', 'count'])
                promedio_por_docente['promedio_min'] = (promedio_por_docente['mean'] / 60).round(2)
                promedio_por_docente = promedio_por_docente.sort_values(by='promedio_min', ascending=False)
                
                docentes_impuntuales = [
                    {
                        'docente': idx,
                        'promedio_retraso': float(row['promedio_min']),
                        'total_retrasos': int(row['count'])
                    }
                    for idx, row in promedio_por_docente.iterrows()
                ]

        return {
            'total_registros': total_registros,
            'prestamos_activos': prestamos_activos,
            'promedio_retraso_entrega_min': promedio_retraso_min,
            'porcentaje_puntual': porcentaje_puntual,
            'facultades_puntuales': facultades_puntuales,
            'docentes_deben': docentes_deben,
            'docentes_impuntuales': docentes_impuntuales
        }


