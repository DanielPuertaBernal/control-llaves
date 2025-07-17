import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
from datetime import datetime
from helpers.limpieza_programacion import limpiar_programacion, guardar_programacion_limpia
from helpers.gestion_excel import (registrar_entrega, registrar_devolucion, 
                                 inicializar_registro, verificar_llave_entregada, obtener_llaves_pendientes,
                                 limpiar_numero_documento, obtener_historial_completo, generar_respaldo)
from assets.estilo_tkinter import aplicar_estilo

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Llaves - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.programacion = None
        self.programacion_original = None
        
        inicializar_registro()
        aplicar_estilo(root)
        self.crear_interfaz_principal()

    def crear_interfaz_principal(self):
        """Crea la interfaz principal con pestañas"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título principal
        titulo = ttk.Label(main_frame, text="SISTEMA DE CONTROL DE LLAVES", 
                          font=('Segoe UI', 18, 'bold'))
        titulo.pack(pady=(0, 20))

        # Crear el notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Crear las pestañas
        self.crear_vista_entrega_devolucion()
        self.crear_vista_programacion()
        self.crear_vista_informes()

    def crear_vista_entrega_devolucion(self):
        """Crea la vista de entrega y devolución de llaves"""
        frame_entrega = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame_entrega, text="🔑 Entrega y Devolución")

        # Título de la vista
        titulo_entrega = ttk.Label(frame_entrega, text="GESTIÓN DE LLAVES", 
                                  font=('Segoe UI', 16, 'bold'))
        titulo_entrega.pack(pady=(0, 20))

        # Frame principal dividido en dos columnas
        main_container = ttk.Frame(frame_entrega)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Columna izquierda - Entrega de llaves
        frame_izq = ttk.LabelFrame(main_container, text="ENTREGA DE LLAVES", padding="15")
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Búsqueda de profesor
        ttk.Label(frame_izq, text="Buscar Profesor:").pack(anchor=tk.W, pady=(0, 5))
        
        frame_busqueda = ttk.Frame(frame_izq)
        frame_busqueda.pack(fill=tk.X, pady=(0, 15))
        
        self.entry_busqueda = ttk.Entry(frame_busqueda, font=('Segoe UI', 11))
        self.entry_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_profesor)
        
        btn_buscar = ttk.Button(frame_busqueda, text="🔍 Buscar", 
                               command=self.buscar_profesor, width=10)
        btn_buscar.pack(side=tk.RIGHT)

        # Lista de profesores encontrados
        ttk.Label(frame_izq, text="Seleccione Profesor:").pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para la lista con scrollbar
        list_frame = ttk.Frame(frame_izq)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Crear Treeview para mostrar profesores
        columns = ('Profesor', 'Documento', 'Materia', 'Aula', 'Horario')
        self.tree_profesores = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        # Configurar columnas
        self.tree_profesores.heading('Profesor', text='Profesor')
        self.tree_profesores.heading('Documento', text='Documento')
        self.tree_profesores.heading('Materia', text='Materia')
        self.tree_profesores.heading('Aula', text='Aula')
        self.tree_profesores.heading('Horario', text='Horario')

        # Ajustar ancho de columnas
        self.tree_profesores.column('Profesor', width=120)
        self.tree_profesores.column('Documento', width=90)
        self.tree_profesores.column('Materia', width=100)
        self.tree_profesores.column('Aula', width=60)
        self.tree_profesores.column('Horario', width=90)

        # Scrollbar para la lista
        scrollbar_prof = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_profesores.yview)
        self.tree_profesores.configure(yscrollcommand=scrollbar_prof.set)

        # Pack de la lista y scrollbar
        self.tree_profesores.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_prof.pack(side=tk.RIGHT, fill=tk.Y)

        # Label de información de búsqueda
        self.info_label = ttk.Label(frame_izq, text="Escriba nombre o número de documento para buscar", 
                                   foreground="gray")
        self.info_label.pack(pady=(0, 10))

        # Botón de entrega
        btn_entregar = ttk.Button(frame_izq, text="🔑 ENTREGAR LLAVE", 
                                 command=self.entregar_llave_seleccionada,
                                 style="Accent.TButton")
        btn_entregar.pack(pady=10, fill=tk.X)

        # Columna derecha - Devolución de llaves
        frame_der = ttk.LabelFrame(main_container, text="DEVOLUCIÓN DE LLAVES", padding="15")
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Lista de llaves prestadas
        ttk.Label(frame_der, text="Llaves Prestadas Actualmente:").pack(anchor=tk.W, pady=(0, 5))

        # Frame para la lista de prestadas
        list_prestadas_frame = ttk.Frame(frame_der)
        list_prestadas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Treeview para llaves prestadas
        columns_prestadas = ('Profesor', 'Documento', 'Aula', 'Fecha', 'Hora')
        self.tree_prestadas = ttk.Treeview(list_prestadas_frame, columns=columns_prestadas, 
                                         show='headings', height=10)

        # Configurar columnas prestadas
        self.tree_prestadas.heading('Profesor', text='Profesor')
        self.tree_prestadas.heading('Documento', text='Documento')
        self.tree_prestadas.heading('Aula', text='Aula')
        self.tree_prestadas.heading('Fecha', text='Fecha')
        self.tree_prestadas.heading('Hora', text='Hora')

        # Ajustar ancho de columnas prestadas
        self.tree_prestadas.column('Profesor', width=120)
        self.tree_prestadas.column('Documento', width=90)
        self.tree_prestadas.column('Aula', width=60)
        self.tree_prestadas.column('Fecha', width=80)
        self.tree_prestadas.column('Hora', width=70)

        # Scrollbar para prestadas
        scrollbar_prest = ttk.Scrollbar(list_prestadas_frame, orient=tk.VERTICAL, 
                                      command=self.tree_prestadas.yview)
        self.tree_prestadas.configure(yscrollcommand=scrollbar_prest.set)

        # Pack de prestadas
        self.tree_prestadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_prest.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones de devolución
        btn_frame = ttk.Frame(frame_der)
        btn_frame.pack(fill=tk.X, pady=10)

        btn_devolver = ttk.Button(btn_frame, text="↩️ DEVOLVER LLAVE", 
                                 command=self.devolver_llave_seleccionada,
                                 style="Accent.TButton")
        btn_devolver.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_actualizar = ttk.Button(btn_frame, text="🔄 ACTUALIZAR", 
                                   command=self.actualizar_llaves_prestadas,
                                   width=12)
        btn_actualizar.pack(side=tk.RIGHT)

    def crear_vista_programacion(self):
        """Crea la vista de gestión de programación"""
        frame_prog = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame_prog, text="📅 Programación")

        # Título de la vista
        titulo_prog = ttk.Label(frame_prog, text="GESTIÓN DE PROGRAMACIÓN ACADÉMICA", 
                               font=('Segoe UI', 16, 'bold'))
        titulo_prog.pack(pady=(0, 20))

        # Frame superior - Controles
        frame_controles = ttk.Frame(frame_prog)
        frame_controles.pack(fill=tk.X, pady=(0, 15))

        # Frame izquierdo - Cargar programación
        frame_cargar = ttk.LabelFrame(frame_controles, text="CARGAR PROGRAMACIÓN", padding="10")
        frame_cargar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Archivo de programación
        frame_archivo = ttk.Frame(frame_cargar)
        frame_archivo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_archivo, text="Archivo de Programación:").pack(side=tk.LEFT)
        btn_cargar = ttk.Button(frame_archivo, text="📁 Seleccionar Archivo", 
                               command=self.cargar_programacion)
        btn_cargar.pack(side=tk.RIGHT)

        # Información del archivo cargado
        self.label_archivo = ttk.Label(frame_cargar, text="No hay archivo cargado", 
                                      foreground="red")
        self.label_archivo.pack(anchor=tk.W)

        # Frame derecho - Filtros rápidos
        frame_filtros = ttk.LabelFrame(frame_controles, text="FILTROS RÁPIDOS", padding="10")
        frame_filtros.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Filtro por día
        frame_dia = ttk.Frame(frame_filtros)
        frame_dia.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame_dia, text="Día:").pack(side=tk.LEFT)
        self.combo_dia_prog = ttk.Combobox(frame_dia, values=['TODOS', 'LUNES', 'MARTES', 
                                          'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO'], 
                                          state="readonly", width=12)
        self.combo_dia_prog.set('TODOS')
        self.combo_dia_prog.pack(side=tk.RIGHT)
        self.combo_dia_prog.bind('<<ComboboxSelected>>', self.filtrar_programacion_rapido)

        # Filtro por aula
        frame_aula = ttk.Frame(frame_filtros)
        frame_aula.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame_aula, text="Aula:").pack(side=tk.LEFT)
        self.combo_aula_prog = ttk.Combobox(frame_aula, state="readonly", width=12)
        self.combo_aula_prog.pack(side=tk.RIGHT)
        self.combo_aula_prog.bind('<<ComboboxSelected>>', self.filtrar_programacion_rapido)

        # Botón limpiar filtros
        btn_limpiar = ttk.Button(frame_filtros, text="🗑️ Limpiar", 
                                command=self.limpiar_filtros_prog, width=10)
        btn_limpiar.pack(pady=5)

        # Frame principal - Lista de programación
        frame_lista = ttk.LabelFrame(frame_prog, text="PROGRAMACIÓN ACTUAL", padding="10")
        frame_lista.pack(fill=tk.BOTH, expand=True)

        # Crear Treeview para programación
        columns_prog = ('Profesor', 'Documento', 'Materia', 'Aula', 'Día', 'Horario', 'Estudiantes')
        self.tree_programacion = ttk.Treeview(frame_lista, columns=columns_prog, 
                                            show='headings', height=15)

        # Configurar columnas de programación
        for col in columns_prog:
            self.tree_programacion.heading(col, text=col)
            
        # Ajustar ancho de columnas
        self.tree_programacion.column('Profesor', width=150)
        self.tree_programacion.column('Documento', width=100)
        self.tree_programacion.column('Materia', width=120)
        self.tree_programacion.column('Aula', width=70)
        self.tree_programacion.column('Día', width=80)
        self.tree_programacion.column('Horario', width=100)
        self.tree_programacion.column('Estudiantes', width=80)

        # Scrollbars para programación
        scrollbar_prog_v = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, 
                                       command=self.tree_programacion.yview)
        scrollbar_prog_h = ttk.Scrollbar(frame_lista, orient=tk.HORIZONTAL, 
                                       command=self.tree_programacion.xview)
        
        self.tree_programacion.configure(yscrollcommand=scrollbar_prog_v.set,
                                       xscrollcommand=scrollbar_prog_h.set)

        # Grid para programación con scrollbars
        self.tree_programacion.grid(row=0, column=0, sticky='nsew')
        scrollbar_prog_v.grid(row=0, column=1, sticky='ns')
        scrollbar_prog_h.grid(row=1, column=0, sticky='ew')

        # Configurar grid
        frame_lista.grid_rowconfigure(0, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)

        # Frame inferior - Botones de acción
        frame_acciones = ttk.Frame(frame_prog)
        frame_acciones.pack(fill=tk.X, pady=15)

        btn_ver_completa = ttk.Button(frame_acciones, text="📊 Ver Programación Completa", 
                                     command=self.mostrar_ventana_programacion_completa)
        btn_ver_completa.pack(side=tk.LEFT, padx=(0, 10))

        btn_exportar = ttk.Button(frame_acciones, text="📤 Exportar Vista Actual", 
                                 command=self.exportar_programacion_actual)
        btn_exportar.pack(side=tk.LEFT, padx=(0, 10))

    def crear_vista_informes(self):
        """Crea la vista de informes y reportes"""
        frame_informes = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame_informes, text="📊 Informes")

        # Título de la vista
        titulo_informes = ttk.Label(frame_informes, text="SISTEMA DE INFORMES Y REPORTES", 
                                   font=('Segoe UI', 16, 'bold'))
        titulo_informes.pack(pady=(0, 20))

        # Frame principal dividido en dos columnas
        main_informes = ttk.Frame(frame_informes)
        main_informes.pack(fill=tk.BOTH, expand=True)

        # Columna izquierda - Configuración de informes
        frame_config = ttk.LabelFrame(main_informes, text="CONFIGURACIÓN DE INFORMES", padding="15")
        frame_config.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Sección 1: Tipo de informe
        ttk.Label(frame_config, text="TIPO DE INFORME:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        self.tipo_informe = tk.StringVar(value="llaves_pendientes")
        
        ttk.Radiobutton(frame_config, text="🔴 Llaves No Devueltas", 
                       variable=self.tipo_informe, value="llaves_pendientes").pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(frame_config, text="📋 Todas las Entregas", 
                       variable=self.tipo_informe, value="todas_entregas").pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(frame_config, text="✅ Entregas por Fecha", 
                       variable=self.tipo_informe, value="entregas_fecha").pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(frame_config, text="� Entregas por Profesor", 
                       variable=self.tipo_informe, value="entregas_profesor").pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(frame_config, text="🏢 Entregas por Aula", 
                       variable=self.tipo_informe, value="entregas_aula").pack(anchor=tk.W, pady=2)

        # Separador
        ttk.Separator(frame_config, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # Sección 2: Filtros por fecha
        ttk.Label(frame_config, text="FILTROS TEMPORALES:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        # Fecha específica
        frame_fecha = ttk.Frame(frame_config)
        frame_fecha.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_fecha, text="Fecha específica:").pack(anchor=tk.W)
        self.entry_fecha = ttk.Entry(frame_fecha, width=20)
        self.entry_fecha.pack(fill=tk.X)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Rango de fechas
        frame_rango = ttk.Frame(frame_config)
        frame_rango.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_rango, text="Desde:").pack(anchor=tk.W)
        self.entry_fecha_desde = ttk.Entry(frame_rango, width=20)
        self.entry_fecha_desde.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame_rango, text="Hasta:").pack(anchor=tk.W)
        self.entry_fecha_hasta = ttk.Entry(frame_rango, width=20)
        self.entry_fecha_hasta.pack(fill=tk.X)

        # Separador
        ttk.Separator(frame_config, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # Sección 3: Filtros adicionales
        ttk.Label(frame_config, text="FILTROS ADICIONALES:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        # Filtro por profesor
        ttk.Label(frame_config, text="Profesor específico:").pack(anchor=tk.W)
        self.entry_profesor_filtro = ttk.Entry(frame_config, width=20)
        self.entry_profesor_filtro.pack(fill=tk.X, pady=(0, 5))

        # Filtro por aula
        ttk.Label(frame_config, text="Aula específica:").pack(anchor=tk.W)
        self.entry_aula_filtro = ttk.Entry(frame_config, width=20)
        self.entry_aula_filtro.pack(fill=tk.X, pady=(0, 15))

        # Botones de acción
        btn_generar = ttk.Button(frame_config, text="📊 GENERAR INFORME", 
                                command=self.generar_informe,
                                style="Accent.TButton")
        btn_generar.pack(fill=tk.X, pady=(0, 10))

        btn_exportar_inf = ttk.Button(frame_config, text="📤 EXPORTAR A EXCEL", 
                                     command=self.exportar_informe)
        btn_exportar_inf.pack(fill=tk.X, pady=(0, 10))

        btn_limpiar_inf = ttk.Button(frame_config, text="🗑️ LIMPIAR FILTROS", 
                                    command=self.limpiar_filtros_informe)
        btn_limpiar_inf.pack(fill=tk.X)

        # Columna derecha - Visualización de informes
        frame_resultado = ttk.LabelFrame(main_informes, text="RESULTADO DEL INFORME", padding="15")
        frame_resultado.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Frame para estadísticas rápidas
        frame_stats = ttk.Frame(frame_resultado)
        frame_stats.pack(fill=tk.X, pady=(0, 15))

        # Etiquetas de estadísticas
        self.label_total_registros = ttk.Label(frame_stats, text="Total de registros: 0", 
                                              font=('Segoe UI', 10, 'bold'))
        self.label_total_registros.pack(side=tk.LEFT, padx=(0, 20))

        self.label_llaves_pendientes = ttk.Label(frame_stats, text="Llaves pendientes: 0", 
                                                font=('Segoe UI', 10, 'bold'), foreground="red")
        self.label_llaves_pendientes.pack(side=tk.LEFT)

        # Treeview para mostrar resultados del informe
        frame_tree_inf = ttk.Frame(frame_resultado)
        frame_tree_inf.pack(fill=tk.BOTH, expand=True)

        # Columnas dinámicas según el tipo de informe
        self.tree_informe = ttk.Treeview(frame_tree_inf, show='headings', height=20)

        # Scrollbars para el informe
        scrollbar_inf_v = ttk.Scrollbar(frame_tree_inf, orient=tk.VERTICAL, 
                                       command=self.tree_informe.yview)
        scrollbar_inf_h = ttk.Scrollbar(frame_tree_inf, orient=tk.HORIZONTAL, 
                                       command=self.tree_informe.xview)
        
        self.tree_informe.configure(yscrollcommand=scrollbar_inf_v.set,
                                   xscrollcommand=scrollbar_inf_h.set)

        # Grid para informe con scrollbars
        self.tree_informe.grid(row=0, column=0, sticky='nsew')
        scrollbar_inf_v.grid(row=0, column=1, sticky='ns')
        scrollbar_inf_h.grid(row=1, column=0, sticky='ew')

        # Configurar grid
        frame_tree_inf.grid_rowconfigure(0, weight=1)
        frame_tree_inf.grid_columnconfigure(0, weight=1)

        # Frame inferior con información adicional
        self.label_info_informe = ttk.Label(frame_resultado, 
                                           text="Seleccione un tipo de informe y haga clic en 'Generar Informe'", 
                                           foreground="blue", font=('Segoe UI', 10))
        self.label_info_informe.pack(pady=10)

    # ============ FUNCIONES VISTA ENTREGA/DEVOLUCIÓN ============
    
    def buscar_profesor(self, event=None):
        """Busca profesores en la programación por nombre o documento"""
        if self.programacion is None:
            messagebox.showwarning("Advertencia", "Primero debe cargar una programación.")
            return

        termino = self.entry_busqueda.get().strip().upper()
        
        # Limpiar lista anterior
        for item in self.tree_profesores.get_children():
            self.tree_profesores.delete(item)

        if len(termino) < 2:
            return

        # Crear una copia de la programación con documentos limpios para búsqueda
        programacion_busqueda = self.programacion.copy()
        programacion_busqueda['nroidenti_limpio'] = programacion_busqueda['nroidenti'].astype(str).str.replace('.0', '', regex=False)

        # Filtrar profesores que coincidan por nombre O por documento
        resultados = programacion_busqueda[
            (programacion_busqueda['profesor'].str.contains(termino, case=False, na=False)) |
            (programacion_busqueda['nroidenti_limpio'].str.contains(termino, case=False, na=False))
        ]

        # Agregar resultados al tree
        count = 0
        for _, fila in resultados.iterrows():
            documento = limpiar_numero_documento(str(fila['nroidenti']))
            self.tree_profesores.insert('', 'end', values=(
                fila['profesor'],
                documento,
                fila['materia'],
                fila['aula'],
                fila['horario']
            ))
            count += 1
        
        # Mostrar información sobre los resultados
        if hasattr(self, 'info_label') and self.info_label:
            if count == 0:
                self.info_label.config(text=f"No se encontraron profesores para: '{termino}'", foreground="red")
            else:
                self.info_label.config(text=f"Se encontraron {count} profesor(es)", foreground="green")

    def entregar_llave_seleccionada(self):
        """Entrega la llave del profesor seleccionado"""
        seleccion = self.tree_profesores.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un profesor de la lista.")
            return

        item = self.tree_profesores.item(seleccion[0])
        valores = item['values']
        
        # Buscar la información completa en la programación
        documento = str(valores[1])
        profesor = valores[0]
        
        # Buscar en la programación original
        fila_programacion = self.programacion[
            (self.programacion['profesor'] == profesor) & 
            (self.programacion['nroidenti'].astype(str).str.replace('.0', '') == documento)
        ]

        if fila_programacion.empty:
            messagebox.showerror("Error", "No se pudo encontrar la información completa del profesor.")
            return

        fila = fila_programacion.iloc[0]
        
        # Verificar si ya tiene llave prestada
        prestadas = obtener_llaves_pendientes()
        if not prestadas.empty:
            docs_prestadas = [limpiar_numero_documento(str(doc)) for doc in prestadas['nroidenti']]
            if documento in docs_prestadas:
                messagebox.showwarning("Advertencia", 
                                     f"El profesor {profesor} ya tiene una llave prestada.")
                return

        # Preparar información para entrega
        info_entrega = {
            'nroidenti': documento,
            'profesor': fila['profesor'],
            'materia': fila['materia'],
            'aula': fila['aula'],
            'dia': fila['dia'],
            'horario': fila['horario'],
            'nro_estudiantes': fila.get('nro_estudiantes', 0)
        }

        # Confirmar entrega
        respuesta = messagebox.askyesno("Confirmar Entrega", 
                                       f"¿Entregar llave del aula {fila['aula']} a:\n\n"
                                       f"Profesor: {fila['profesor']}\n"
                                       f"Documento: {documento}\n"
                                       f"Materia: {fila['materia']}\n"
                                       f"Horario: {fila['horario']}")

        if respuesta:
            if registrar_entrega(info_entrega):
                messagebox.showinfo("Éxito", 
                                  f"Llave del aula {fila['aula']} entregada correctamente a {fila['profesor']}")
                self.actualizar_llaves_prestadas()
                # Limpiar búsqueda
                self.entry_busqueda.delete(0, tk.END)
                for item in self.tree_profesores.get_children():
                    self.tree_profesores.delete(item)
            else:
                messagebox.showerror("Error", "No se pudo registrar la entrega.")

    def devolver_llave_seleccionada(self):
        """Devuelve la llave seleccionada de la lista de prestadas"""
        seleccion = self.tree_prestadas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una llave prestada de la lista.")
            return

        item = self.tree_prestadas.item(seleccion[0])
        valores = item['values']
        
        # Orden correcto: Profesor(0), Documento(1), Aula(2), Fecha(3), Hora(4)
        profesor = str(valores[0])
        documento = str(valores[1])
        aula = str(valores[2])

        # Confirmar devolución
        respuesta = messagebox.askyesno("Confirmar Devolución", 
                                       f"¿Confirmar devolución de llave?\n\n"
                                       f"Profesor: {profesor}\n"
                                       f"Documento: {documento}\n"
                                       f"Aula: {aula}")

        if respuesta:
            if registrar_devolucion(documento):
                messagebox.showinfo("Éxito", 
                                  f"Llave del aula {aula} devuelta por {profesor}")
                self.actualizar_llaves_prestadas()
            else:
                messagebox.showerror("Error", "No se pudo registrar la devolución.")

    def actualizar_llaves_prestadas(self):
        """Actualiza la lista de llaves prestadas"""
        # Limpiar lista
        for item in self.tree_prestadas.get_children():
            self.tree_prestadas.delete(item)

        # Obtener llaves pendientes
        prestadas = obtener_llaves_pendientes()
        
        if not prestadas.empty:
            for _, fila in prestadas.iterrows():
                documento = limpiar_numero_documento(str(fila['nroidenti']))
                fecha_entrega = fila['fecha_entrega']
                hora_entrega = fila['hora_entrega']
                
                self.tree_prestadas.insert('', 'end', values=(
                    fila['profesor'],
                    documento,
                    fila['aula'],
                    fecha_entrega,
                    hora_entrega
                ))

    # ============ FUNCIONES VISTA PROGRAMACIÓN ============
    
    def cargar_programacion(self):
        """Carga el archivo de programación"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de programación",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            try:
                # Cargar y limpiar programación
                programacion_limpia = limpiar_programacion(archivo)
                
                if programacion_limpia is not None and not programacion_limpia.empty:
                    self.programacion = programacion_limpia.copy()
                    self.programacion_original = programacion_limpia.copy()
                    
                    # Actualizar interfaz
                    self.label_archivo.config(text=f"Archivo: {os.path.basename(archivo)}", 
                                            foreground="green")
                    
                    # Llenar combo de aulas
                    aulas = sorted(self.programacion['aula'].unique())
                    self.combo_aula_prog['values'] = ['TODAS'] + list(aulas)
                    self.combo_aula_prog.set('TODAS')
                    
                    # Mostrar programación en la vista
                    self.mostrar_programacion_en_vista()
                    
                    # Actualizar información general
                    total_registros = len(self.programacion)
                    total_aulas = len(aulas)
                    if hasattr(self, 'info_label'):
                        self.info_label.config(text=f"Programación cargada: {total_registros} registros, {total_aulas} aulas")
                    
                    messagebox.showinfo("Éxito", 
                                      f"Programación cargada correctamente.\n"
                                      f"Registros: {total_registros}\n"
                                      f"Aulas: {total_aulas}")
                else:
                    messagebox.showerror("Error", "No se pudo procesar el archivo de programación.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")
                messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")

    def mostrar_programacion_en_vista(self):
        """Muestra la programación en el treeview de la vista"""
        # Limpiar vista
        for item in self.tree_programacion.get_children():
            self.tree_programacion.delete(item)

        if self.programacion is None:
            return

        # Agregar registros
        for _, fila in self.programacion.iterrows():
            documento = limpiar_numero_documento(str(fila['nroidenti']))
            self.tree_programacion.insert('', 'end', values=(
                fila['profesor'],
                documento,
                fila['materia'],
                fila['aula'],
                fila['dia'],
                fila['horario'],
                fila.get('nro_estudiantes', '')
            ))

    def filtrar_programacion_rapido(self, event=None):
        """Aplica filtros rápidos a la programación"""
        if self.programacion_original is None:
            return

        # Obtener valores de filtros
        dia_seleccionado = self.combo_dia_prog.get()
        aula_seleccionada = self.combo_aula_prog.get()

        # Partir de la programación original
        programacion_filtrada = self.programacion_original.copy()

        # Aplicar filtro de día
        if dia_seleccionado != 'TODOS':
            programacion_filtrada = programacion_filtrada[
                programacion_filtrada['dia'].str.upper() == dia_seleccionado.upper()
            ]

        # Aplicar filtro de aula
        if aula_seleccionada != 'TODAS':
            programacion_filtrada = programacion_filtrada[
                programacion_filtrada['aula'] == aula_seleccionada
            ]

        # Actualizar programación mostrada
        self.programacion = programacion_filtrada
        self.mostrar_programacion_en_vista()

        # Actualizar info
        total = len(programacion_filtrada)
        if hasattr(self, 'info_label'):
            self.info_label.config(text=f"Mostrando {total} registros filtrados")

    def limpiar_filtros_prog(self):
        """Limpia todos los filtros de programación"""
        if self.programacion_original is None:
            return

        self.combo_dia_prog.set('TODOS')
        self.combo_aula_prog.set('TODAS')
        self.programacion = self.programacion_original.copy()
        self.mostrar_programacion_en_vista()
        
        total = len(self.programacion)
        if hasattr(self, 'info_label'):
            self.info_label.config(text=f"Mostrando todos los registros: {total}")

    def exportar_programacion_actual(self):
        """Exporta la programación actualmente mostrada"""
        if self.programacion is None or self.programacion.empty:
            messagebox.showwarning("Advertencia", "No hay programación para exportar.")
            return

        archivo = filedialog.asksaveasfilename(
            title="Guardar programación",
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )

        if archivo:
            try:
                # Crear una copia para exportar con documentos limpios
                prog_export = self.programacion.copy()
                prog_export['nroidenti'] = prog_export['nroidenti'].apply(
                    lambda x: limpiar_numero_documento(str(x))
                )
                
                prog_export.to_excel(archivo, index=False)
                messagebox.showinfo("Éxito", f"Programación exportada a:\n{archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

    def mostrar_estadisticas_prog(self):
        """Muestra estadísticas de la programación"""
        if self.programacion is None:
            messagebox.showwarning("Advertencia", "Primero debe cargar una programación.")
            return

        # Calcular estadísticas
        total_registros = len(self.programacion)
        total_profesores = len(self.programacion['profesor'].unique())
        total_aulas = len(self.programacion['aula'].unique())
        total_materias = len(self.programacion['materia'].unique())
        
        # Estadísticas por día
        por_dia = self.programacion['dia'].value_counts().to_string()
        
        # Aulas más utilizadas
        aulas_frecuentes = self.programacion['aula'].value_counts().head(5).to_string()

        mensaje = f"""ESTADÍSTICAS DE LA PROGRAMACIÓN

📊 RESUMEN GENERAL:
• Total de registros: {total_registros}
• Profesores únicos: {total_profesores}
• Aulas utilizadas: {total_aulas}
• Materias diferentes: {total_materias}

📅 DISTRIBUCIÓN POR DÍA:
{por_dia}

🏢 AULAS MÁS UTILIZADAS:
{aulas_frecuentes}
"""
        
        messagebox.showinfo("Estadísticas de Programación", mensaje)

    # ============ FUNCIONES VISTA INFORMES ============
    
    def generar_informe(self):
        """Genera el informe según la configuración seleccionada"""
        tipo = self.tipo_informe.get()
        
        try:
            if tipo == "llaves_pendientes":
                self.generar_informe_llaves_pendientes()
            elif tipo == "todas_entregas":
                self.generar_informe_todas_entregas()
            elif tipo == "entregas_fecha":
                self.generar_informe_por_fecha()
            elif tipo == "entregas_profesor":
                self.generar_informe_por_profesor()
            elif tipo == "entregas_aula":
                self.generar_informe_por_aula()
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar informe:\n{str(e)}")

    def generar_informe_llaves_pendientes(self):
        """Genera informe de llaves no devueltas"""
        prestadas = obtener_llaves_pendientes()
        
        # Configurar columnas del treeview
        columnas = ('Profesor', 'Documento', 'Aula', 'Materia', 'Fecha Entrega', 'Hora Entrega', 'Días Prestada')
        self.tree_informe['columns'] = columnas
        self.tree_informe['show'] = 'headings'
        
        # Configurar encabezados
        for col in columnas:
            self.tree_informe.heading(col, text=col)
            self.tree_informe.column(col, width=120)

        # Limpiar datos anteriores
        for item in self.tree_informe.get_children():
            self.tree_informe.delete(item)

        if not prestadas.empty:
            for _, fila in prestadas.iterrows():
                documento = limpiar_numero_documento(str(fila['nroidenti']))
                
                # Calcular días prestada
                fecha_entrega = pd.to_datetime(fila['fecha_entrega'])
                dias_prestada = (datetime.now() - fecha_entrega).days
                
                self.tree_informe.insert('', 'end', values=(
                    fila['profesor'],
                    documento,
                    fila['aula'],
                    fila['materia'],
                    fila['fecha_entrega'],
                    fila['hora_entrega'],
                    f"{dias_prestada} días"
                ))

        # Actualizar estadísticas
        total = len(prestadas)
        self.label_total_registros.config(text=f"Total de registros: {total}")
        self.label_llaves_pendientes.config(text=f"Llaves pendientes: {total}")
        self.label_info_informe.config(text=f"Informe generado: {total} llaves no devueltas")

    def generar_informe_todas_entregas(self):
        """Genera informe de todas las entregas registradas"""
        # Usar la función del helper
        try:
            df = obtener_historial_completo()
            
            if df.empty:
                self.label_info_informe.config(text="No hay registros de entregas")
                return

            # Aplicar filtros adicionales
            df_filtrado = self.aplicar_filtros_adicionales(df)
            
            # Configurar columnas
            columnas = ('Profesor', 'Documento', 'Aula', 'Materia', 'Fecha Entrega', 'Hora Entrega', 'Fecha Devolución', 'Estado')
            self.tree_informe['columns'] = columnas
            self.tree_informe['show'] = 'headings'
            
            for col in columnas:
                self.tree_informe.heading(col, text=col)
                self.tree_informe.column(col, width=100)

            # Limpiar datos anteriores
            for item in self.tree_informe.get_children():
                self.tree_informe.delete(item)

            # Cargar datos
            for _, fila in df_filtrado.iterrows():
                documento = limpiar_numero_documento(str(fila['nroidenti']))
                estado = "Devuelta" if pd.notna(fila.get('fecha_devolucion')) else "Prestada"
                fecha_dev = fila.get('fecha_devolucion', '') if pd.notna(fila.get('fecha_devolucion')) else ''
                
                self.tree_informe.insert('', 'end', values=(
                    fila['profesor'],
                    documento,
                    fila['aula'],
                    fila['materia'],
                    fila['fecha_entrega'],
                    fila['hora_entrega'],
                    fecha_dev,
                    estado
                ))

            # Actualizar estadísticas
            total = len(df_filtrado)
            pendientes = len(df_filtrado[df_filtrado['estado'] == 'Entregada'])
            
            self.label_total_registros.config(text=f"Total de registros: {total}")
            self.label_llaves_pendientes.config(text=f"Llaves pendientes: {pendientes}")
            self.label_info_informe.config(text=f"Informe generado: {total} entregas registradas")
            
        except Exception as e:
            self.label_info_informe.config(text=f"Error: {str(e)}")

    def generar_informe_por_fecha(self):
        """Genera informe filtrado por fecha específica"""
        fecha_str = self.entry_fecha.get().strip()
        
        if not fecha_str:
            messagebox.showwarning("Advertencia", "Ingrese una fecha específica (YYYY-MM-DD)")
            return
            
        try:
            # Validar formato de fecha
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
            
            # Leer registros usando la función helper
            df = obtener_historial_completo()
            
            if df.empty:
                self.label_info_informe.config(text="No hay registros para filtrar")
                return
            
            # Filtrar por fecha
            df['fecha_entrega'] = pd.to_datetime(df['fecha_entrega'])
            df_fecha = df[df['fecha_entrega'].dt.date == fecha_obj.date()]
            
            # Aplicar filtros adicionales
            df_filtrado = self.aplicar_filtros_adicionales(df_fecha)
            
            # Mostrar resultados
            self.mostrar_resultados_entregas(df_filtrado)
            
            total = len(df_filtrado)
            self.label_info_informe.config(text=f"Entregas del {fecha_str}: {total} registros")
            
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD (ej: 2025-01-15)")
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar por fecha:\n{str(e)}")

    def generar_informe_por_profesor(self):
        """Genera informe filtrado por profesor específico"""
        profesor_filtro = self.entry_profesor_filtro.get().strip().upper()
        
        if not profesor_filtro:
            messagebox.showwarning("Advertencia", "Ingrese el nombre del profesor para filtrar")
            return
            
        try:
            df = obtener_historial_completo()
            
            if df.empty:
                self.label_info_informe.config(text="No hay registros para filtrar")
                return
            
            # Filtrar por profesor
            df_profesor = df[df['profesor'].str.upper().str.contains(profesor_filtro, na=False)]
            
            # Aplicar otros filtros
            df_filtrado = self.aplicar_filtros_adicionales(df_profesor)
            
            self.mostrar_resultados_entregas(df_filtrado)
            
            total = len(df_filtrado)
            self.label_info_informe.config(text=f"Entregas de {profesor_filtro}: {total} registros")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar por profesor:\n{str(e)}")

    def generar_informe_por_aula(self):
        """Genera informe filtrado por aula específica"""
        aula_filtro = self.entry_aula_filtro.get().strip().upper()
        
        if not aula_filtro:
            messagebox.showwarning("Advertencia", "Ingrese el código del aula para filtrar")
            return
            
        try:
            df = obtener_historial_completo()
            
            if df.empty:
                self.label_info_informe.config(text="No hay registros para filtrar")
                return
            
            # Filtrar por aula
            df_aula = df[df['aula'].str.upper() == aula_filtro]
            
            # Aplicar otros filtros
            df_filtrado = self.aplicar_filtros_adicionales(df_aula)
            
            self.mostrar_resultados_entregas(df_filtrado)
            
            total = len(df_filtrado)
            self.label_info_informe.config(text=f"Entregas del aula {aula_filtro}: {total} registros")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar por aula:\n{str(e)}")

    def aplicar_filtros_adicionales(self, df):
        """Aplica filtros adicionales de fechas y otros"""
        df_resultado = df.copy()
        
        # Filtro por rango de fechas
        fecha_desde = self.entry_fecha_desde.get().strip()
        fecha_hasta = self.entry_fecha_hasta.get().strip()
        
        if fecha_desde or fecha_hasta:
            try:
                df_resultado['fecha_entrega'] = pd.to_datetime(df_resultado['fecha_entrega'])
                
                if fecha_desde:
                    fecha_desde_obj = datetime.strptime(fecha_desde, "%Y-%m-%d")
                    df_resultado = df_resultado[df_resultado['fecha_entrega'] >= fecha_desde_obj]
                    
                if fecha_hasta:
                    fecha_hasta_obj = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                    df_resultado = df_resultado[df_resultado['fecha_entrega'] <= fecha_hasta_obj]
                    
            except ValueError:
                messagebox.showwarning("Advertencia", "Formato de fecha inválido en el rango. Use YYYY-MM-DD")
        
        return df_resultado

    def mostrar_resultados_entregas(self, df):
        """Muestra los resultados de entregas en el treeview"""
        # Configurar columnas
        columnas = ('Profesor', 'Documento', 'Aula', 'Materia', 'Fecha Entrega', 'Hora Entrega', 'Fecha Devolución', 'Estado')
        self.tree_informe['columns'] = columnas
        self.tree_informe['show'] = 'headings'
        
        for col in columnas:
            self.tree_informe.heading(col, text=col)
            self.tree_informe.column(col, width=100)

        # Limpiar datos anteriores
        for item in self.tree_informe.get_children():
            self.tree_informe.delete(item)

        # Cargar datos
        for _, fila in df.iterrows():
            documento = limpiar_numero_documento(str(fila['nroidenti']))
            estado = fila.get('estado', 'Desconocido')
            fecha_dev = fila.get('fecha_devolucion', '') if pd.notna(fila.get('fecha_devolucion')) else ''
            
            self.tree_informe.insert('', 'end', values=(
                fila.get('profesor', ''),
                documento,
                fila.get('aula', ''),
                fila.get('materia', ''),
                fila.get('fecha_entrega', ''),
                fila.get('hora_entrega', ''),
                fecha_dev,
                estado
            ))

        # Actualizar estadísticas
        total = len(df)
        pendientes = len(df[df['estado'] == 'Entregada']) if 'estado' in df.columns else 0
        
        self.label_total_registros.config(text=f"Total de registros: {total}")
        self.label_llaves_pendientes.config(text=f"Llaves pendientes: {pendientes}")

    def exportar_informe(self):
        """Exporta el informe actual a Excel"""
        # Obtener datos del treeview actual
        items = self.tree_informe.get_children()
        if not items:
            messagebox.showwarning("Advertencia", "No hay datos para exportar. Genere un informe primero.")
            return

        archivo = filedialog.asksaveasfilename(
            title="Exportar informe",
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )

        if archivo:
            try:
                # Obtener columnas y datos
                columnas = [self.tree_informe.heading(col)['text'] for col in self.tree_informe['columns']]
                datos = []
                
                for item in items:
                    valores = self.tree_informe.item(item)['values']
                    datos.append(valores)
                
                # Crear DataFrame y exportar
                df_export = pd.DataFrame(datos, columns=columnas)
                
                # Agregar metadatos
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tipo_informe = self.tipo_informe.get()
                
                with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                    df_export.to_excel(writer, sheet_name='Informe', index=False)
                    
                    # Agregar hoja de metadatos
                    metadata = pd.DataFrame([
                        ['Fecha de generación', timestamp],
                        ['Tipo de informe', tipo_informe],
                        ['Total de registros', len(datos)],
                        ['Generado por', 'Sistema de Control de Llaves']
                    ], columns=['Campo', 'Valor'])
                    
                    metadata.to_excel(writer, sheet_name='Metadatos', index=False)
                
                messagebox.showinfo("Éxito", f"Informe exportado a:\n{archivo}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar informe:\n{str(e)}")

    def limpiar_filtros_informe(self):
        """Limpia todos los filtros del informe"""
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.entry_fecha_desde.delete(0, tk.END)
        self.entry_fecha_hasta.delete(0, tk.END)
        self.entry_profesor_filtro.delete(0, tk.END)
        self.entry_aula_filtro.delete(0, tk.END)
        
        self.tipo_informe.set("llaves_pendientes")
        
        # Limpiar resultados
        for item in self.tree_informe.get_children():
            self.tree_informe.delete(item)
            
        self.label_info_informe.config(text="Filtros limpiados. Seleccione un tipo de informe.")

    def actualizar_estadisticas_generales(self):
        """Actualiza las estadísticas generales del sistema"""
        try:
            # Obtener llaves pendientes
            prestadas = obtener_llaves_pendientes()
            pendientes = len(prestadas)
            
            # Intentar obtener total de registros
            try:
                df_total = pd.read_excel('registros_llaves.xlsx')
                total_registros = len(df_total)
            except:
                total_registros = 0
            
            self.label_total_registros.config(text=f"Total de registros: {total_registros}")
            self.label_llaves_pendientes.config(text=f"Llaves pendientes: {pendientes}")
            
        except Exception as e:
            self.label_total_registros.config(text="Total de registros: 0")
            self.label_llaves_pendientes.config(text="Llaves pendientes: 0")

    # ============ FUNCIONES LEGADO (Mantenidas para compatibilidad) ============
    
    def mostrar_ventana_programacion_completa(self):
        """Muestra la ventana de programación completa con filtros avanzados"""
        if self.programacion is None:
            messagebox.showwarning("Advertencia", "Primero debe cargar una programación.")
            return

        # Crear ventana secundaria
        ventana = tk.Toplevel(self.root)
        ventana.title("Programación Completa - Filtros Avanzados")
        ventana.geometry("1200x700")
        ventana.transient(self.root)
        ventana.grab_set()

        # Frame principal
        main_frame = ttk.Frame(ventana, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = ttk.Label(main_frame, text="PROGRAMACIÓN ACADÉMICA COMPLETA", 
                          font=('Segoe UI', 16, 'bold'))
        titulo.pack(pady=(0, 20))

        # Frame de filtros
        frame_filtros = ttk.LabelFrame(main_frame, text="FILTROS AVANZADOS", padding="10")
        frame_filtros.pack(fill=tk.X, pady=(0, 15))

        # Primera fila de filtros
        fila1 = ttk.Frame(frame_filtros)
        fila1.pack(fill=tk.X, pady=(0, 10))

        # Filtro por día
        ttk.Label(fila1, text="Día:").pack(side=tk.LEFT, padx=(0, 5))
        combo_dia = ttk.Combobox(fila1, values=['TODOS'] + ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO'], 
                                state="readonly", width=15)
        combo_dia.set('TODOS')
        combo_dia.pack(side=tk.LEFT, padx=(0, 20))

        # Filtro por aula
        ttk.Label(fila1, text="Aula:").pack(side=tk.LEFT, padx=(0, 5))
        aulas = sorted(self.programacion['aula'].unique())
        combo_aula = ttk.Combobox(fila1, values=['TODAS'] + list(aulas), state="readonly", width=15)
        combo_aula.set('TODAS')
        combo_aula.pack(side=tk.LEFT, padx=(0, 20))

        # Filtro por profesor
        ttk.Label(fila1, text="Profesor:").pack(side=tk.LEFT, padx=(0, 5))
        entry_profesor = ttk.Entry(fila1, width=20)
        entry_profesor.pack(side=tk.LEFT)

        # Segunda fila de filtros
        fila2 = ttk.Frame(frame_filtros)
        fila2.pack(fill=tk.X, pady=(0, 10))

        # Filtro por materia
        ttk.Label(fila2, text="Materia:").pack(side=tk.LEFT, padx=(0, 5))
        entry_materia = ttk.Entry(fila2, width=20)
        entry_materia.pack(side=tk.LEFT, padx=(0, 20))

        # Botones de filtro
        btn_aplicar = ttk.Button(fila2, text="🔍 Aplicar Filtros", 
                               command=lambda: aplicar_filtros_completos())
        btn_aplicar.pack(side=tk.LEFT, padx=(20, 10))

        btn_limpiar_todo = ttk.Button(fila2, text="🗑️ Limpiar Todo", 
                                    command=lambda: limpiar_filtros_completos())
        btn_limpiar_todo.pack(side=tk.LEFT, padx=(0, 10))

        btn_exportar_ventana = ttk.Button(fila2, text="📤 Exportar", 
                                        command=lambda: exportar_programacion_ventana())
        btn_exportar_ventana.pack(side=tk.RIGHT)

        # Frame para la tabla
        frame_tabla = ttk.Frame(main_frame)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        # Crear Treeview
        columns = ('Profesor', 'Documento', 'Materia', 'Aula', 'Día', 'Horario', 'Estudiantes')
        tree_completa = ttk.Treeview(frame_tabla, columns=columns, show='headings', height=20)

        # Configurar columnas
        for col in columns:
            tree_completa.heading(col, text=col, command=lambda c=col: ordenar_por_columna(c))
            tree_completa.column(col, width=120)

        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tree_completa.yview)
        scrollbar_h = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=tree_completa.xview)
        tree_completa.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        # Grid
        tree_completa.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')

        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        # Label de información
        label_info = ttk.Label(main_frame, text="", font=('Segoe UI', 10))
        label_info.pack(pady=10)

        # Variables para ordenamiento
        orden_ascendente = {}

        def cargar_datos(datos=None):
            """Carga datos en la tabla"""
            if datos is None:
                datos = self.programacion

            # Limpiar tabla
            for item in tree_completa.get_children():
                tree_completa.delete(item)

            # Cargar datos
            for _, fila in datos.iterrows():
                documento = limpiar_numero_documento(str(fila['nroidenti']))
                tree_completa.insert('', 'end', values=(
                    fila['profesor'],
                    documento,
                    fila['materia'],
                    fila['aula'],
                    fila['dia'],
                    fila['horario'],
                    fila.get('nro_estudiantes', '')
                ))

            # Actualizar información
            total = len(datos)
            label_info.config(text=f"Mostrando {total} registros de {len(self.programacion)} totales")

        def aplicar_filtros_completos():
            """Aplica todos los filtros seleccionados"""
            datos_filtrados = self.programacion.copy()

            # Filtro por día
            if combo_dia.get() != 'TODOS':
                datos_filtrados = datos_filtrados[
                    datos_filtrados['dia'].str.upper() == combo_dia.get().upper()
                ]

            # Filtro por aula
            if combo_aula.get() != 'TODAS':
                datos_filtrados = datos_filtrados[
                    datos_filtrados['aula'] == combo_aula.get()
                ]

            # Filtro por profesor
            if entry_profesor.get().strip():
                datos_filtrados = datos_filtrados[
                    datos_filtrados['profesor'].str.contains(entry_profesor.get().strip(), case=False, na=False)
                ]

            # Filtro por materia
            if entry_materia.get().strip():
                datos_filtrados = datos_filtrados[
                    datos_filtrados['materia'].str.contains(entry_materia.get().strip(), case=False, na=False)
                ]

            cargar_datos(datos_filtrados)

        def limpiar_filtros_completos():
            """Limpia todos los filtros"""
            combo_dia.set('TODOS')
            combo_aula.set('TODAS')
            entry_profesor.delete(0, tk.END)
            entry_materia.delete(0, tk.END)
            cargar_datos()

        def ordenar_por_columna(columna):
            """Ordena la tabla por la columna seleccionada"""
            # Obtener datos actuales
            items = [(tree_completa.set(item, columna), item) for item in tree_completa.get_children('')]
            
            # Determinar orden
            reverso = orden_ascendente.get(columna, False)
            orden_ascendente[columna] = not reverso
            
            # Ordenar
            items.sort(reverse=reverso)
            
            # Reorganizar
            for index, (val, item) in enumerate(items):
                tree_completa.move(item, '', index)

        def exportar_programacion_ventana():
            """Exporta la programación mostrada en la ventana"""
            items = tree_completa.get_children()
            if not items:
                messagebox.showwarning("Advertencia", "No hay datos para exportar.")
                return

            archivo = filedialog.asksaveasfilename(
                title="Exportar programación completa",
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
            )

            if archivo:
                try:
                    # Obtener datos de la tabla
                    datos_export = []
                    for item in items:
                        valores = tree_completa.item(item)['values']
                        datos_export.append(valores)

                    # Crear DataFrame
                    df_export = pd.DataFrame(datos_export, columns=columns)
                    
                    # Agregar metadatos
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                        df_export.to_excel(writer, sheet_name='Programación', index=False)
                        
                        # Metadatos
                        metadata = pd.DataFrame([
                            ['Fecha de exportación', timestamp],
                            ['Total de registros', len(datos_export)],
                            ['Filtros aplicados', f"Día: {combo_dia.get()}, Aula: {combo_aula.get()}"],
                            ['Generado por', 'Sistema de Control de Llaves']
                        ], columns=['Campo', 'Valor'])
                        
                        metadata.to_excel(writer, sheet_name='Metadatos', index=False)

                    messagebox.showinfo("Éxito", f"Programación exportada a:\n{archivo}")

                except Exception as e:
                    messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

        # Cargar datos iniciales
        cargar_datos()

        # Frame inferior con ayuda
        frame_ayuda = ttk.Frame(main_frame)
        frame_ayuda.pack(fill=tk.X, pady=10)

        btn_ayuda = ttk.Button(frame_ayuda, text="❓ Ayuda", command=mostrar_ayuda_completa)
        btn_ayuda.pack(side=tk.LEFT)

        def mostrar_ayuda_completa():
            """Muestra ayuda para la ventana completa"""
            ayuda = """AYUDA - PROGRAMACIÓN COMPLETA

🔍 FILTROS:
• Día: Filtra clases por día de la semana
• Aula: Muestra solo clases de un aula específica
• Profesor: Busca por nombre del profesor (búsqueda parcial)
• Materia: Busca por nombre de la materia (búsqueda parcial)

📊 ORDENAMIENTO:
• Haga clic en cualquier encabezado de columna para ordenar
• Segundo clic invierte el orden

📤 EXPORTAR:
• Exporta los datos actualmente mostrados (con filtros aplicados)
• Incluye metadatos sobre los filtros y fecha de exportación

🎯 CONSEJOS:
• Combine varios filtros para búsquedas específicas
• Use nombres parciales en los filtros de texto
• Los filtros son sensibles a mayúsculas/minúsculas
"""
        # Frame de información general (debajo de las pestañas)
        self.info_label = ttk.Label(main_frame, text="Sistema listo. Cargue una programación para comenzar.", 
                                   foreground="blue", font=('Segoe UI', 10))
        self.info_label.pack(pady=10)

        # Inicializar valores
        self.actualizar_llaves_prestadas()
        self.actualizar_estadisticas_generales()
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = ttk.Label(main_frame, text="SISTEMA DE CONTROL DE LLAVES", 
                          font=('Segoe UI', 16, 'bold'))
        titulo.pack(pady=(0, 20))

        # Frame para carga de programación
        frame_carga = ttk.LabelFrame(main_frame, text="Gestión de Programación", padding="10")
        frame_carga.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(frame_carga, text="Cargar Programación", 
                  command=self.cargar_programacion).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_carga, text="Limpiar y Guardar Programación", 
                  command=self.limpiar_y_guardar).pack(side=tk.LEFT)

        # Frame para búsqueda
        frame_busqueda = ttk.LabelFrame(main_frame, text="Búsqueda de Clases", padding="10")
        frame_busqueda.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_busqueda, text="Número de Documento:").pack(side=tk.LEFT)
        self.doc_entry = ttk.Entry(frame_busqueda, width=20)
        self.doc_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.doc_entry.bind('<Return>', lambda e: self.buscar_clases())

        ttk.Button(frame_busqueda, text="Buscar Clases del Día", 
                  command=self.buscar_clases).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_busqueda, text="Ver Todas las Clases", 
                  command=self.ver_todas_clases).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_busqueda, text="Ver Programación Completa", 
                  command=self.ver_programacion_completa).pack(side=tk.LEFT)

        # Frame para acciones
        frame_acciones = ttk.Frame(main_frame)
        frame_acciones.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(frame_acciones, text="🔑 Entregar Llave", 
                  command=self.entregar_llave).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_acciones, text="🔄 Devolver Llave", 
                  command=self.devolver_llave).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_acciones, text="📋 Llaves Entregadas", 
                  command=self.ver_llaves_entregadas).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_acciones, text="📚 Programación Completa", 
                  command=self.ver_programacion_completa).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_acciones, text="📊 Historial", 
                  command=self.ver_historial).pack(side=tk.LEFT)

        # Frame para la tabla
        frame_tabla = ttk.LabelFrame(main_frame, text="Clases del Profesor", padding="10")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tabla con scrollbar
        tabla_frame = ttk.Frame(frame_tabla)
        tabla_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        scrollbar_v = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL)
        scrollbar_h = ttk.Scrollbar(tabla_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(tabla_frame, 
                                columns=("profesor", "materia", "aula", "horario", "dia", "estudiantes", "estado"), 
                                show="headings",
                                yscrollcommand=scrollbar_v.set,
                                xscrollcommand=scrollbar_h.set)

        # Configurar scrollbars
        scrollbar_v.config(command=self.tree.yview)
        scrollbar_h.config(command=self.tree.xview)

        # Configurar columnas
        columnas = {
            "profesor": ("Profesor", 200),
            "materia": ("Materia", 200),
            "aula": ("Aula", 80),
            "horario": ("Horario", 120),
            "dia": ("Día", 80),
            "estudiantes": ("Est.", 60),
            "estado": ("Estado", 120)
        }

        for col, (texto, ancho) in columnas.items():
            self.tree.heading(col, text=texto)
            self.tree.column(col, width=ancho, minwidth=50)

        # Posicionar elementos
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)

        # Nuevo frame para llaves prestadas
        frame_llaves_prestadas = ttk.LabelFrame(main_frame, text="🔑 Llaves Actualmente Prestadas", padding="10")
        frame_llaves_prestadas.pack(fill=tk.X, pady=(0, 10))

        # Crear frame interno para organizar el contenido
        contenido_prestadas = ttk.Frame(frame_llaves_prestadas)
        contenido_prestadas.pack(fill=tk.BOTH, expand=True)

        # Tabla de llaves prestadas (más compacta)
        self.tree_prestadas = ttk.Treeview(contenido_prestadas,
                                          columns=("doc_prestada", "profesor_prestada", "aula_prestada", "hora_prestada"),
                                          show="headings",
                                          height=6)

        # Configurar columnas de llaves prestadas
        columnas_prestadas = {
            "doc_prestada": ("Documento", 100),
            "profesor_prestada": ("Profesor", 180),
            "aula_prestada": ("Aula", 80),
            "hora_prestada": ("Hora Entrega", 130)
        }

        for col, (texto, ancho) in columnas_prestadas.items():
            self.tree_prestadas.heading(col, text=texto)
            self.tree_prestadas.column(col, width=ancho, minwidth=50)

        self.tree_prestadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind para doble clic en llaves prestadas
        self.tree_prestadas.bind('<Double-1>', self.devolver_desde_prestadas)

        # Scrollbar para tabla de prestadas
        scrollbar_prestadas = ttk.Scrollbar(contenido_prestadas, orient=tk.VERTICAL, command=self.tree_prestadas.yview)
        self.tree_prestadas.configure(yscrollcommand=scrollbar_prestadas.set)
        scrollbar_prestadas.pack(side=tk.RIGHT, fill=tk.Y)

        # Botón de actualizar llaves prestadas
        frame_btn_prestadas = ttk.Frame(frame_llaves_prestadas)
        frame_btn_prestadas.pack(fill=tk.X, pady=(5, 0))

        self.label_total_prestadas = ttk.Label(frame_btn_prestadas, text="Total: 0 llaves prestadas", 
                                              font=('Segoe UI', 9, 'bold'), foreground="red")
        self.label_total_prestadas.pack(side=tk.LEFT)

        ttk.Button(frame_btn_prestadas, text="🔄 Actualizar", 
                  command=self.actualizar_llaves_prestadas).pack(side=tk.RIGHT)

        # Frame de información
        self.info_label = ttk.Label(main_frame, text="Sistema listo. Cargue una programación para comenzar.", 
                                   foreground="blue")
        # Info label para mostrar estados del sistema
        self.info_label = ttk.Label(main_frame, text="Sistema listo. Cargue una programación para comenzar.", 
                                   foreground="blue", font=('Segoe UI', 10))
        self.info_label.pack(pady=10)

        # Inicializar valores
        self.actualizar_llaves_prestadas()
        self.actualizar_estadisticas_generales()

    def limpiar_y_guardar(self):
        if self.programacion_original is None:
            messagebox.showwarning("Advertencia", "Primero debe cargar una programación")
            return

        try:
            archivo_salida = filedialog.asksaveasfilename(
                title="Guardar programación limpia",
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            
            if archivo_salida:
                ruta_guardada = guardar_programacion_limpia(self.programacion_original, archivo_salida)
                messagebox.showinfo("Éxito", 
                    f"Programación limpia guardada en:\n{ruta_guardada}")
                if hasattr(self, 'info_label'):
                    self.info_label.config(
                        text=f"Archivo limpio guardado: {ruta_guardada}",
                        foreground="green"
                    )
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar archivo:\n{str(e)}")

    def buscar_clases(self):
        doc = self.doc_entry.get().strip()
        if not doc:
            messagebox.showwarning("Advertencia", "Ingrese un número de documento")
            return

        if self.programacion is None:
            messagebox.showerror("Error", "Primero debe cargar una programación")
            return

        try:
            # Limpiar el número de documento para evitar formato .0
            doc_limpio = limpiar_numero_documento(doc)
            
            # Obtener día actual en español
            dias_semana = {
                'Monday': 'LUNES',
                'Tuesday': 'MARTES', 
                'Wednesday': 'MIÉRCOLES',
                'Thursday': 'JUEVES',
                'Friday': 'VIERNES',
                'Saturday': 'SÁBADO',
                'Sunday': 'DOMINGO'
            }
            
            hoy = datetime.now().strftime('%A')
            dia_espanol = dias_semana.get(hoy, hoy.upper())
            
            # Buscar clases del profesor para el día actual
            clases = self.programacion[
                (self.programacion['nroidenti'].astype(str) == doc_limpio) & 
                (self.programacion['dia'] == dia_espanol)
            ]
            
            self.mostrar_clases(clases, f"Clases de hoy ({dia_espanol}) para documento: {doc_limpio}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clases:\n{str(e)}")

    def ver_todas_clases(self):
        doc = self.doc_entry.get().strip()
        if not doc:
            messagebox.showwarning("Advertencia", "Ingrese un número de documento")
            return

        if self.programacion is None:
            messagebox.showerror("Error", "Primero debe cargar una programación")
            return

        try:
            # Limpiar el número de documento para evitar formato .0
            doc_limpio = limpiar_numero_documento(doc)
            
            clases = self.programacion[self.programacion['nroidenti'].astype(str) == doc_limpio]
            self.mostrar_clases(clases, f"Todas las clases para documento: {doc_limpio}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clases:\n{str(e)}")

    def mostrar_clases(self, clases, titulo):
        self.tree.delete(*self.tree.get_children())
        
        if clases.empty:
            if hasattr(self, 'info_label'):
                self.info_label.config(text="No se encontraron clases para este documento", foreground="orange")
            return

        for _, fila in clases.iterrows():
            # Verificar si ya hay una llave entregada
            llave_entregada = verificar_llave_entregada(
                fila['nroidenti'], 
                fila['materia'], 
                fila['aula']
            )
            
            estado = "🔑 Entregada" if llave_entregada else "⭕ Disponible"
            
            self.tree.insert('', 'end', values=(
                fila.get('profesor', ''),
                fila['materia'],
                fila['aula'],
                fila['horario'],
                fila['dia'],
                fila.get('nro_estudiantes', ''),
                estado
            ))
        
        if hasattr(self, 'info_label'):
            self.info_label.config(text=f"{titulo} - {len(clases)} clases encontradas", foreground="blue")

    def entregar_llave(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una clase de la tabla")
            return

        valores = self.tree.item(seleccion[0])['values']
        if valores[6] == "🔑 Entregada":
            messagebox.showwarning("Advertencia", "Esta llave ya está entregada")
            return

        try:
            doc = self.doc_entry.get().strip()
            # Limpiar el número de documento
            doc_limpio = limpiar_numero_documento(doc)
            
            info_clase = {
                'nroidenti': doc_limpio,
                'profesor': valores[0],
                'materia': valores[1],
                'aula': valores[2],
                'horario': valores[3],
                'dia': valores[4],
                'nro_estudiantes': valores[5]
            }
            
            if registrar_entrega(info_clase):
                messagebox.showinfo("Éxito", f"Llave entregada para {valores[1]} en aula {valores[2]}")
                # Actualizar las vistas
                self.buscar_clases()
                self.actualizar_llaves_prestadas()
            else:
                messagebox.showerror("Error", "No se pudo registrar la entrega")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al entregar llave:\n{str(e)}")

    def devolver_llave(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una clase de la tabla")
            return

        valores = self.tree.item(seleccion[0])['values']
        if valores[6] != "🔑 Entregada":
            messagebox.showwarning("Advertencia", "Esta llave no está entregada")
            return

        try:
            doc = self.doc_entry.get().strip()
            # Limpiar el número de documento
            doc_limpio = limpiar_numero_documento(doc)
            
            if registrar_devolucion(doc_limpio, valores[1], valores[2]):
                messagebox.showinfo("Éxito", f"Llave devuelta para {valores[1]} en aula {valores[2]}")
                # Actualizar las vistas
                self.buscar_clases()
                self.actualizar_llaves_prestadas()
            else:
                messagebox.showerror("Error", "No se encontró la llave entregada para devolver")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al devolver llave:\n{str(e)}")

    def ver_llaves_entregadas(self):
        try:
            llaves_pendientes = obtener_llaves_pendientes()
            
            if llaves_pendientes.empty:
                messagebox.showinfo("Información", "No hay llaves entregadas actualmente")
                return

            # Crear ventana para mostrar llaves entregadas
            self.mostrar_ventana_llaves_entregadas(llaves_pendientes)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar llaves entregadas:\n{str(e)}")

    def mostrar_ventana_llaves_entregadas(self, llaves):
        ventana = tk.Toplevel(self.root)
        ventana.title("Llaves Entregadas")
        ventana.geometry("800x400")
        
        frame = ttk.Frame(ventana, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="LLAVES ACTUALMENTE ENTREGADAS", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 10))
        
        # Crear tabla
        tree = ttk.Treeview(frame, 
                           columns=("profesor", "materia", "aula", "horario", "entrega"), 
                           show="headings")
        
        tree.heading("profesor", text="Profesor")
        tree.heading("materia", text="Materia") 
        tree.heading("aula", text="Aula")
        tree.heading("horario", text="Horario")
        tree.heading("entrega", text="Hora Entrega")
        
        for _, fila in llaves.iterrows():
            tree.insert('', 'end', values=(
                fila['profesor'],
                fila['materia'], 
                fila['aula'],
                fila['horario'],
                fila['hora_entrega']
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)

    def ver_historial(self):
        try:
            historial = obtener_historial_completo()
            
            if historial.empty:
                messagebox.showinfo("Información", "No hay registros en el historial")
                return

            # Crear ventana para mostrar historial
            self.mostrar_ventana_historial(historial)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar historial:\n{str(e)}")

    def mostrar_ventana_historial(self, historial):
        ventana = tk.Toplevel(self.root)
        ventana.title("Historial de Llaves")
        ventana.geometry("1000x500")
        
        frame = ttk.Frame(ventana, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="HISTORIAL COMPLETO DE LLAVES", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 10))
        
        # Crear tabla con scrollbar
        tabla_frame = ttk.Frame(frame)
        tabla_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tabla_frame)
        tree = ttk.Treeview(tabla_frame, 
                           columns=("documento", "profesor", "materia", "aula", "estado", "entrega", "devolucion"), 
                           show="headings",
                           yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=tree.yview)
        
        # Configurar columnas
        tree.heading("documento", text="Documento")
        tree.heading("profesor", text="Profesor")
        tree.heading("materia", text="Materia")
        tree.heading("aula", text="Aula") 
        tree.heading("estado", text="Estado")
        tree.heading("entrega", text="Hora Entrega")
        tree.heading("devolucion", text="Hora Devolución")
        
        for _, fila in historial.iterrows():
            tree.insert('', 'end', values=(
                fila['nroidenti'],
                fila['profesor'],
                fila['materia'],
                fila['aula'],
                fila['estado'],
                fila['hora_entrega'],
                fila.get('hora_devolucion', '')
            ))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def ver_programacion_completa(self):
        """Muestra la programación completa con filtros por día"""
        if self.programacion is None:
            messagebox.showerror("Error", "Primero debe cargar una programación")
            return

        try:
            # Crear ventana para la programación completa
            self.mostrar_ventana_programacion_completa()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar programación:\n{str(e)}")

    def mostrar_ventana_programacion_completa(self):
        """Crea una ventana para mostrar toda la programación con filtros"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Programación Académica Completa")
        ventana.geometry("1200x700")
        
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="PROGRAMACIÓN ACADÉMICA COMPLETA", 
                 font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # Frame para filtros
        frame_filtros = ttk.LabelFrame(main_frame, text="Filtros", padding="10")
        frame_filtros.pack(fill=tk.X, pady=(0, 10))
        
        # Filtro por día
        ttk.Label(frame_filtros, text="Filtrar por día:").pack(side=tk.LEFT)
        
        self.combo_dia = ttk.Combobox(frame_filtros, width=15, state="readonly")
        dias_disponibles = ["TODOS"] + sorted(self.programacion['dia'].unique().tolist())
        self.combo_dia['values'] = dias_disponibles
        self.combo_dia.set("TODOS")
        self.combo_dia.pack(side=tk.LEFT, padx=(5, 10))
        self.combo_dia.bind('<<ComboboxSelected>>', self.filtrar_por_dia)
        
        # Filtro por aula
        ttk.Label(frame_filtros, text="Filtrar por aula:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.combo_aula = ttk.Combobox(frame_filtros, width=15, state="readonly")
        aulas_disponibles = ["TODAS"] + sorted(self.programacion['aula'].unique().tolist())
        self.combo_aula['values'] = aulas_disponibles
        self.combo_aula.set("TODAS")
        self.combo_aula.pack(side=tk.LEFT, padx=(5, 10))
        self.combo_aula.bind('<<ComboboxSelected>>', self.filtrar_por_aula)
        
        # Botón para limpiar filtros
        ttk.Button(frame_filtros, text="Limpiar Filtros", 
                  command=self.limpiar_filtros_programacion).pack(side=tk.LEFT, padx=(20, 0))
        
        # Botón de ayuda
        ttk.Button(frame_filtros, text="❓ Ayuda", 
                  command=self.mostrar_ayuda_programacion).pack(side=tk.RIGHT)

        # Frame para estadísticas
        frame_stats = ttk.Frame(main_frame)
        frame_stats.pack(fill=tk.X, pady=(0, 10))
        
        self.label_estadisticas = ttk.Label(frame_stats, 
                                           text="", 
                                           font=('Segoe UI', 10, 'bold'),
                                           foreground="blue")
        self.label_estadisticas.pack()
        
        # Frame para la tabla
        frame_tabla = ttk.Frame(main_frame)
        frame_tabla.pack(fill=tk.BOTH, expand=True)
        
        # Crear tabla con scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
        scrollbar_h = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        
        self.tree_programacion = ttk.Treeview(frame_tabla,
                                            columns=("documento", "profesor", "materia", "aula", "dia", "horario", "estudiantes", "grupo"),
                                            show="headings",
                                            yscrollcommand=scrollbar_v.set,
                                            xscrollcommand=scrollbar_h.set)
        
        scrollbar_v.config(command=self.tree_programacion.yview)
        scrollbar_h.config(command=self.tree_programacion.xview)
        
        # Configurar columnas
        columnas_programacion = {
            "documento": ("Documento", 100),
            "profesor": ("Profesor", 200),
            "materia": ("Materia", 250),
            "aula": ("Aula", 80),
            "dia": ("Día", 100),
            "horario": ("Horario", 120),
            "estudiantes": ("Estudiantes", 80),
            "grupo": ("Grupo", 80)
        }
        
        for col, (texto, ancho) in columnas_programacion.items():
            self.tree_programacion.heading(col, text=texto, 
                                          command=lambda c=col: self.ordenar_programacion(c))
            self.tree_programacion.column(col, width=ancho, minwidth=50)
        
        # Posicionar elementos
        self.tree_programacion.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Botones de acción
        frame_acciones = ttk.Frame(main_frame)
        frame_acciones.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(frame_acciones, text="Exportar Vista Actual", 
                  command=self.exportar_programacion_filtrada).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_acciones, text="Actualizar", 
                  command=self.actualizar_programacion_completa).pack(side=tk.LEFT)
        
        # Cargar datos iniciales
        self.programacion_filtrada = self.programacion.copy()
        self.actualizar_tabla_programacion()
        
        # Guardar referencia a la ventana
        self.ventana_programacion = ventana

    def filtrar_por_dia(self, event=None):
        """Filtra la programación por día seleccionado"""
        dia_seleccionado = self.combo_dia.get()
        aula_seleccionada = self.combo_aula.get()
        
        # Aplicar filtros
        datos_filtrados = self.programacion.copy()
        
        if dia_seleccionado != "TODOS":
            datos_filtrados = datos_filtrados[datos_filtrados['dia'] == dia_seleccionado]
        
        if aula_seleccionada != "TODAS":
            datos_filtrados = datos_filtrados[datos_filtrados['aula'] == aula_seleccionada]
        
        self.programacion_filtrada = datos_filtrados
        self.actualizar_tabla_programacion()

    def filtrar_por_aula(self, event=None):
        """Filtra la programación por aula seleccionada"""
        self.filtrar_por_dia()  # Reutilizar la lógica de filtrado

    def limpiar_filtros_programacion(self):
        """Limpia todos los filtros y muestra toda la programación"""
        self.combo_dia.set("TODOS")
        self.combo_aula.set("TODAS")
        self.programacion_filtrada = self.programacion.copy()
        self.actualizar_tabla_programacion()

    def actualizar_tabla_programacion(self):
        """Actualiza la tabla de programación con los datos filtrados"""
        # Limpiar tabla
        for item in self.tree_programacion.get_children():
            self.tree_programacion.delete(item)
        
        if self.programacion_filtrada.empty:
            self.label_estadisticas.config(text="No hay clases que coincidan con los filtros seleccionados")
            return
        
        # Agregar datos a la tabla
        for _, fila in self.programacion_filtrada.iterrows():
            self.tree_programacion.insert('', 'end', values=(
                fila['nroidenti'],
                fila['profesor'],
                fila['materia'],
                fila['aula'],
                fila['dia'],
                fila['horario'],
                fila.get('nro_estudiantes', ''),
                fila.get('grupo', '')
            ))
        
        # Actualizar estadísticas
        total_clases = len(self.programacion_filtrada)
        total_profesores = self.programacion_filtrada['profesor'].nunique()
        total_aulas = self.programacion_filtrada['aula'].nunique()
        
        estadisticas = f"Total: {total_clases} clases | {total_profesores} profesores | {total_aulas} aulas"
        
        dia_actual = self.combo_dia.get()
        aula_actual = self.combo_aula.get()
        
        if dia_actual != "TODOS" or aula_actual != "TODAS":
            filtros_activos = []
            if dia_actual != "TODOS":
                filtros_activos.append(f"Día: {dia_actual}")
            if aula_actual != "TODAS":
                filtros_activos.append(f"Aula: {aula_actual}")
            estadisticas += f" | Filtros: {', '.join(filtros_activos)}"
        
        self.label_estadisticas.config(text=estadisticas)

    def actualizar_programacion_completa(self):
        """Actualiza los datos de la programación completa"""
        if hasattr(self, 'ventana_programacion') and self.ventana_programacion.winfo_exists():
            # Actualizar combos con nuevos valores si los hay
            dias_disponibles = ["TODOS"] + sorted(self.programacion['dia'].unique().tolist())
            self.combo_dia['values'] = dias_disponibles
            
            aulas_disponibles = ["TODAS"] + sorted(self.programacion['aula'].unique().tolist())
            self.combo_aula['values'] = aulas_disponibles
            
            # Aplicar filtros actuales
            self.filtrar_por_dia()

    def exportar_programacion_filtrada(self):
        """Exporta la programación filtrada actual a Excel"""
        try:
            archivo_salida = filedialog.asksaveasfilename(
                title="Exportar programación filtrada",
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            
            if archivo_salida:
                # Preparar datos para exportar
                datos_exportar = self.programacion_filtrada.copy()
                
                # Agregar información del filtro
                dia_filtro = self.combo_dia.get()
                aula_filtro = self.combo_aula.get()
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Crear un DataFrame con información del reporte
                info_reporte = pd.DataFrame({
                    'Campo': ['Fecha de exportación', 'Total de clases', 'Filtro por día', 'Filtro por aula'],
                    'Valor': [timestamp, len(datos_exportar), dia_filtro, aula_filtro]
                })
                
                # Exportar a Excel con múltiples hojas
                with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
                    datos_exportar.to_excel(writer, sheet_name='Programación', index=False)
                    info_reporte.to_excel(writer, sheet_name='Información del Reporte', index=False)
                
                messagebox.showinfo("Éxito", 
                    f"Programación exportada exitosamente:\n{archivo_salida}\n\n"
                    f"Registros exportados: {len(datos_exportar)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

    def mostrar_ayuda_programacion(self):
        """Muestra ayuda sobre la funcionalidad de programación completa"""
        ayuda_texto = """
AYUDA - PROGRAMACIÓN ACADÉMICA COMPLETA

🔍 FILTROS DISPONIBLES:
• Filtrar por día: Seleccione un día específico o "TODOS"
• Filtrar por aula: Seleccione un aula específica o "TODAS"
• Los filtros se pueden combinar para mayor precisión

📊 ESTADÍSTICAS:
• Total de clases mostradas
• Número de profesores únicos
• Número de aulas utilizadas
• Filtros activos actuales

⚡ FUNCIONES RÁPIDAS:
• Doble clic en combo para seleccionar rápido
• "Limpiar Filtros" restaura vista completa
• "Actualizar" recarga los datos
• "Exportar Vista Actual" guarda los datos filtrados

💡 CONSEJOS:
• Use filtro por día para ver carga diaria
• Use filtro por aula para gestión de espacios
• Combine filtros para análisis específicos
• Exporte vistas para reportes

🔄 ACTUALIZACIÓN:
Los datos se actualizan automáticamente cuando 
se cargan nuevas programaciones en la ventana principal.
        """
        
        messagebox.showinfo("Ayuda - Programación Completa", ayuda_texto)

    def ordenar_programacion(self, columna):
        """Ordena la tabla de programación por la columna seleccionada"""
        try:
            # Mapear nombres de columnas de la tabla a nombres del DataFrame
            mapeo_columnas = {
                "documento": "nroidenti",
                "profesor": "profesor",
                "materia": "materia",
                "aula": "aula",
                "dia": "dia",
                "horario": "horario",
                "estudiantes": "nro_estudiantes",
                "grupo": "grupo"
            }
            
            columna_df = mapeo_columnas.get(columna)
            if not columna_df or columna_df not in self.programacion_filtrada.columns:
                return
            
            # Alternar entre ascendente y descendente
            if not hasattr(self, 'orden_columna') or self.orden_columna != columna:
                self.orden_ascendente = True
                self.orden_columna = columna
            else:
                self.orden_ascendente = not self.orden_ascendente
            
            # Ordenar datos
            self.programacion_filtrada = self.programacion_filtrada.sort_values(
                by=columna_df, 
                ascending=self.orden_ascendente,
                na_position='last'
            ).reset_index(drop=True)
            
            # Actualizar tabla
            self.actualizar_tabla_programacion()
            
            # Actualizar encabezado para mostrar dirección del ordenamiento
            direccion = "↑" if self.orden_ascendente else "↓"
            for col in ["documento", "profesor", "materia", "aula", "dia", "horario", "estudiantes", "grupo"]:
                texto_base = {
                    "documento": "Documento",
                    "profesor": "Profesor", 
                    "materia": "Materia",
                    "aula": "Aula",
                    "dia": "Día",
                    "horario": "Horario",
                    "estudiantes": "Estudiantes",
                    "grupo": "Grupo"
                }[col]
                
                if col == columna:
                    self.tree_programacion.heading(col, text=f"{texto_base} {direccion}")
                else:
                    self.tree_programacion.heading(col, text=texto_base)
                    
        except Exception as e:
            print(f"Error al ordenar: {e}")

    def devolver_desde_prestadas(self, event):
        """Permite devolver una llave directamente desde la tabla de prestadas"""
        seleccion = self.tree_prestadas.selection()
        if not seleccion:
            return
        
        valores = self.tree_prestadas.item(seleccion[0])['values']
        if len(valores) < 3:
            return
        
        # Orden correcto: Profesor(0), Documento(1), Aula(2), Fecha(3), Hora(4)
        profesor = valores[0]
        documento = valores[1]
        aula = valores[2]
        
        # Confirmar devolución
        respuesta = messagebox.askyesno(
            "Confirmar Devolución",
            f"¿Devolver llave del aula {aula}?\n\n"
            f"Profesor: {profesor}\n"
            f"Documento: {documento}"
        )
        
        if respuesta:
            try:
                # Usar el nuevo sistema simplificado de devolución
                if registrar_devolucion(documento):
                    messagebox.showinfo("Éxito", f"Llave devuelta: {aula}")
                    self.actualizar_llaves_prestadas()
                    # Actualizar búsqueda si hay documento en el campo
                    if hasattr(self, 'doc_entry') and self.doc_entry.get().strip():
                        self.buscar_clases()
                else:
                    messagebox.showerror("Error", "No se pudo registrar la devolución")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar devolución:\n{str(e)}")
