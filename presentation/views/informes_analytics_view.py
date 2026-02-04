"""
Vista de Informes para Administrador
Filtros avanzados + exportación a Excel
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd

try:
    from tkcalendar import DateEntry
    CALENDARIO_DISPONIBLE = True
except ImportError:
    CALENDARIO_DISPONIBLE = False


class InformesAnalyticsView:
    """Vista de informes y exportación para administradores"""

    def __init__(self, parent_frame, historial_controller):
        self.historial_controller = historial_controller

        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)

        self.df_base = None
        self.df_filtrada = None

        self._crear_interfaz()
        self._cargar_datos_base()

    def _crear_interfaz(self):
        # Filtros
        filtros = ttk.LabelFrame(self.frame, text="Filtros de Exportación", padding="20")
        filtros.pack(fill='x', pady=(0, 20))

        # Fila 1: Fechas
        ttk.Label(filtros, text="Fecha inicio:").grid(row=0, column=0, sticky='w', padx=(0, 8), pady=8)
        
        if CALENDARIO_DISPONIBLE:
            self.fecha_inicio = DateEntry(filtros, width=18, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        else:
            self.fecha_inicio = ttk.Entry(filtros, width=20)
        self.fecha_inicio.grid(row=0, column=1, padx=(0, 20), pady=8)

        ttk.Label(filtros, text="Fecha fin:").grid(row=0, column=2, sticky='w', padx=(0, 8), pady=8)
        
        if CALENDARIO_DISPONIBLE:
            self.fecha_fin = DateEntry(filtros, width=18, background='darkblue',
                                      foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        else:
            self.fecha_fin = ttk.Entry(filtros, width=20)
        self.fecha_fin.grid(row=0, column=3, padx=(0, 20), pady=8)

        # Fila 2: Facultad y Docente
        ttk.Label(filtros, text="Facultad:").grid(row=1, column=0, sticky='w', padx=(0, 8), pady=8)
        self.facultad_var = tk.StringVar(value="Todas")
        self.facultad_combo = ttk.Combobox(filtros, textvariable=self.facultad_var, width=28, state="readonly")
        self.facultad_combo.grid(row=1, column=1, padx=(0, 20), pady=8)

        ttk.Label(filtros, text="Docente:").grid(row=1, column=2, sticky='w', padx=(0, 8), pady=8)
        self.docente_entry = ttk.Entry(filtros, width=30)
        self.docente_entry.grid(row=1, column=3, padx=(0, 20), pady=8)

        # Fila 3: Botones
        btn_frame = ttk.Frame(filtros)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(12, 0))

        btn_aplicar = ttk.Button(btn_frame, text="Aplicar filtros", command=self._aplicar_filtros)
        btn_aplicar.pack(side='left', padx=4)

        btn_limpiar = ttk.Button(btn_frame, text="Limpiar", command=self._limpiar_filtros)
        btn_limpiar.pack(side='left', padx=4)

        btn_refrescar = ttk.Button(btn_frame, text="Actualizar datos", command=self._cargar_datos_base)
        btn_refrescar.pack(side='left', padx=4)

        # Panel de exportación (más prominente)
        export_frame = ttk.LabelFrame(self.frame, text="Exportación", padding="20")
        export_frame.pack(fill='both', expand=True)

        # Info y opciones
        info_frame = ttk.Frame(export_frame)
        info_frame.pack(fill='x', pady=(0, 12))

        self.lbl_info = ttk.Label(info_frame, text="0 registros seleccionados", font=('Segoe UI', 10, 'bold'))
        self.lbl_info.pack(anchor='w', pady=(0, 8))

        self.exportar_todo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(export_frame, text="Exportar todo el historial (ignorar filtros)", 
                       variable=self.exportar_todo_var, command=self._actualizar_info_exportacion).pack(anchor='w', pady=4)

        ttk.Label(export_frame, text="Se exportarán los registros según los filtros aplicados.\n"
                                     "Marque la opción anterior para exportar todos los datos.",
                 font=('Segoe UI', 9), foreground='gray').pack(anchor='w', pady=(4, 16))

        btn_exportar = ttk.Button(export_frame, text="📥 Exportar a Excel", command=self._exportar_excel)
        btn_exportar.pack(anchor='w')

    def _cargar_datos_base(self):
        self.df_base = self.historial_controller.obtener_historial_completo()
        self._actualizar_filtros()
        self._aplicar_filtros()

    def _actualizar_filtros(self):
        if self.df_base is None or self.df_base.empty:
            return
        facultades = self.historial_controller.obtener_facultades(self.df_base)
        opciones = ["Todas"] + facultades
        self.facultad_combo['values'] = opciones
        if self.facultad_var.get() not in opciones:
            self.facultad_var.set("Todas")

    def _validar_fecha(self, valor: str) -> bool:
        if not valor:
            return True
        try:
            datetime.strptime(valor, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _aplicar_filtros(self):
        if CALENDARIO_DISPONIBLE:
            fecha_inicio = self.fecha_inicio.get_date().strftime('%Y-%m-%d') if hasattr(self.fecha_inicio.get_date(), 'strftime') else str(self.fecha_inicio.get())
            fecha_fin = self.fecha_fin.get_date().strftime('%Y-%m-%d') if hasattr(self.fecha_fin.get_date(), 'strftime') else str(self.fecha_fin.get())
        else:
            fecha_inicio = self.fecha_inicio.get().strip()
            fecha_fin = self.fecha_fin.get().strip()

        if not CALENDARIO_DISPONIBLE and (not self._validar_fecha(fecha_inicio) or not self._validar_fecha(fecha_fin)):
            messagebox.showwarning("Formato inválido", "Use formato de fecha YYYY-MM-DD")
            return

        facultad = self.facultad_var.get()
        docente = self.docente_entry.get().strip()

        self.df_filtrada = self.historial_controller.filtrar_historial(
            fecha_inicio or None,
            fecha_fin or None,
            facultad,
            docente,
            self.df_base
        )

        self._actualizar_info_exportacion()

    def _limpiar_filtros(self):
        if CALENDARIO_DISPONIBLE:
            self.fecha_inicio.set_date(datetime.now())
            self.fecha_fin.set_date(datetime.now())
        else:
            self.fecha_inicio.delete(0, 'end')
            self.fecha_fin.delete(0, 'end')
        self.facultad_var.set("Todas")
        self.docente_entry.delete(0, 'end')
        self._aplicar_filtros()

    def _actualizar_info_exportacion(self):
        if self.exportar_todo_var.get():
            total = 0 if self.df_base is None else len(self.df_base)
            self.lbl_info.config(text=f"📄 {total} registros (TODO EL HISTORIAL)")
        else:
            total = 0 if self.df_filtrada is None else len(self.df_filtrada)
            self.lbl_info.config(text=f"📄 {total} registros (con filtros aplicados)")

    def _exportar_excel(self):
        if self.df_base is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar")
            return

        df_exportar = self.df_base if self.exportar_todo_var.get() else self.df_filtrada
        if df_exportar is None or df_exportar.empty:
            messagebox.showwarning("Sin datos", "No hay registros para exportar")
            return

        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        nombre_archivo = f"Informes_Llaves_{fecha_hoy}.xlsx"

        ruta = filedialog.asksaveasfilename(
            title="Guardar informe",
            defaultextension=".xlsx",
            filetypes=[("Archivo Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            initialfile=nombre_archivo
        )

        if not ruta:
            return

        try:
            self.historial_controller.exportar_excel(df_exportar, ruta)
            messagebox.showinfo("Éxito", f"Informe exportado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")
