"""
Vista de Informe de Llaves para Administrador
Interfaz simplificada: filtros rápidos, tabla de datos y exportación
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
import pandas as pd

from application.helpers import DateHelper
from presentation.components.date_widget_factory import DateWidgetFactory
from presentation.helpers import ViewHelper
from presentation.assets.estiloTkinter import COLORS_LLAVES


class InformesLlavesAdminView:
    """Informe de llaves con filtros rápidos y visualización clara"""

    def __init__(self, parent_frame, historial_controller):
        self.historial_controller = historial_controller
        self.df_base = None
        self.df_filtrada = None

        self.frame = ttk.Frame(parent_frame, padding="15")
        self.frame.pack(fill='both', expand=True)

        self._crear_interfaz()
        self._cargar_datos()

    def _crear_interfaz(self):
        """Interfaz con dos secciones: filtros y datos"""
        # SECCIÓN 1: Filtros (horizontal, compactos)
        self._crear_seccion_filtros()
        
        # SECCIÓN 2: Tabla de datos
        self._crear_seccion_tabla()

    def _crear_seccion_filtros(self):
        """Filtros rápidos en una sola fila"""
        filtros_frame = ttk.LabelFrame(self.frame, text="🔍 Filtros Rápidos", padding="12")
        filtros_frame.pack(fill='x', pady=(0, 15))

        # Fila 1: Rango de fechas
        ttk.Label(filtros_frame, text="Del:", font=('Segoe UI', 9)).pack(side='left', padx=(0, 5))
        self.fecha_inicio = DateWidgetFactory.crear_selector_fecha(filtros_frame)
        self.fecha_inicio.pack(side='left', padx=(0, 15))

        ttk.Label(filtros_frame, text="Al:", font=('Segoe UI', 9)).pack(side='left', padx=(0, 5))
        self.fecha_fin = DateWidgetFactory.crear_selector_fecha(filtros_frame)
        self.fecha_fin.pack(side='left', padx=(0, 15))

        # Facultad
        ttk.Label(filtros_frame, text="Facultad:", font=('Segoe UI', 9)).pack(side='left', padx=(0, 5))
        self.facultad_var = tk.StringVar(value="Todas")
        self.facultad_combo = ttk.Combobox(
            filtros_frame, 
            textvariable=self.facultad_var, 
            width=20, 
            state="readonly"
        )
        self.facultad_combo.pack(side='left', padx=(0, 15))

        # Botones de control
        btn_aplicar = ttk.Button(filtros_frame, text="Aplicar", command=self._aplicar_filtros)
        btn_aplicar.pack(side='left', padx=3)

        btn_limpiar = ttk.Button(filtros_frame, text="Limpiar", command=self._limpiar_filtros)
        btn_limpiar.pack(side='left', padx=3)

        btn_refrescar = ttk.Button(filtros_frame, text="Actualizar", command=self._cargar_datos)
        btn_refrescar.pack(side='left', padx=3)

    def _crear_seccion_tabla(self):
        """Tabla con información clara y resumen"""
        tabla_frame = ttk.LabelFrame(self.frame, text="📊 Registros de Llaves", padding="12")
        tabla_frame.pack(fill='both', expand=True)

        # Barra superior: información y exportar
        top_bar = ttk.Frame(tabla_frame)
        top_bar.pack(fill='x', pady=(0, 10))

        self.lbl_info = ttk.Label(
            top_bar, 
            text="0 registros", 
            font=('Segoe UI', 10, 'bold')
        )
        self.lbl_info.pack(side='left')

        ttk.Separator(top_bar, orient='vertical').pack(side='left', fill='y', padx=15)

        self.lbl_stats = ttk.Label(
            top_bar,
            text="Devueltas: 0 | En Préstamo: 0 | Retraso: 0",
            font=('Segoe UI', 9)
        )
        self.lbl_stats.pack(side='left')

        btn_exportar = ttk.Button(
            top_bar,
            text="📥 Exportar a Excel",
            command=self._exportar_datos
        )
        btn_exportar.pack(side='right')

        # Tabla con scroll
        tree_frame = ttk.Frame(tabla_frame)
        tree_frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                'Docente', 'Aula', 'Materia', 
                'Fecha Entrega', 'Hora Entrega', 'Hora Devolución',
                'Duración', 'Estado'
            ),
            show='headings',
            height=20
        )

        # Configurar columnas
        col_config = {
            'Docente': 150,
            'Aula': 80,
            'Materia': 150,
            'Fecha Entrega': 110,
            'Hora Entrega': 95,
            'Hora Devolución': 95,
            'Duración': 90,
            'Estado': 130
        }

        for col, ancho in col_config.items():
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=ancho, anchor='center')

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Configurar colores de estado
        self.tree.tag_configure('devuelta', background=COLORS_LLAVES['devuelta'])
        self.tree.tag_configure('en_prestamo', background=COLORS_LLAVES['en_prestamo'])
        self.tree.tag_configure('retraso', background=COLORS_LLAVES['retraso'])

    def _cargar_datos(self):
        """Carga datos del historial completo"""
        try:
            self.df_base = self.historial_controller.obtener_historial_completo()
            self._actualizar_filtros()
            self._aplicar_filtros()
        except Exception as e:
            ViewHelper.mostrar_error("Error", f"Error al cargar datos:\n{str(e)}")

    def _actualizar_filtros(self):
        """Actualiza opciones de facultad"""
        if self.df_base is None or self.df_base.empty:
            self.facultad_combo['values'] = ["Todas"]
            return

        facultades = self.historial_controller.obtener_facultades(self.df_base)
        opciones = ["Todas"] + facultades
        self.facultad_combo['values'] = opciones

    def _aplicar_filtros(self):
        """Aplica filtros seleccionados"""
        fecha_inicio = DateWidgetFactory.obtener_fecha(self.fecha_inicio)
        fecha_fin = DateWidgetFactory.obtener_fecha(self.fecha_fin)
        facultad = self.facultad_var.get()

        self.df_filtrada = self.historial_controller.filtrar_historial(
            fecha_inicio or None,
            fecha_fin or None,
            facultad,
            None,
            self.df_base
        )

        self._actualizar_tabla()

    def _limpiar_filtros(self):
        """Limpia todos los filtros"""
        hoy = datetime.now()
        DateWidgetFactory.establecer_fecha(self.fecha_inicio, hoy)
        DateWidgetFactory.establecer_fecha(self.fecha_fin, hoy)
        self.facultad_var.set("Todas")
        self._aplicar_filtros()

    def _actualizar_tabla(self):
        """Actualiza tabla con datos filtrados"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.df_filtrada is None or self.df_filtrada.empty:
            self.lbl_info.config(text="0 registros")
            self.lbl_stats.config(text="Sin datos")
            return

        # Contar estados
        stats = self._calcular_estadisticas()
        
        # Insertar datos
        for _, row in self.df_filtrada.iterrows():
            estado = row.get('Estado', '')
            tag = self._obtener_tag_estado(estado)

            valores = (
                str(row.get('Docente', '')),
                str(row.get('Aula', '')),
                str(row.get('Materia de la Clase', '')),
                str(row.get('Fecha de entrega', '')),
                str(row.get('Hora de entrega', '')),
                str(row.get('Hora de devolución', '') or ''),
                str(row.get('Duración clase (entrega→devolución)', '') or ''),
                estado
            )

            self.tree.insert('', 'end', values=valores, tags=(tag,))

        # Actualizar labels
        total = len(self.df_filtrada)
        self.lbl_info.config(text=f"{total} registros")
        self.lbl_stats.config(
            text=f"✓ Devueltas: {stats['devueltas']} | ⏳ En Préstamo: {stats['prestamo']} | ⚠ Retraso: {stats['retraso']}"
        )

    def _calcular_estadisticas(self) -> dict:
        """Calcula estadísticas de estado"""
        stats = {'devueltas': 0, 'prestamo': 0, 'retraso': 0}
        
        if self.df_filtrada is None or self.df_filtrada.empty:
            return stats

        for _, row in self.df_filtrada.iterrows():
            estado = row.get('Estado', '')
            
            if estado == 'Devuelta':
                stats['devueltas'] += 1
            elif estado == 'En Préstamo':
                # Verificar retraso (campos presentes en el registro)
                tiempo_retraso = row.get('Tiempo retraso devolución', '')
                if tiempo_retraso and tiempo_retraso.strip() and tiempo_retraso.lower() != 'n/a':
                    stats['retraso'] += 1
                else:
                    stats['prestamo'] += 1

        return stats

    def _obtener_tag_estado(self, estado: str) -> str:
        """Retorna el tag de color según estado"""
        if estado == 'Devuelta':
            return 'devuelta'
        elif estado == 'En Préstamo':
            return 'en_prestamo'
        return ''

    def _exportar_datos(self):
        """Exporta datos filtrados a Excel"""
        if self.df_filtrada is None or self.df_filtrada.empty:
            ViewHelper.mostrar_advertencia("Sin datos", "No hay registros para exportar")
            return

        try:
            fecha_hoy = date.today().strftime('%Y-%m-%d')
            nombre_archivo = f"Informe_Llaves_{fecha_hoy}.xlsx"

            ViewHelper.exportar_excel_simple(
                self.df_filtrada,
                nombre_archivo,
                "Guardar informe de llaves"
            )
        except Exception as e:
            ViewHelper.mostrar_error("Error", f"Error al exportar:\n{str(e)}")
