import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from helpers.limpieza_programacion import limpiar_programacion, guardar_programacion_limpia
from helpers.gestion_excel import (registrar_entrega, registrar_devolucion, filtrar_llaves, 
                                 inicializar_registro, verificar_llave_entregada, obtener_llaves_pendientes)
from assets.estilo_tkinter import aplicar_estilo

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Llaves - Sistema de Gestión")
        self.root.geometry("1000x700")
        self.programacion = None
        self.programacion_original = None
        
        inicializar_registro()
        aplicar_estilo(root)
        self.crear_interfaz()

    def crear_interfaz(self):
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
        frame_tabla.pack(fill=tk.BOTH, expand=True)

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

        # Frame de información
        self.info_label = ttk.Label(main_frame, text="Sistema listo. Cargue una programación para comenzar.", 
                                   foreground="blue")
        self.info_label.pack(pady=10)

    def cargar_programacion(self):
        file = filedialog.askopenfilename(
            title="Seleccionar archivo de programación",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if file:
            try:
                df = pd.read_excel(file)
                self.programacion_original = df.copy()
                self.programacion = limpiar_programacion(df)
                self.info_label.config(
                    text=f"Programación cargada: {len(self.programacion)} clases consolidadas de {len(df)} registros originales",
                    foreground="green"
                )
                messagebox.showinfo("Éxito", 
                    f"Programación cargada exitosamente.\n"
                    f"Registros originales: {len(df)}\n"
                    f"Clases consolidadas: {len(self.programacion)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")
                self.info_label.config(text="Error al cargar programación", foreground="red")

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
                (self.programacion['nroidenti'] == doc) & 
                (self.programacion['dia'] == dia_espanol)
            ]
            
            self.mostrar_clases(clases, f"Clases de hoy ({dia_espanol}) para documento: {doc}")
            
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
            clases = self.programacion[self.programacion['nroidenti'] == doc]
            self.mostrar_clases(clases, f"Todas las clases para documento: {doc}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clases:\n{str(e)}")

    def mostrar_clases(self, clases, titulo):
        self.tree.delete(*self.tree.get_children())
        
        if clases.empty:
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
            info_clase = {
                'nroidenti': doc,
                'profesor': valores[0],
                'materia': valores[1],
                'aula': valores[2],
                'horario': valores[3],
                'dia': valores[4],
                'nro_estudiantes': valores[5]
            }
            
            if registrar_entrega(info_clase):
                messagebox.showinfo("Éxito", f"Llave entregada para {valores[1]} en aula {valores[2]}")
                # Actualizar la vista
                if hasattr(self, 'buscar_clases'):
                    self.buscar_clases()
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
            
            if registrar_devolucion(doc, valores[1], valores[2]):
                messagebox.showinfo("Éxito", f"Llave devuelta para {valores[1]} en aula {valores[2]}")
                # Actualizar la vista
                if hasattr(self, 'buscar_clases'):
                    self.buscar_clases()
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
            historial = filtrar_llaves()
            
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
