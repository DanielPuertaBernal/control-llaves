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
                  command=self.ver_todas_clases).pack(side=tk.LEFT)

        # Frame para acciones
        frame_acciones = ttk.Frame(main_frame)
        frame_acciones.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(frame_acciones, text="Entregar Llave", 
                  command=self.entregar_llave).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_acciones, text="Devolver Llave", 
                  command=self.devolver_llave).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_acciones, text="Ver Llaves Entregadas", 
                  command=self.ver_llaves_entregadas).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_acciones, text="Ver Historial", 
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
