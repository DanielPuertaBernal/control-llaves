"""
Vista de Historial de Equipos
"""
from tkinter import ttk, messagebox

from controllers import PréstamoController, DevolucionController


class EquiposHistorialView:
    """Vista para historial de préstamos y devoluciones"""

    def __init__(self, parent_frame, prestamo_controller: PréstamoController, devolucion_controller: DevolucionController):
        self.prestamo_controller = prestamo_controller
        self.devolucion_controller = devolucion_controller

        self.frame = ttk.Frame(parent_frame, padding="15")
        self.frame.pack(fill='both', expand=True)

        self._crear_tab_historial()

    def _crear_tab_historial(self):
        """Crea la pestaña de historial"""
        self.notebook_historial = ttk.Notebook(self.frame)
        self.notebook_historial.pack(fill='both', expand=True)

        frame_activos = ttk.Frame(self.notebook_historial)
        self.notebook_historial.add(frame_activos, text="Préstamos Activos")

        frame_activos_content = ttk.Frame(frame_activos, padding="15")
        frame_activos_content.pack(fill='both', expand=True)

        frame_busq_act = ttk.Frame(frame_activos_content)
        frame_busq_act.pack(fill='x', pady=(0, 15))

        ttk.Label(frame_busq_act, text="Buscar:").pack(side='left', padx=(0, 10))
        self.entrada_busq_activos = ttk.Entry(frame_busq_act)
        self.entrada_busq_activos.pack(side='left', fill='x', expand=True)

        ttk.Button(frame_busq_act, text="🔄 Actualizar",
                   command=self.cargar_historial).pack(side='left', padx=(10, 0))

        self.tree_activos = ttk.Treeview(frame_activos_content, height=15, columns=(
            'docente', 'equipos', 'fecha'
        ), show='headings')

        self.tree_activos.heading('docente', text='Docente', anchor='center')
        self.tree_activos.heading('equipos', text='Equipos', anchor='center')
        self.tree_activos.heading('fecha', text='Fecha Préstamo', anchor='center')

        self.tree_activos.column('docente', width=120, anchor='center')
        self.tree_activos.column('equipos', width=250, anchor='center')
        self.tree_activos.column('fecha', width=100, anchor='center')

        scrollbar_act = ttk.Scrollbar(frame_activos_content, orient='vertical', command=self.tree_activos.yview)
        self.tree_activos.configure(yscrollcommand=scrollbar_act.set)

        self.tree_activos.pack(side='left', fill='both', expand=True)
        scrollbar_act.pack(side='right', fill='y')

        frame_devs = ttk.Frame(self.notebook_historial)
        self.notebook_historial.add(frame_devs, text="Devoluciones")

        frame_devs_content = ttk.Frame(frame_devs, padding="15")
        frame_devs_content.pack(fill='both', expand=True)

        frame_busq_dev = ttk.Frame(frame_devs_content)
        frame_busq_dev.pack(fill='x', pady=(0, 15))

        ttk.Label(frame_busq_dev, text="Buscar:").pack(side='left', padx=(0, 10))
        self.entrada_busq_devs = ttk.Entry(frame_busq_dev)
        self.entrada_busq_devs.pack(side='left', fill='x', expand=True)

        ttk.Button(frame_busq_dev, text="🔄 Actualizar",
                   command=self.cargar_historial).pack(side='left', padx=(10, 0))

        self.tree_devoluciones = ttk.Treeview(frame_devs_content, height=15, columns=(
            'docente', 'equipos', 'fecha', 'estados'
        ), show='headings')

        self.tree_devoluciones.heading('docente', text='Docente', anchor='center')
        self.tree_devoluciones.heading('equipos', text='Equipos', anchor='center')
        self.tree_devoluciones.heading('fecha', text='Fecha Devolución', anchor='center')
        self.tree_devoluciones.heading('estados', text='Estados', anchor='center')

        self.tree_devoluciones.column('docente', width=120, anchor='center')
        self.tree_devoluciones.column('equipos', width=250, anchor='center')
        self.tree_devoluciones.column('fecha', width=120, anchor='center')
        self.tree_devoluciones.column('estados', width=120, anchor='center')

        scrollbar_devs = ttk.Scrollbar(frame_devs_content, orient='vertical', command=self.tree_devoluciones.yview)
        self.tree_devoluciones.configure(yscrollcommand=scrollbar_devs.set)

        self.tree_devoluciones.pack(side='left', fill='both', expand=True)
        scrollbar_devs.pack(side='right', fill='y')

        self.prestamos_activos = []
        self.devoluciones = []

    def cargar_historial(self):
        """Carga historial de préstamos y devoluciones"""
        try:
            prestamos = self.prestamo_controller.obtener_activos()
            self.prestamos_activos = [
                p.to_dict() if hasattr(p, 'to_dict') else p for p in (prestamos or [])
            ]

            devoluciones = self.devolucion_controller.obtener_todas()
            self.devoluciones = [
                d.to_dict() if hasattr(d, 'to_dict') else d for d in (devoluciones or [])
            ]

            self._actualizar_tabla_activos()
            self._actualizar_tabla_devoluciones()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")

    def _actualizar_tabla_activos(self):
        """Actualiza tabla de préstamos activos"""
        for item in self.tree_activos.get_children():
            self.tree_activos.delete(item)

        for prestamo in self.prestamos_activos:
            docente = prestamo.get('docente_nombre', '')
            equipos = prestamo.get('equipos', [])
            equipos_str = ', '.join([f"{e.get('equipo_nombre') or e.get('nombre', '')} x{e.get('cantidad', 1)}" for e in equipos])
            if len(equipos_str) > 50:
                equipos_str = equipos_str[:47] + "..."

            fecha = prestamo.get('fecha_prestamo', '')

            self.tree_activos.insert('', 'end', values=(docente, equipos_str, fecha))

    def _actualizar_tabla_devoluciones(self):
        """Actualiza tabla de devoluciones"""
        for item in self.tree_devoluciones.get_children():
            self.tree_devoluciones.delete(item)

        for devolucion in self.devoluciones:
            docente = devolucion.get('docente_codigo_nfc', '')
            equipos = devolucion.get('equipos_devueltos', [])
            equipos_str = ', '.join([f"{e.get('equipo_nombre') or e.get('nombre', '')} x{e.get('cantidad_devuelta', 1)}" for e in equipos])
            if len(equipos_str) > 50:
                equipos_str = equipos_str[:47] + "..."

            estados = set([e.get('estado_equipo') or e.get('estado', 'bueno') for e in equipos])
            estados_str = ', '.join(sorted(estados))

            fecha = devolucion.get('fecha_devolucion', '')

            self.tree_devoluciones.insert('', 'end', values=(docente, equipos_str, fecha, estados_str))
