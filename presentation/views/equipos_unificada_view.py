"""
Vista Unificada de Sistema de Equipos
Incluye gestión, préstamos, devoluciones e historial en pestañas
"""
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from controllers import DocenteController, EquipoController, PréstamoController, DevolucionController
from presentation.nfc_presenter import NFCPresenter


class EquiposUnificadaView:
    """Vista unificada para todo el sistema de equipos"""
    
    def __init__(self, parent_frame, equipo_controller: EquipoController,
                 prestamo_controller: PréstamoController, devolucion_controller: DevolucionController,
                 nfc_presenter: NFCPresenter = None, docente_controller: DocenteController = None):
        self.equipo_controller = equipo_controller
        self.prestamo_controller = prestamo_controller
        self.devolucion_controller = devolucion_controller
        self.nfc_presenter = nfc_presenter
        self.docente_controller = docente_controller
        
        # Frame principal
        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)
        
        # Crear interfaz con pestañas
        self._crear_interfaz()
        
        # Cargar datos iniciales
        self.cargar_inventario()
        self.cargar_historial()

    def _crear_interfaz(self):
        """Crea la interfaz con pestañas"""
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True)

        # Pestañas
        self.tab_inventario = ttk.Frame(self.notebook)
        self.tab_movimiento = ttk.Frame(self.notebook)
        self.tab_historial = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_inventario, text="📦 Inventario")
        self.notebook.add(self.tab_movimiento, text="↔️ Movimiento de Equipos")
        self.notebook.add(self.tab_historial, text="📜 Historial")

        self._crear_tab_inventario()
        self._crear_tab_movimiento()
        self._crear_tab_historial()

    # ==================== TAB 1: INVENTARIO ====================
    def _crear_tab_inventario(self):
        """Crea la pestaña de inventario"""
        frame = ttk.Frame(self.tab_inventario, padding="15")
        frame.pack(fill='both', expand=True)

        frame_top = ttk.Frame(frame)
        frame_top.pack(fill='x', pady=(0, 10))

        ttk.Label(frame_top, text="Buscar:").pack(side='left')
        self.entrada_busqueda_inv = ttk.Entry(frame_top)
        self.entrada_busqueda_inv.pack(side='left', fill='x', expand=True, padx=(10, 10))
        self.entrada_busqueda_inv.bind('<KeyRelease>', lambda e: self._filtrar_inventario())

        ttk.Button(frame_top, text="➕ Nuevo Equipo", command=self._abrir_formulario_nuevo_equipo).pack(side='right')

        frame_tabla = ttk.Frame(frame)
        frame_tabla.pack(fill='both', expand=True)

        self.tree_inventario = ttk.Treeview(
            frame_tabla,
            height=18,
            columns=('codigo', 'nombre', 'marca', 'serie', 'responsable'),
            show='headings'
        )

        self.tree_inventario.heading('codigo', text='Código', anchor='center')
        self.tree_inventario.heading('nombre', text='Nombre', anchor='center')
        self.tree_inventario.heading('marca', text='Marca', anchor='center')
        self.tree_inventario.heading('serie', text='Nº Serie', anchor='center')
        self.tree_inventario.heading('responsable', text='Responsable', anchor='center')

        self.tree_inventario.column('codigo', width=100, anchor='center')
        self.tree_inventario.column('nombre', width=160, anchor='center')
        self.tree_inventario.column('marca', width=140, anchor='center')
        self.tree_inventario.column('serie', width=140, anchor='center')
        self.tree_inventario.column('responsable', width=140, anchor='center')

        scrollbar_inv = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_inventario.yview)
        self.tree_inventario.configure(yscrollcommand=scrollbar_inv.set)

        self.tree_inventario.pack(side='left', fill='both', expand=True)
        scrollbar_inv.pack(side='right', fill='y')

        self.tree_inventario.bind('<Double-1>', self._editar_equipo)
        self.tree_inventario.bind('<Button-3>', self._mostrar_menu_contextual_equipo)
    
    # ==================== TAB 2: MOVIMIENTO INTELIGENTE ====================
    def _crear_tab_movimiento(self):
        """Crea la pestaña unificada de movimiento (Préstamo/Devolución)"""
        frame = ttk.Frame(self.tab_movimiento, padding="15")
        frame.pack(fill='both', expand=True)
        
        # Sección docente con NFC
        frame_docente = ttk.LabelFrame(frame, text="👤 Escanea Docente", padding="15")
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
        
        # Frame para contenido dinámico (será préstamo o devolución según estado)
        self.frame_contenido_mov = ttk.Frame(frame)
        self.frame_contenido_mov.pack(fill='both', expand=True)
        
        # Datos
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
        
        # Limpiar contenido
        for widget in self.frame_contenido_mov.winfo_children():
            widget.destroy()

    def detectar_nfc_automático(self, codigo_nfc):
        """Procesa lectura NFC y muestra formulario según estado del docente"""
        if not codigo_nfc:
            return

        # Enfocar pestaña de movimiento
        if hasattr(self, 'notebook') and hasattr(self, 'tab_movimiento'):
            self.notebook.select(self.tab_movimiento)

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
            # Obtener préstamos activos del docente
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
        """Muestra formulario para hacer un préstamo"""
        # Limpiar contenido anterior
        for widget in self.frame_contenido_mov.winfo_children():
            widget.destroy()
        
        frame = ttk.LabelFrame(self.frame_contenido_mov, text="📤 Nuevo Préstamo", padding="15")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Buscar Equipo:").grid(row=0, column=0, sticky='w', pady=5)
        entrada_busqueda = ttk.Entry(frame)
        entrada_busqueda.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Tabla de equipos disponibles
        frame_tabla = ttk.Frame(frame)
        frame_tabla.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=10)
        
        tree = ttk.Treeview(frame_tabla, height=8, columns=('codigo', 'nombre', 'serie', 'accion'), show='headings')
        tree.heading('codigo', text='Código', anchor='center')
        tree.heading('nombre', text='Nombre', anchor='center')
        tree.heading('serie', text='Nº Serie', anchor='center')
        tree.heading('accion', text='Acción', anchor='center')
        
        tree.column('codigo', width=80, anchor='center')
        tree.column('nombre', width=120, anchor='center')
        tree.column('serie', width=140, anchor='center')
        tree.column('accion', width=100, anchor='center')
        
        # Cargar equipos disponibles
        equipos_disp = self.equipo_controller.obtener_disponibles()

        prestamos_activos = self.prestamo_controller.obtener_activos() or []
        equipos_prestados = set()
        for prestamo in prestamos_activos:
            prestamo_dict = prestamo.to_dict() if hasattr(prestamo, 'to_dict') else prestamo
            for item in prestamo_dict.get('equipos', []):
                equipo_id = item.get('equipo_id')
                if equipo_id:
                    equipos_prestados.add(str(equipo_id))

        for eq in equipos_disp:
            eq_dict = eq.to_dict() if hasattr(eq, 'to_dict') else eq
            if str(eq_dict.get('_id')) in equipos_prestados:
                continue
            tree.insert('', 'end', values=(
                eq_dict.get('codigo_inventario', ''),
                eq_dict.get('nombre', ''),
                eq_dict.get('numero_serie', ''),
                'Prestar'
            ))
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        def on_click_prestar(event):
            region = tree.identify('region', event.x, event.y)
            if region != 'cell':
                return
            col = tree.identify_column(event.x)
            if col != '#4':
                return
            item_id = tree.identify_row(event.y)
            if not item_id:
                return
            self._crear_prestamo_simple(tree, item_id)

        tree.bind('<ButtonRelease-1>', on_click_prestar)
    
    def _mostrar_formulario_devolucion(self):
        """Muestra formulario para devolver un préstamo"""
        # Limpiar contenido anterior
        for widget in self.frame_contenido_mov.winfo_children():
            widget.destroy()
        
        if not self.prestamo_actual:
            return
        
        frame = ttk.LabelFrame(self.frame_contenido_mov, text="📥 Devolución de Préstamo", padding="15")
        frame.pack(fill='both', expand=True)
        
        # Información del préstamo
        frame_info = ttk.Frame(frame)
        frame_info.pack(fill='x', pady=5)
        ttk.Label(frame_info, text=f"Fecha de Préstamo: {self.prestamo_actual.get('fecha_prestamo', 'N/A')}").pack(side='left')
        
        # Tabla de equipos prestados
        frame_tabla = ttk.Frame(frame)
        frame_tabla.pack(fill='both', expand=True, pady=10)
        
        tree = ttk.Treeview(frame_tabla, height=8, columns=('codigo', 'nombre', 'serie', 'accion'), show='headings')
        tree.heading('codigo', text='Código', anchor='center')
        tree.heading('nombre', text='Nombre', anchor='center')
        tree.heading('serie', text='Nº Serie', anchor='center')
        tree.heading('accion', text='Acción', anchor='center')
        
        tree.column('codigo', width=80, anchor='center')
        tree.column('nombre', width=120, anchor='center')
        tree.column('serie', width=140, anchor='center')
        tree.column('accion', width=100, anchor='center')
        
        # Cargar equipos del préstamo
        equipos = self.prestamo_actual.get('equipos', [])
        for eq in equipos:
            equipo_id = eq.get('equipo_id')
            numero_serie = ''
            if equipo_id:
                equipo_obj = self.equipo_controller.obtener_equipo(equipo_id)
                if equipo_obj:
                    equipo_dict = equipo_obj.to_dict() if hasattr(equipo_obj, 'to_dict') else equipo_obj
                    numero_serie = equipo_dict.get('numero_serie', '')
            tree.insert('', 'end', values=(
                eq.get('equipo_codigo', ''),
                eq.get('equipo_nombre', ''),
                numero_serie,
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
    
    def _crear_prestamo_simple(self, tree, item_id=None):
        """Crea un préstamo simple con equipo seleccionado"""
        if not item_id and not tree.selection():
            messagebox.showwarning("Advertencia", "Selecciona un equipo")
            return
        
        item = item_id or tree.selection()[0]
        valores = tree.item(item, 'values')
        
        # Los valores son: (codigo, nombre, numero_serie, accion)
        numero_serie = valores[2]
        nombre_equipo = valores[1]
        
        try:
            # Buscar el equipo por número de serie
            equipo = self.equipo_controller.obtener_por_numero_serie(numero_serie)
            if not equipo:
                messagebox.showerror("Error", f"Equipo no encontrado: {numero_serie}")
                return
            
            # Crear el préstamo con este equipo
            prestamo = self.prestamo_controller.crear_prestamo_simple(
                self.docente_nfc_mov,
                self.docente_nombre_mov,
                [equipo.to_dict() if hasattr(equipo, 'to_dict') else equipo]
            )
            
            messagebox.showinfo("Éxito", f"Préstamo creado para {nombre_equipo}")
            self._limpiar_movimiento()
            self.cargar_historial()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _registrar_devolucion_simple(self):
        """Registra la devolución completa"""
        try:
            if not self.prestamo_actual:
                messagebox.showerror("Error", "No hay préstamo activo")
                return
            
            # Registrar devolución
            self.devolucion_controller.crear_devolucion(
                self.prestamo_actual.get('_id'),
                self.docente_nfc_mov,
                self.docente_nombre_mov,
                self.prestamo_actual.get('equipos', [])
            )
            
            messagebox.showinfo("Éxito", "Devolución registrada correctamente")
            self._limpiar_movimiento()
            self.cargar_historial()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # ==================== TAB 3: HISTORIAL ====================
    def _crear_tab_historial(self):
        """Crea la pestaña de historial"""
        frame = ttk.Frame(self.tab_historial, padding="15")
        frame.pack(fill='both', expand=True)
        
        # Sub-notebook para préstamos y devoluciones
        self.notebook_historial = ttk.Notebook(frame)
        self.notebook_historial.pack(fill='both', expand=True)
        
        # Sub-tab préstamos activos
        frame_activos = ttk.Frame(self.notebook_historial)
        self.notebook_historial.add(frame_activos, text="Préstamos Activos")
        
        frame_activos_content = ttk.Frame(frame_activos, padding="15")
        frame_activos_content.pack(fill='both', expand=True)
        
        # Búsqueda
        frame_busq_act = ttk.Frame(frame_activos_content)
        frame_busq_act.pack(fill='x', pady=(0, 15))
        
        ttk.Label(frame_busq_act, text="Buscar:").pack(side='left', padx=(0, 10))
        self.entrada_busq_activos = ttk.Entry(frame_busq_act)
        self.entrada_busq_activos.pack(side='left', fill='x', expand=True)
        
        ttk.Button(frame_busq_act, text="🔄 Actualizar", 
                   command=self.cargar_historial).pack(side='left', padx=(10, 0))
        
        # Tabla activos
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
        
        # Sub-tab devoluciones
        frame_devs = ttk.Frame(self.notebook_historial)
        self.notebook_historial.add(frame_devs, text="Devoluciones")
        
        frame_devs_content = ttk.Frame(frame_devs, padding="15")
        frame_devs_content.pack(fill='both', expand=True)
        
        # Búsqueda
        frame_busq_dev = ttk.Frame(frame_devs_content)
        frame_busq_dev.pack(fill='x', pady=(0, 15))
        
        ttk.Label(frame_busq_dev, text="Buscar:").pack(side='left', padx=(0, 10))
        self.entrada_busq_devs = ttk.Entry(frame_busq_dev)
        self.entrada_busq_devs.pack(side='left', fill='x', expand=True)
        
        ttk.Button(frame_busq_dev, text="🔄 Actualizar", 
                   command=self.cargar_historial).pack(side='left', padx=(10, 0))
        
        # Tabla devoluciones
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
        
        # Datos
        self.prestamos_activos = []
        self.devoluciones = []
    
    # ==================== MÉTODOS TAB INVENTARIO ====================
    def cargar_inventario(self):
        """Carga el inventario de equipos"""
        try:
            equipos = self.equipo_controller.obtener_inventario()
            prestamos_activos = self.prestamo_controller.obtener_activos() or []
            self.equipos_prestados_ids = set()
            self.equipo_docente_responsable = {}  # Mapeo equipo_id -> docente_nombre
            
            # Crear mapeo de equipo a docente responsable
            for prestamo in prestamos_activos:
                prestamo_dict = prestamo.to_dict() if hasattr(prestamo, 'to_dict') else prestamo
                docente_nombre = prestamo_dict.get('docente_nombre', '')
                for item in prestamo_dict.get('equipos', []):
                    equipo_id = item.get('equipo_id')
                    if equipo_id:
                        self.equipos_prestados_ids.add(str(equipo_id))
                        self.equipo_docente_responsable[str(equipo_id)] = docente_nombre
            
            self.equipos_dict = {}
            self.equipos_filtrados = []
            
            for equipo in (equipos or []):
                equipo_dict = equipo.to_dict() if hasattr(equipo, 'to_dict') else equipo
                equipo_id = str(equipo_dict.get('_id', ''))
                self.equipos_dict[equipo_id] = equipo_dict
                self.equipos_filtrados.append(equipo_dict)
            
            self._actualizar_tabla_inventario()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar inventario: {str(e)}")
    
    def _filtrar_inventario(self):
        """Filtra el inventario"""
        termino = self.entrada_busqueda_inv.get().lower()
        
        if not termino:
            self.equipos_filtrados = list(self.equipos_dict.values())
        else:
            self.equipos_filtrados = [
                e for e in self.equipos_dict.values()
                if termino in str(e.get('nombre', '')).lower() or
                   termino in str(e.get('marca', '')).lower() or
                   termino in str(e.get('codigo_inventario', '')).lower() or
                   termino in str(e.get('numero_serie', '')).lower() or
                   termino in str(self.equipo_docente_responsable.get(str(e.get('_id', '')), '')).lower()
            ]
        
        self._actualizar_tabla_inventario()
    
    def _actualizar_tabla_inventario(self):
        """Actualiza la tabla de inventario"""
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)
        
        # Configurar los estilos de fondo para las filas (colores pastel)
        self.tree_inventario.tag_configure('row_verde', background='#C8E6C9')
        self.tree_inventario.tag_configure('row_amarillo', background='#FFFACD')
        self.tree_inventario.tag_configure('row_rojo', background='#FFB6C1')
        self.tree_inventario.tag_configure('row_gris', background='#E8E8E8')
        
        for equipo in self.equipos_filtrados:
            codigo = equipo.get('codigo_inventario', '')
            nombre = equipo.get('nombre', '')
            marca = equipo.get('marca', '')
            numero_serie = equipo.get('numero_serie', '')
            estado = equipo.get('estado', 'activo')
            
            equipo_id = str(equipo.get('_id', ''))

            if estado == 'activo' and hasattr(self, 'equipos_prestados_ids') and equipo_id in self.equipos_prestados_ids:
                estado = 'prestado'
            
            # Determinar el responsable
            responsable = ''
            if estado == 'prestado' and equipo_id in self.equipo_docente_responsable:
                responsable = self.equipo_docente_responsable[equipo_id]
            else:
                responsable = 'N/A'
            
            # Colorear fila según estado
            if estado == 'dañado':
                tag = 'row_rojo'
            elif estado == 'descartado':
                tag = 'row_gris'
            elif estado == 'prestado':
                tag = 'row_amarillo'
            else:
                tag = 'row_verde'
            
            self.tree_inventario.insert('', 'end', iid=equipo_id, 
                                       values=(codigo, nombre, marca, numero_serie, responsable),
                                       tags=(tag,))
    
    def _abrir_formulario_nuevo_equipo(self):
        """Abre formulario para nuevo equipo"""
        ventana = tk.Toplevel(self.frame)
        ventana.title("Nuevo Equipo")
        ventana.geometry("400x400")
        
        frame = ttk.Frame(ventana, padding="15")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Código Inventario:").grid(row=0, column=0, sticky='w', pady=5)
        entrada_codigo = ttk.Entry(frame)
        entrada_codigo.grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky='w', pady=5)
        entrada_nombre = ttk.Entry(frame)
        entrada_nombre.grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Marca:").grid(row=2, column=0, sticky='w', pady=5)
        entrada_marca = ttk.Entry(frame)
        entrada_marca.grid(row=2, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Número de Serie:").grid(row=3, column=0, sticky='w', pady=5)
        entrada_numero_serie = ttk.Entry(frame)
        entrada_numero_serie.grid(row=3, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Descripción:").grid(row=4, column=0, sticky='w', pady=5)
        entrada_desc = ttk.Entry(frame)
        entrada_desc.grid(row=4, column=1, sticky='ew', pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        def guardar():
            try:
                codigo = entrada_codigo.get().strip()
                nombre = entrada_nombre.get().strip()
                marca = entrada_marca.get().strip()
                numero_serie = entrada_numero_serie.get().strip()
                desc = entrada_desc.get().strip()
                
                if not all([codigo, nombre, marca, numero_serie]):
                    messagebox.showwarning("Advertencia", "Completa todos los campos obligatorios")
                    return
                
                equipo = self.equipo_controller.registrar_equipo(
                    nombre, marca, numero_serie, codigo, desc
                )
                messagebox.showinfo("Éxito", f"Equipo {equipo.nombre} #{equipo.numero_serie} registrado")
                ventana.destroy()
                self.cargar_inventario()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        frame_botones = ttk.Frame(ventana)
        frame_botones.pack(fill='x', padx=15, pady=15)
        
        ttk.Button(frame_botones, text="Guardar", command=guardar).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=ventana.destroy).pack(side='left')
    
    def _editar_equipo(self, event):
        """Edita un equipo"""
        items = self.tree_inventario.selection()
        if not items:
            return
        
        equipo_id = items[0]
        equipo = self.equipos_dict.get(equipo_id, {})
        
        ventana = tk.Toplevel(self.frame)
        ventana.title("Editar Equipo")
        ventana.geometry("400x250")
        
        frame = ttk.Frame(ventana, padding="15")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky='w', pady=5)
        entrada_nombre = ttk.Entry(frame)
        entrada_nombre.insert(0, equipo.get('nombre', ''))
        entrada_nombre.grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Marca:").grid(row=1, column=0, sticky='w', pady=5)
        entrada_marca = ttk.Entry(frame)
        entrada_marca.insert(0, equipo.get('marca', ''))
        entrada_marca.grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Label(frame, text="Número de Serie:").grid(row=2, column=0, sticky='w', pady=5)
        label_numero = ttk.Label(frame, text=equipo.get('numero_serie', ''))
        label_numero.grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Label(frame, text="Descripción:").grid(row=3, column=0, sticky='w', pady=5)
        entrada_desc = ttk.Entry(frame)
        entrada_desc.insert(0, equipo.get('descripcion', ''))
        entrada_desc.grid(row=3, column=1, sticky='ew', pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        def guardar():
            try:
                nombre = entrada_nombre.get().strip()
                marca = entrada_marca.get().strip()
                desc = entrada_desc.get().strip()
                
                equipo = self.equipo_controller.actualizar_equipo(equipo_id, nombre, marca, desc)
                messagebox.showinfo("Éxito", f"Equipo actualizado")
                ventana.destroy()
                self.cargar_inventario()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        frame_botones = ttk.Frame(ventana)
        frame_botones.pack(fill='x', padx=15, pady=15)
        
        ttk.Button(frame_botones, text="Guardar", command=guardar).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=ventana.destroy).pack(side='left')
    
    def _mostrar_menu_contextual_equipo(self, event):
        """Muestra menú contextual"""
        items = self.tree_inventario.selection()
        if not items:
            return
        
        equipo_id = items[0]
        equipo = self.equipos_dict.get(equipo_id, {})
        estado = equipo.get('estado', 'activo')
        
        menu = tk.Menu(self.tree_inventario, tearoff=False)
        menu.add_command(label="✏️ Editar", command=lambda: self._editar_equipo(event))
        
        if estado == 'activo':
            menu.add_command(label="⚠️ Marcar Dañado", command=lambda: self._marcar_danado(equipo_id))
        elif estado == 'dañado':
            menu.add_command(label="🔧 Reparar", command=lambda: self._reparar_equipo(equipo_id))
        
        menu.add_command(label="🗑️ Descartar", command=lambda: self._descartar_equipo(equipo_id))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _marcar_danado(self, equipo_id):
        """Marca equipo como dañado"""
        equipo = self.equipos_dict.get(equipo_id, {})
        
        if messagebox.askyesno("Confirmar", f"¿Marcar {equipo.get('nombre')} #{equipo.get('numero_serie')} como dañado?"):
            try:
                self.equipo_controller.marcar_dañado(equipo_id)
                messagebox.showinfo("Éxito", "Equipo marcado como dañado")
                self.cargar_inventario()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _reparar_equipo(self, equipo_id):
        """Marca equipo como reparado"""
        equipo = self.equipos_dict.get(equipo_id, {})
        
        if messagebox.askyesno("Confirmar", f"¿Reparar {equipo.get('nombre')} #{equipo.get('numero_serie')}?"):
            try:
                self.equipo_controller.reparar_equipo(equipo_id)
                messagebox.showinfo("Éxito", "Equipo marcado como reparado")
                self.cargar_inventario()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _descartar_equipo(self, equipo_id):
        """Descarta un equipo"""
        equipo = self.equipos_dict.get(equipo_id, {})
        
        if messagebox.askyesno("Confirmar", f"¿Descartar {equipo.get('nombre')} #{equipo.get('numero_serie')} permanentemente?"):
            try:
                self.equipo_controller.eliminar_equipo(equipo_id)
                messagebox.showinfo("Éxito", "Equipo descartado")
                self.cargar_inventario()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    # ==================== MÉTODOS TAB HISTORIAL ====================
    def cargar_historial(self):
        """Carga historial de préstamos y devoluciones"""
        try:
            # Préstamos activos
            prestamos = self.prestamo_controller.obtener_activos()
            self.prestamos_activos = [
                p.to_dict() if hasattr(p, 'to_dict') else p for p in (prestamos or [])
            ]
            
            # Devoluciones
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
