"""
Vista de Movimiento de Equipos (Préstamo/Devolución)
"""
from tkinter import ttk, messagebox

from controllers import DocenteController, EquipoController, PréstamoController, DevolucionController


class EquiposMovimientoView:
    """Vista para el movimiento de equipos"""

    def __init__(self, parent_frame, equipo_controller: EquipoController,
                 prestamo_controller: PréstamoController, devolucion_controller: DevolucionController,
                 docente_controller: DocenteController = None, on_actualizar_historial=None):
        self.equipo_controller = equipo_controller
        self.prestamo_controller = prestamo_controller
        self.devolucion_controller = devolucion_controller
        self.docente_controller = docente_controller
        self.on_actualizar_historial = on_actualizar_historial

        self.frame = ttk.Frame(parent_frame, padding="15")
        self.frame.pack(fill='both', expand=True)

        self._crear_tab_movimiento()

    def _crear_tab_movimiento(self):
        """Crea la pestaña unificada de movimiento (Préstamo/Devolución)"""
        frame_docente = ttk.LabelFrame(self.frame, text="👤 Escanea Docente", padding="15")
        frame_docente.pack(fill='x', pady=(0, 20))

        ttk.Label(frame_docente, text="Código NFC:").grid(row=0, column=0, sticky='w', pady=5)
        self.label_codigo_nfc_mov = ttk.Label(frame_docente, text="[Escanea tarjeta]",
                                              foreground='blue', font=('Segoe UI', 10, 'bold'))
        self.label_codigo_nfc_mov.grid(row=0, column=1, sticky='w', pady=5)

        ttk.Label(frame_docente, text="Nombre:").grid(row=1, column=0, sticky='w', pady=5)
        self.label_nombre_mov = ttk.Label(frame_docente, text="[Pendiente]")
        self.label_nombre_mov.grid(row=1, column=1, sticky='w', pady=5)

        ttk.Label(frame_docente, text="Estado:").grid(row=2, column=0, sticky='w', pady=5)
        self.label_estado_mov = ttk.Label(frame_docente, text="[Sin información]",
                                          foreground='gray', font=('Segoe UI', 9, 'italic'))
        self.label_estado_mov.grid(row=2, column=1, sticky='w', pady=5)

        ttk.Button(frame_docente, text="🔄 Limpiar",
                   command=self._limpiar_movimiento).grid(row=0, column=2, padx=(20, 0), rowspan=3)

        self.frame_contenido_mov = ttk.Frame(self.frame)
        self.frame_contenido_mov.pack(fill='both', expand=True)

        self.docente_nfc_mov = None
        self.docente_nombre_mov = None
        self.docente_tiene_prestado = False
        self.prestamo_actual = None

    def _limpiar_movimiento(self):
        """Limpia la sección de movimiento"""
        self.docente_nfc_mov = None
        self.docente_nombre_mov = None
        self.docente_tiene_prestado = False
        self.label_codigo_nfc_mov.config(text="[Escanea tarjeta]", foreground='blue')
        self.label_nombre_mov.config(text="[Pendiente]")
        self.label_estado_mov.config(text="[Sin información]", foreground='gray')

        for widget in self.frame_contenido_mov.winfo_children():
            widget.destroy()

    def detectar_nfc_automático(self, codigo_nfc):
        """Procesa lectura NFC y muestra formulario según estado del docente"""
        if not codigo_nfc:
            return

        self._limpiar_movimiento()
        self.docente_nfc_mov = codigo_nfc
        self.label_codigo_nfc_mov.config(text=codigo_nfc, foreground='green')

        nombre_docente = None
        if self.docente_controller:
            docente = self.docente_controller.buscar_docente_por_carnet(codigo_nfc)
            if docente:
                nombre_docente = docente.get('Nombre') or docente.get('nombre')

        if nombre_docente:
            self.docente_nombre_mov = nombre_docente
            self.label_nombre_mov.config(text=nombre_docente)

        self._detectar_estado_docente(codigo_nfc)

    def _detectar_estado_docente(self, codigo_nfc):
        """Detecta si el docente tiene equipos prestados"""
        try:
            prestamos = self.prestamo_controller.obtener_activos_docente(codigo_nfc)
            self.docente_tiene_prestado = bool(prestamos)

            if prestamos:
                prestamo = prestamos[0] if isinstance(prestamos, list) else prestamos
                self.prestamo_actual = prestamo.to_dict() if hasattr(prestamo, 'to_dict') else prestamo
                nombre_prestamo = self.prestamo_actual.get('docente_nombre') if isinstance(self.prestamo_actual, dict) else None
                if nombre_prestamo:
                    self.docente_nombre_mov = nombre_prestamo
                    self.label_nombre_mov.config(text=nombre_prestamo)
                self.label_estado_mov.config(text="✅ Tiene equipos en préstamo", foreground='green')
                self._mostrar_formulario_devolucion()
            else:
                self.prestamo_actual = None
                self.label_estado_mov.config(text="❌ Sin préstamos - Disponible para nuevos", foreground='orange')
                self._mostrar_formulario_prestamo()

            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al detectar estado: {str(e)}")
            return False

    def _mostrar_formulario_prestamo(self):
        """Muestra formulario con carrito de lectura de códigos de barras"""
        for widget in self.frame_contenido_mov.winfo_children():
            widget.destroy()

        frame = ttk.LabelFrame(self.frame_contenido_mov, text="📤 Nuevo Préstamo - Lectura de Códigos", padding="15")
        frame.pack(fill='both', expand=True)

        frame_entrada = ttk.LabelFrame(frame, text="📖 Escanea Equipos", padding="10")
        frame_entrada.pack(fill='x', pady=(0, 15))

        ttk.Label(frame_entrada, text="Código de Barras:").pack(side='left', padx=(0, 10))
        self.entrada_codigo_barras = ttk.Entry(frame_entrada, width=40)
        self.entrada_codigo_barras.pack(side='left', fill='x', expand=True)
        self.entrada_codigo_barras.focus()

        self.entrada_codigo_barras.bind('<Return>', lambda e: self._agregar_equipo_al_carrito())

        frame_carrito = ttk.LabelFrame(frame, text="🛒 Carrito de Préstamo", padding="10")
        frame_carrito.pack(fill='both', expand=True, pady=(0, 15))

        self.tree_carrito = ttk.Treeview(
            frame_carrito,
            height=10,
            columns=('codigo', 'nombre', 'consecutivo', 'codigo_barras', 'eliminar'),
            show='headings'
        )

        self.tree_carrito.heading('codigo', text='Código', anchor='center')
        self.tree_carrito.heading('nombre', text='Nombre', anchor='center')
        self.tree_carrito.heading('consecutivo', text='Consecutivo', anchor='center')
        self.tree_carrito.heading('codigo_barras', text='Código Barras', anchor='center')
        self.tree_carrito.heading('eliminar', text='Acción', anchor='center')

        self.tree_carrito.column('codigo', width=80, anchor='center')
        self.tree_carrito.column('nombre', width=120, anchor='center')
        self.tree_carrito.column('consecutivo', width=80, anchor='center')
        self.tree_carrito.column('codigo_barras', width=140, anchor='center')
        self.tree_carrito.column('eliminar', width=80, anchor='center')

        scrollbar_carrito = ttk.Scrollbar(frame_carrito, orient='vertical', command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar_carrito.set)

        self.tree_carrito.pack(side='left', fill='both', expand=True)
        scrollbar_carrito.pack(side='right', fill='y')

        self.tree_carrito.bind('<ButtonRelease-1>', self._on_click_eliminar_carrito)

        frame_botones = ttk.Frame(frame)
        frame_botones.pack(fill='x', pady=10)

        ttk.Button(frame_botones, text="✔️ Confirmar Préstamo",
                   command=self._confirmar_prestamo_carrito).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="🗑️ Limpiar Carrito",
                   command=self._limpiar_carrito).pack(side='left', padx=5)

        self.carrito_equipos = []

    def _mostrar_formulario_devolucion(self):
        """Muestra formulario para devolver un préstamo"""
        for widget in self.frame_contenido_mov.winfo_children():
            widget.destroy()

        if not self.prestamo_actual:
            return

        frame = ttk.LabelFrame(self.frame_contenido_mov, text="📥 Devolución de Préstamo", padding="15")
        frame.pack(fill='both', expand=True)

        frame_info = ttk.Frame(frame)
        frame_info.pack(fill='x', pady=5)
        ttk.Label(frame_info, text=f"Fecha de Préstamo: {self.prestamo_actual.get('fecha_prestamo', 'N/A')}").pack(side='left')

        frame_tabla = ttk.Frame(frame)
        frame_tabla.pack(fill='both', expand=True, pady=10)

        tree = ttk.Treeview(frame_tabla, height=8, columns=('codigo', 'nombre', 'consecutivo', 'accion'), show='headings')
        tree.heading('codigo', text='Código', anchor='center')
        tree.heading('nombre', text='Nombre', anchor='center')
        tree.heading('consecutivo', text='Consecutivo', anchor='center')
        tree.heading('accion', text='Acción', anchor='center')

        tree.column('codigo', width=80, anchor='center')
        tree.column('nombre', width=120, anchor='center')
        tree.column('consecutivo', width=140, anchor='center')
        tree.column('accion', width=100, anchor='center')

        equipos = self.prestamo_actual.get('equipos', [])
        for eq in equipos:
            equipo_id = eq.get('equipo_id')
            consecutivo = ''
            if equipo_id:
                equipo_obj = self.equipo_controller.obtener_equipo(equipo_id)
                if equipo_obj:
                    equipo_dict = equipo_obj.to_dict() if hasattr(equipo_obj, 'to_dict') else equipo_obj
                    consecutivo = equipo_dict.get('consecutivo', '')
            tree.insert('', 'end', values=(
                eq.get('equipo_codigo', ''),
                eq.get('equipo_nombre', ''),
                consecutivo,
                'Devolver'
            ))

        scrollbar = ttk.Scrollbar(frame_tabla, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        def on_click_devolver(event):
            region = tree.identify('region', event.x, event.y)
            if region != 'cell':
                return
            col = tree.identify_column(event.x)
            if col != '#4':
                return
            item_id = tree.identify_row(event.y)
            if not item_id:
                return
            self._registrar_devolucion_simple()

        tree.bind('<ButtonRelease-1>', on_click_devolver)

    def _registrar_devolucion_simple(self):
        """Registra la devolución completa"""
        try:
            if not self.prestamo_actual:
                messagebox.showerror("Error", "No hay préstamo activo")
                return

            self.devolucion_controller.crear_devolucion(
                self.prestamo_actual.get('_id'),
                self.docente_nfc_mov,
                self.docente_nombre_mov,
                self.prestamo_actual.get('equipos', [])
            )

            messagebox.showinfo("Éxito", "Devolución registrada correctamente")
            self._limpiar_movimiento()
            if self.on_actualizar_historial:
                self.on_actualizar_historial()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _agregar_equipo_al_carrito(self):
        """Agrega un equipo al carrito por código de barras"""
        codigo_barras = self.entrada_codigo_barras.get().strip()

        if not codigo_barras:
            messagebox.showwarning("Advertencia", "Ingresa un código de barras")
            self.entrada_codigo_barras.focus()
            return

        equipo = self.equipo_controller.obtener_por_codigo_barras(codigo_barras)

        if not equipo:
            messagebox.showerror("Error", f"Equipo no encontrado: {codigo_barras}")
            self.entrada_codigo_barras.delete(0, 'end')
            self.entrada_codigo_barras.focus()
            return

        equipo_dict = equipo.to_dict() if hasattr(equipo, 'to_dict') else equipo
        if equipo_dict.get('estado') != 'activo':
            messagebox.showerror("Error", f"Equipo no disponible: {equipo_dict.get('nombre')}")
            self.entrada_codigo_barras.delete(0, 'end')
            self.entrada_codigo_barras.focus()
            return

        equipo_id = str(equipo_dict.get('_id', ''))
        for eq_carrito in self.carrito_equipos:
            if str(eq_carrito.get('_id', '')) == equipo_id:
                messagebox.showwarning("Advertencia", "Este equipo ya está en el carrito")
                self.entrada_codigo_barras.delete(0, 'end')
                self.entrada_codigo_barras.focus()
                return

        self.carrito_equipos.append(equipo_dict)

        self.tree_carrito.insert('', 'end',
            values=(
                equipo_dict.get('codigo_inventario', ''),
                equipo_dict.get('nombre', ''),
                equipo_dict.get('consecutivo', ''),
                equipo_dict.get('codigo_barras', ''),
                'Eliminar'
            )
        )

        self.entrada_codigo_barras.delete(0, 'end')
        self.entrada_codigo_barras.focus()

    def _on_click_eliminar_carrito(self, event):
        """Elimina un equipo del carrito cuando se hace clic en 'Eliminar'"""
        region = self.tree_carrito.identify('region', event.x, event.y)
        if region != 'cell':
            return
        col = self.tree_carrito.identify_column(event.x)
        if col != '#5':
            return

        item_id = self.tree_carrito.identify_row(event.y)
        if not item_id:
            return

        items = self.tree_carrito.get_children()
        idx = list(items).index(item_id)

        self.carrito_equipos.pop(idx)
        self.tree_carrito.delete(item_id)

    def _limpiar_carrito(self):
        """Limpia todos los equipos del carrito"""
        self.carrito_equipos.clear()
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)

    def _confirmar_prestamo_carrito(self):
        """Confirma el préstamo con todos los equipos del carrito"""
        if not self.carrito_equipos:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return

        try:
            self.prestamo_controller.crear_prestamo(
                self.docente_nfc_mov,
                self.docente_nombre_mov,
                self.carrito_equipos
            )

            messagebox.showinfo(
                "Éxito",
                f"Préstamo creado para {self.docente_nombre_mov}\nEquipos prestados: {len(self.carrito_equipos)}"
            )

            self._limpiar_movimiento()
            if self.on_actualizar_historial:
                self.on_actualizar_historial()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear préstamo: {str(e)}")
