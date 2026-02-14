"""
Vista de Estadísticas para Administrador - Versión Simplificada
Muestra solo métricas esenciales para tomar decisiones
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from application.helpers import TimeHelper


class AdminAnalyticsView:
    """Vista de estadísticas simplificada para administradores"""

    def __init__(self, parent_frame, historial_controller):
        self.historial_controller = historial_controller
        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)
        self.df_base = None
        self._crear_interfaz()
        self._cargar_datos()

    def _crear_interfaz(self):
        """Crea la interfaz simplificada"""
        # Header
        header = ttk.Frame(self.frame)
        header.pack(fill='x', pady=(0, 16))
        ttk.Label(header, text="Estadísticas Esenciales", font=('Segoe UI', 14, 'bold')).pack(side='left')
        ttk.Button(header, text="🔄 Actualizar", command=self._cargar_datos).pack(side='right')

        # KPIs principales (4 métricas esenciales)
        kpis = ttk.Frame(self.frame)
        kpis.pack(fill='x', pady=(0, 16))

        self.lbl_total = self._crear_kpi(kpis, "Total de préstamos", "0")
        self.lbl_activos = self._crear_kpi(kpis, "En préstamo actualmente", "0")
        self.lbl_puntualidad = self._crear_kpi(kpis, "Puntualidad general", "0%")
        self.lbl_promedio_retraso = self._crear_kpi(kpis, "Retraso promedio", "0 min")

        # Problemas detectados (docentes impuntuales)
        ttk.Label(self.frame, text="⚠️ Docentes con retrasos frecuentes", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(8, 4))
        
        frame_impuntuales = ttk.Frame(self.frame)
        frame_impuntuales.pack(fill='both', expand=True, pady=(0, 12))
        
        self.tree_impuntuales = ttk.Treeview(frame_impuntuales, columns=("Docente", "Retraso Promedio", "Casos"), show="headings", height=5)
        self.tree_impuntuales.heading("Docente", text="Docente")
        self.tree_impuntuales.heading("Retraso Promedio", text="Retraso Promedio")
        self.tree_impuntuales.heading("Casos", text="Casos con retraso")
        self.tree_impuntuales.column("Docente", width=300)
        self.tree_impuntuales.column("Retraso Promedio", width=150, anchor='center')
        self.tree_impuntuales.column("Casos", width=100, anchor='center')
        self.tree_impuntuales.pack(fill='both', expand=True)

        # Llaves pendientes
        ttk.Label(self.frame, text="📌 Llaves pendientes por docente", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(8, 4))
        
        frame_pendientes = ttk.Frame(self.frame)
        frame_pendientes.pack(fill='both', expand=True)
        
        self.tree_pendientes = ttk.Treeview(frame_pendientes, columns=("Docente", "Llaves Pendientes"), show="headings", height=5)
        self.tree_pendientes.heading("Docente", text="Docente")
        self.tree_pendientes.heading("Llaves Pendientes", text="Cantidad")
        self.tree_pendientes.column("Docente", width=350)
        self.tree_pendientes.column("Llaves Pendientes", width=100, anchor='center')
        self.tree_pendientes.pack(fill='both', expand=True)

    def _crear_kpi(self, parent, titulo, valor):
        """Crea una tarjeta KPI simple"""
        card = ttk.Frame(parent)
        card.pack(side='left', padx=8, fill='both', expand=True)
        ttk.Label(card, text=titulo, font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        lbl_valor = ttk.Label(card, text=valor, font=('Segoe UI', 16, 'bold'), foreground="#1976D2")
        lbl_valor.pack(anchor='w')
        return lbl_valor

    def _cargar_datos(self):
        """Carga y actualiza todos los datos"""
        self.df_base = self.historial_controller.obtener_historial_completo()
        if self.df_base is None or self.df_base.empty:
            return

        stats = self.historial_controller.obtener_estadisticas_avanzadas(self.df_base)

        # Actualizar KPIs
        self.lbl_total.config(text=str(stats.get('total_registros', 0)))
        self.lbl_activos.config(text=str(stats.get('prestamos_activos', 0)))
        self.lbl_puntualidad.config(text=f"{stats.get('porcentaje_puntual', 0)}%")
        self.lbl_promedio_retraso.config(text=TimeHelper.minutes_to_hhmm(stats.get('promedio_retraso_entrega_min', 0)))

        # Docentes impuntuales (máximo 5)
        docentes_impuntuales = stats.get('docentes_impuntuales', [])[:5]
        self._llenar_tree(self.tree_impuntuales, [
            (d['docente'], TimeHelper.minutes_to_hhmm(d.get('promedio_retraso', 0)), d.get('total_retrasos', 0))
            for d in docentes_impuntuales
        ])

        # Docentes con llaves pendientes (máximo 5)
        docentes_pendientes = stats.get('docentes_deben', [])[:5]
        self._llenar_tree(self.tree_pendientes, [
            (d['docente'], d['pendientes'])
            for d in docentes_pendientes
        ])

    def _llenar_tree(self, tree: ttk.Treeview, rows):
        """Llena un treeview con datos"""
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert('', 'end', values=row)
