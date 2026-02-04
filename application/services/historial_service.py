"""Casos de uso para historial de llaves"""
import pandas as pd
from typing import Optional, List, Dict
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
            if 'Fecha de entrega' in resultado.columns:
                resultado['fecha_temp'] = pd.to_datetime(resultado['Fecha de entrega'], errors='coerce')

                if fecha_inicio:
                    fecha_inicio_dt = pd.to_datetime(fecha_inicio)
                    resultado = resultado[resultado['fecha_temp'] >= fecha_inicio_dt]

                if fecha_fin:
                    fecha_fin_dt = pd.to_datetime(fecha_fin)
                    resultado = resultado[resultado['fecha_temp'] <= fecha_fin_dt]

                resultado = resultado.drop('fecha_temp', axis=1)

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

    def obtener_docentes(self, historial_df: Optional[pd.DataFrame] = None) -> List[str]:
        if historial_df is None:
            historial_df = self.repository.obtener_historial_completo()
        if historial_df.empty or 'Docente' not in historial_df.columns:
            return []
        return sorted([d for d in historial_df['Docente'].dropna().unique().tolist() if str(d).strip()])

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
                segundos = self._parse_hhmmss_to_seconds(valor)
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
                lambda x: self._parse_hhmmss_to_seconds(str(x)) if pd.notna(x) else None
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

    @staticmethod
    def _parse_hhmmss_to_seconds(valor: str) -> Optional[int]:
        """Convierte un string HH:MM:SS a segundos"""
        if valor is None:
            return None
        valor = str(valor).strip()
        if not valor or valor.lower() == 'n/a':
            return None
        if valor == '0':
            return 0
        if ':' not in valor:
            return None
        partes = valor.split(':')
        if len(partes) != 3:
            return None
        try:
            horas = int(partes[0])
            minutos = int(partes[1])
            segundos = int(partes[2])
            return horas * 3600 + minutos * 60 + segundos
        except ValueError:
            return None
