"""
Vista de Estadísticas para Administrador
Muestra estadísticas generales o del día
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from application.helpers import TimeHelper


class AdminAnalyticsView:
    """Vista de estadísticas para administradores"""

    def __init__(self, parent_frame, historial_controller):
        self.historial_controller = historial_controller
        self.modo_actual = "general"  # "general" o "dia"

        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)

        self.df_base = None

        self._crear_interfaz()
        self._cargar_datos_base()

    def _crear_interfaz(self):
        # Header con botones
        header = ttk.Frame(self.frame)
        header.pack(fill='x', pady=(0, 12))

        ttk.Label(header, text="Estadísticas de Llaves", font=('Segoe UI', 12, 'bold')).pack(side='left')

        btn_refrescar = ttk.Button(header, text="🔄 Actualizar", command=self._cargar_datos_base)
        btn_refrescar.pack(side='right', padx=(12, 0))

        btn_dia = ttk.Button(header, text="📅 Hoy", command=lambda: self._cambiar_modo("dia"))
        btn_dia.pack(side='right', padx=6)

        btn_general = ttk.Button(header, text="📈 General", command=lambda: self._cambiar_modo("general"))
        btn_general.pack(side='right')

        # Tarjetas resumen
        resumen = ttk.Frame(self.frame)
        resumen.pack(fill='x', pady=(0, 12))

        self.lbl_total = self._crear_tarjeta(resumen, "Total registros", "0")
        self.lbl_activos = self._crear_tarjeta(resumen, "Préstamos activos", "0")
        self.lbl_promedio = self._crear_tarjeta(resumen, "Prom. retraso entrega", "0 min")
        self.lbl_puntual = self._crear_tarjeta(resumen, "% Puntualidad", "0%")

        # Tablas de ranking
        rankings = ttk.Frame(self.frame)
        rankings.pack(fill='both', expand=True)

        # Facultades puntuales
        frame_fac = ttk.LabelFrame(rankings, text="Facultades más puntuales")
        frame_fac.pack(side='left', fill='both', expand=True, padx=(0, 8))
        self.tree_fac = ttk.Treeview(frame_fac, columns=("Facultad", "Puntualidad", "Total"), show="headings", height=8)
        self.tree_fac.heading("Facultad", text="Facultad")
        self.tree_fac.heading("Puntualidad", text="Puntualidad")
        self.tree_fac.heading("Total", text="Total")
        self.tree_fac.column("Facultad", width=180)
        self.tree_fac.column("Puntualidad", width=100, anchor='center')
        self.tree_fac.column("Total", width=60, anchor='center')
        self.tree_fac.pack(fill='both', expand=True, padx=8, pady=8)

        # Docentes con más llaves pendientes
        frame_deben = ttk.LabelFrame(rankings, text="Docentes con más llaves pendientes")
        frame_deben.pack(side='left', fill='both', expand=True, padx=8)
        self.tree_deben = ttk.Treeview(frame_deben, columns=("Docente", "Pendientes"), show="headings", height=8)
        self.tree_deben.heading("Docente", text="Docente")
        self.tree_deben.heading("Pendientes", text="Pendientes")
        self.tree_deben.column("Docente", width=200)
        self.tree_deben.column("Pendientes", width=80, anchor='center')
        self.tree_deben.pack(fill='both', expand=True, padx=8, pady=8)

        # Docentes más impuntuales
        frame_imp = ttk.LabelFrame(rankings, text="Docentes más impuntuales")
        frame_imp.pack(side='left', fill='both', expand=True, padx=(8, 0))
        self.tree_imp = ttk.Treeview(frame_imp, columns=("Docente", "Promedio"), show="headings", height=8)
        self.tree_imp.heading("Docente", text="Docente")
        self.tree_imp.heading("Promedio", text="Promedio (HH:MM)")
        self.tree_imp.column("Docente", width=200)
        self.tree_imp.column("Promedio", width=100, anchor='center')
        self.tree_imp.pack(fill='both', expand=True, padx=8, pady=8)

    def _cambiar_modo(self, modo):
        self.modo_actual = modo
        self._aplicar_filtros()

    def _crear_tarjeta(self, parent, titulo, valor):
        card = ttk.Frame(parent, padding="10")
        card.pack(side='left', padx=6, fill='x', expand=True)
        ttk.Label(card, text=titulo, font=('Segoe UI', 9)).pack(anchor='w')
        lbl_valor = ttk.Label(card, text=valor, font=('Segoe UI', 14, 'bold'))
        lbl_valor.pack(anchor='w')
        return lbl_valor

    def _cargar_datos_base(self):
        self.df_base = self.historial_controller.obtener_historial_completo()
        self._aplicar_filtros()

    def _aplicar_filtros(self):
        """Filtra datos según modo (general o día)"""
        if self.df_base is None or self.df_base.empty:
            return

        df_filtrado = self.df_base.copy()

        # Si modo es "dia", filtrar por fecha actual
        if self.modo_actual == "dia":
            hoy = datetime.now().strftime('%Y-%m-%d')
            if 'Fecha de entrega' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Fecha de entrega'].astype(str).str.contains(hoy, na=False)]

        self._actualizar_estadisticas(df_filtrado)

    def _actualizar_estadisticas(self, df_datos):
        stats = self.historial_controller.obtener_estadisticas_avanzadas(df_datos)

        self.lbl_total.config(text=str(stats['total_registros']))
        self.lbl_activos.config(text=str(stats['prestamos_activos']))
        self.lbl_promedio.config(text=TimeHelper.minutes_to_hhmm(stats['promedio_retraso_entrega_min']))
        self.lbl_puntual.config(text=f"{stats['porcentaje_puntual']}%")

        # Actualizar tablas
        self._llenar_tree(self.tree_fac, [
            (f['facultad'], f"{f['puntualidad']}%", f['total'])
            for f in stats['facultades_puntuales'][:8]
        ])

        self._llenar_tree(self.tree_deben, [
            (d['docente'], d['pendientes'])
            for d in stats['docentes_deben'][:8]
        ])

        self._llenar_tree(self.tree_imp, [
            (d['docente'], TimeHelper.minutes_to_hhmm(d['promedio_retraso']))
            for d in stats['docentes_impuntuales'][:8]
        ])

    def _llenar_tree(self, tree: ttk.Treeview, rows):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert('', 'end', values=row)
