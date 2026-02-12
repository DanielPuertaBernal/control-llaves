"""
Vista de Movimiento de Equipos (Préstamo/Devolución)
"""
from tkinter import ttk, messagebox

from controllers import DocenteController, EquipoController, PréstamoController, DevolucionController
from application.auth.session_manager import SessionManager


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
        self.session_manager = SessionManager()

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
        """Procesa lectura NFC y muestra formulario según estado del docente o agrega equipo"""
        if not codigo_nfc:
            return

        # Detectar si es código de equipo (comienza con INV, DJ, PC, etc.)
        if self._es_codigo_equipo(codigo_nfc):
            print(f"[CARRITO] Código de equipo detectado: {codigo_nfc}")
            self._agregar_equipo_interno(codigo_nfc)
            return

        # Si no es equipo, procesar como carnet de docente
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
                self.label_estado_mov.config(text="✅ Tiene equipos en préstamo - Puede devolver o agregar más", foreground='green')
                self._mostrar_formulario_unificado()
            else:
                self.prestamo_actual = None
                self.label_estado_mov.config(text="❌ Sin préstamos - Disponible para nuevos", foreground='orange')
                self._mostrar_formulario_unificado()

            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al detectar estado: {str(e)}")
            return False

    def _mostrar_formulario_unificado(self):
        """Muestra formulario unificado con una sola tabla para equipos prestados y nuevos"""
        for widget in self.frame_contenido_mov.winfo_children():
            widget.destroy()

        frame = ttk.LabelFrame(self.frame_contenido_mov, text="🔄 Gestión de Equipos", padding="15")
        frame.pack(fill='both', expand=True)

        # Botones superiores
        frame_botones_top = ttk.Frame(frame)
        frame_botones_top.pack(fill='x', pady=(0, 15))

        if self.prestamo_actual:
            # Tiene préstamo activo - guardar cambios (agregar nuevos)
            ttk.Button(frame_botones_top, text="✔️ Guardar Cambios",
                       command=self._guardar_cambios_prestamo).pack(side='left', padx=5)
        else:
            # Sin préstamo - confirmar nuevo préstamo
            ttk.Button(frame_botones_top, text="✔️ Confirmar Préstamo",
                       command=self._confirmar_prestamo_carrito).pack(side='left', padx=5)

        ttk.Button(frame_botones_top, text="🗑️ Limpiar Nuevos",
                   command=self._limpiar_carrito).pack(side='left', padx=5)

        # Campo de escaneo
        frame_entrada = ttk.LabelFrame(frame, text="📖 Escanear Equipos", padding="10")
        frame_entrada.pack(fill='x', pady=(0, 15))

        ttk.Label(frame_entrada, text="Código de Barras:").pack(side='left', padx=(0, 10))
        self.entrada_codigo_barras = ttk.Entry(frame_entrada, width=40)
        self.entrada_codigo_barras.pack(side='left', fill='x', expand=True)
        self.entrada_codigo_barras.focus()

        # Timer para auto-submit
        self.auto_submit_timer = None
        
        # Bind eventos
        self.entrada_codigo_barras.bind('<Return>', lambda e: self._agregar_equipo_al_carrito())
        self.entrada_codigo_barras.bind('<KeyRelease>', self._on_codigo_barras_change)

        # Tabla unificada
        frame_carrito = ttk.LabelFrame(frame, text="📦 Equipos", padding="10")
        frame_carrito.pack(fill='both', expand=True)

        self.tree_carrito = ttk.Treeview(
            frame_carrito,
            height=12,
            columns=('tipo', 'codigo', 'nombre', 'consecutivo', 'accion'),
            show='headings'
        )

        self.tree_carrito.heading('tipo', text='Estado', anchor='center')
        self.tree_carrito.heading('codigo', text='Código', anchor='center')
        self.tree_carrito.heading('nombre', text='Nombre', anchor='center')
        self.tree_carrito.heading('consecutivo', text='Consecutivo', anchor='center')
        self.tree_carrito.heading('accion', text='Acción', anchor='center')

        self.tree_carrito.column('tipo', width=100, anchor='center')
        self.tree_carrito.column('codigo', width=80, anchor='center')
        self.tree_carrito.column('nombre', width=150, anchor='center')
        self.tree_carrito.column('consecutivo', width=80, anchor='center')
        self.tree_carrito.column('accion', width=80, anchor='center')

        scrollbar_carrito = ttk.Scrollbar(frame_carrito, orient='vertical', command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar_carrito.set)

        self.tree_carrito.pack(side='left', fill='both', expand=True)
        scrollbar_carrito.pack(side='right', fill='y')

        self.tree_carrito.bind('<ButtonRelease-1>', self._on_click_accion_equipo)

        # Inicializar listas
        self.carrito_equipos = []
        self.equipos_tabla_map = {}  # {item_id: {'tipo': 'prestado'/'nuevo', 'data': equipo_data}}

        # Cargar equipos prestados si existen
        if self.prestamo_actual:
            equipos_prestados = self.prestamo_actual.get('equipos', [])
            for eq in equipos_prestados:
                equipo_id = eq.get('equipo_id')
                consecutivo = ''
                if equipo_id:
                    equipo_obj = self.equipo_controller.obtener_equipo(equipo_id)
                    if equipo_obj:
                        equipo_dict = equipo_obj.to_dict() if hasattr(equipo_obj, 'to_dict') else equipo_obj
                        consecutivo = equipo_dict.get('consecutivo', '')
                
                item_id = self.tree_carrito.insert('', 'end', values=(
                    '🔵 Prestado',
                    eq.get('equipo_codigo', ''),
                    eq.get('equipo_nombre', ''),
                    consecutivo,
                    'Devolver'
                ), tags=('prestado',))
                
                self.equipos_tabla_map[item_id] = {'tipo': 'prestado', 'data': eq}
            
            # Aplicar color a equipos prestados
            self.tree_carrito.tag_configure('prestado', background='#e3f2fd')

    def _on_click_accion_equipo(self, event):
        """Maneja clic en acción: Devolver (prestados) o Eliminar (nuevos)"""
        region = self.tree_carrito.identify('region', event.x, event.y)
        if region != 'cell':
            return
        
        col = self.tree_carrito.identify_column(event.x)
        if col != '#5':  # Columna de acción
            return

        item_id = self.tree_carrito.identify_row(event.y)
        if not item_id or item_id not in self.equipos_tabla_map:
            return

        equipo_info = self.equipos_tabla_map[item_id]
        
        if equipo_info['tipo'] == 'prestado':
            # Devolver equipo prestado
            self._devolver_equipo_individual(item_id, equipo_info['data'])
        elif equipo_info['tipo'] == 'nuevo':
            # Eliminar del carrito
            self._eliminar_equipo_nuevo(item_id)

    def _devolver_equipo_individual(self, item_id, equipo_data):
        """Devuelve un equipo prestado individualmente"""
        if not self.prestamo_actual:
            messagebox.showerror("Error", "No hay préstamo activo")
            return

        try:
            # Obtener usuario actual
            usuario_actual = self.session_manager.obtener_usuario_actual()
            auxiliar_nombre = usuario_actual.nombre if usuario_actual else "Auxiliar"
            
            # Devolver solo este equipo
            self.devolucion_controller.crear_devolucion(
                self.prestamo_actual.get('_id'),
                self.docente_nfc_mov,
                self.docente_nombre_mov,
                [equipo_data],  # Solo este equipo
                auxiliar_que_recibio=auxiliar_nombre
            )

            # Eliminar de la tabla y del map
            self.tree_carrito.delete(item_id)
            del self.equipos_tabla_map[item_id]

            print(f"[DEVOLUCION] ✅ {equipo_data.get('equipo_nombre', 'Equipo')} devuelto")
            
            if self.on_actualizar_historial:
                self.on_actualizar_historial()
            
            # Verificar si quedan equipos prestados en la tabla
            equipos_prestados_restantes = [
                info for info in self.equipos_tabla_map.values() 
                if info['tipo'] == 'prestado'
            ]
            
            # Si no quedan equipos prestados, recargar estado (para mostrar sin préstamo)
            if not equipos_prestados_restantes:
                self._limpiar_movimiento()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar_equipo_nuevo(self, item_id):
        """Elimina un equipo nuevo del carrito"""
        # Encontrar índice en carrito_equipos
        items = self.tree_carrito.get_children()
        idx_visual = list(items).index(item_id)
        
        # Contar cuántos prestados hay antes de este ítem
        prestados_antes = 0
        for i, item in enumerate(items):
            if i >= idx_visual:
                break
            if item in self.equipos_tabla_map and self.equipos_tabla_map[item]['tipo'] == 'prestado':
                prestados_antes += 1
        
        # Índice real en carrito_equipos
        idx_real = idx_visual - prestados_antes
        
        if 0 <= idx_real < len(self.carrito_equipos):
            self.carrito_equipos.pop(idx_real)
        
        self.tree_carrito.delete(item_id)
        del self.equipos_tabla_map[item_id]

    def _guardar_cambios_prestamo(self):
        """Guarda cambios: agrega equipos nuevos al préstamo existente"""
        if not self.carrito_equipos:
            messagebox.showinfo("Info", "No hay equipos nuevos para agregar")
            return

        if not self.prestamo_actual:
            messagebox.showerror("Error", "No hay préstamo activo")
            return

        try:
            prestamo_id = self.prestamo_actual.get('_id')
            
            # Agregar cada equipo del carrito al préstamo
            for equipo in self.carrito_equipos:
                equipo_id = equipo.get('_id')
                self.prestamo_controller.agregar_equipo(prestamo_id, equipo_id, 1)

            messagebox.showinfo(
                "Éxito",
                f"✅ {len(self.carrito_equipos)} equipo(s) agregado(s) al préstamo"
            )

            self._limpiar_movimiento()
            if self.on_actualizar_historial:
                self.on_actualizar_historial()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_codigo_barras_change(self, event=None):
        """Maneja cambios en el campo de código de barras: normaliza y auto-submit"""
        # Cancelar timer anterior si existe
        if self.auto_submit_timer:
            self.entrada_codigo_barras.after_cancel(self.auto_submit_timer)
        
        # Obtener y normalizar el texto actual
        codigo_actual = self.entrada_codigo_barras.get()
        if codigo_actual:
            # Normalizar: reemplazar comillas simples por guiones y convertir a mayúsculas
            codigo_normalizado = codigo_actual.replace("'", "-").upper()
            if codigo_normalizado != codigo_actual:
                self.entrada_codigo_barras.delete(0, 'end')
                self.entrada_codigo_barras.insert(0, codigo_normalizado)
                print(f"[CARRITO] Código normalizado: {codigo_actual} → {codigo_normalizado}")
        
        # Si hay contenido, programar auto-submit después de 200ms (cuando el lector termina)
        if self.entrada_codigo_barras.get().strip():
            self.auto_submit_timer = self.entrada_codigo_barras.after(200, self._auto_submit_codigo)
    
    def _auto_submit_codigo(self):
        """Auto-ejecuta el agregado al carrito después de que el lector termina"""
        codigo = self.entrada_codigo_barras.get().strip()
        if codigo:
            print(f"[CARRITO] Auto-submit: {codigo}")
            self._agregar_equipo_al_carrito()

    def _es_codigo_equipo(self, codigo):
        """Detecta si el código es de un equipo (INV, DJ, PC, etc.) o de docente"""
        if not codigo:
            return False
        # Códigos de equipos típicamente empiezan con prefijo de inventario
        prefijos_equipo = ['INV', 'DJ', 'PC', 'MON', 'TEC', 'DICT']
        return any(codigo.upper().startswith(prefijo) for prefijo in prefijos_equipo)

    def _agregar_equipo_al_carrito(self):

        """Agrega un equipo al carrito por código de barras"""
        codigo_barras = self.entrada_codigo_barras.get().strip()

        if not codigo_barras:
            messagebox.showwarning("Advertencia", "Ingresa un código de barras")
            self.entrada_codigo_barras.focus()
            return

        self._agregar_equipo_interno(codigo_barras)

    def _agregar_equipo_interno(self, codigo_barras):
        """Lógica interna para agregar equipo o devolverlo si está prestado"""
        equipo = self.equipo_controller.obtener_por_codigo_barras(codigo_barras)

        if not equipo:
            messagebox.showerror("Error", f"Equipo no encontrado: {codigo_barras}")
            if hasattr(self, 'entrada_codigo_barras'):
                self.entrada_codigo_barras.delete(0, 'end')
                self.entrada_codigo_barras.focus()
            return

        equipo_dict = equipo.to_dict() if hasattr(equipo, 'to_dict') else equipo
        equipo_id = str(equipo_dict.get('_id', ''))
        
        # Verificar si este equipo está en la lista de prestados actual
        if hasattr(self, 'equipos_tabla_map') and self.prestamo_actual:
            for item_id, info in self.equipos_tabla_map.items():
                if info['tipo'] == 'prestado':
                    equipo_prestado_id = str(info['data'].get('equipo_id', ''))
                    if equipo_prestado_id == equipo_id:
                        # Equipo encontrado en prestados - devolverlo
                        print(f"[DEVOLUCION] Equipo escaneado está prestado, devolviendo: {codigo_barras}")
                        
                        # Limpiar entrada ANTES de devolver (para evitar problemas si se destruye la vista)
                        if hasattr(self, 'entrada_codigo_barras'):
                            try:
                                self.entrada_codigo_barras.delete(0, 'end')
                            except:
                                pass  # Widget ya destruido
                        
                        self._devolver_equipo_individual(item_id, info['data'])
                        
                        # Re-enfocar si el widget aún existe
                        if hasattr(self, 'entrada_codigo_barras'):
                            try:
                                self.entrada_codigo_barras.focus()
                            except:
                                pass  # Widget ya destruido
                        return
        
        # No está en prestados, intentar agregar como nuevo
        if equipo_dict.get('estado') != 'activo':
            messagebox.showerror("Error", f"Equipo no disponible: {equipo_dict.get('nombre')}")
            if hasattr(self, 'entrada_codigo_barras'):
                self.entrada_codigo_barras.delete(0, 'end')
                self.entrada_codigo_barras.focus()
            return

        # Validar si el equipo ya está en préstamo activo de otro docente
        prestamo_info = self.prestamo_controller.verificar_equipo_prestado(equipo_dict.get('_id'))
        if prestamo_info:
            esta_prestado, docente_nombre = prestamo_info
            messagebox.showerror(
                "Equipo en Préstamo", 
                f"⚠️ {equipo_dict.get('nombre')} ya está prestado a:\n\n👤 {docente_nombre}\n\nNo se puede prestar hasta que sea devuelto."
            )
            if hasattr(self, 'entrada_codigo_barras'):
                self.entrada_codigo_barras.delete(0, 'end')
                self.entrada_codigo_barras.focus()
            return

        # Verificar si ya está en el carrito de nuevos
        for eq_carrito in self.carrito_equipos:
            if str(eq_carrito.get('_id', '')) == equipo_id:
                messagebox.showwarning("Advertencia", "Este equipo ya está en el carrito")
                if hasattr(self, 'entrada_codigo_barras'):
                    self.entrada_codigo_barras.delete(0, 'end')
                    self.entrada_codigo_barras.focus()
                return

        self.carrito_equipos.append(equipo_dict)
        print(f"[CARRITO] Equipo agregado: {equipo_dict.get('codigo_inventario')}")

        # Si el árbol de carrito existe (formulario ya mostrado), actualizar UI
        if hasattr(self, 'tree_carrito') and hasattr(self, 'equipos_tabla_map'):
            item_id = self.tree_carrito.insert('', 'end',
                values=(
                    '🟢 Nuevo',
                    equipo_dict.get('codigo_inventario', ''),
                    equipo_dict.get('nombre', ''),
                    equipo_dict.get('consecutivo', ''),
                    'Eliminar'
                ), tags=('nuevo',))
            
            self.equipos_tabla_map[item_id] = {'tipo': 'nuevo', 'data': equipo_dict}
            self.tree_carrito.tag_configure('nuevo', background='#e8f5e9')

        if hasattr(self, 'entrada_codigo_barras'):
            self.entrada_codigo_barras.delete(0, 'end')
            self.entrada_codigo_barras.focus()
        
        # Mostrar confirmación sin messagebox cuando se agrega desde NFC para evitar bloqueos
        # (El usuario verá el equipo en el carrito inmediatamente)
        print(f"[CARRITO] ✅ {equipo_dict.get('nombre')} agregado al carrito")

    def _limpiar_carrito(self):
        """Limpia solo los equipos nuevos del carrito (mantiene prestados)"""
        if not hasattr(self, 'equipos_tabla_map'):
            return
        
        # Eliminar solo items nuevos
        items_a_eliminar = []
        for item_id, info in self.equipos_tabla_map.items():
            if info['tipo'] == 'nuevo':
                items_a_eliminar.append(item_id)
        
        for item_id in items_a_eliminar:
            self.tree_carrito.delete(item_id)
            del self.equipos_tabla_map[item_id]
        
        self.carrito_equipos.clear()

    def _confirmar_prestamo_carrito(self):
        """Confirma el préstamo con todos los equipos del carrito"""
        if not self.carrito_equipos:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return

        try:
            # Obtener usuario actual
            usuario_actual = self.session_manager.obtener_usuario_actual()
            auxiliar_nombre = usuario_actual.nombre if usuario_actual else "Auxiliar"
            
            self.prestamo_controller.crear_prestamo(
                self.docente_nfc_mov,
                self.docente_nombre_mov,
                self.carrito_equipos,
                auxiliar_prestamista=auxiliar_nombre
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
