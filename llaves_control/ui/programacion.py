from tkinter import ttk, messagebox, filedialog, StringVar
import tkinter as tk
import pandas as pd
from datetime import datetime
import os
from helpers.limpieza_programacion import (
    limpiar_programacion, 
    guardar_programacion_limpia, 
    verificar_programacion_guardada, 
    guardar_programacion_actual
)

class VistaProgramacion:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_programacion = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_programacion, text="📅 Programación")
        
        # Variables para búsqueda
        self.var_busqueda = StringVar()
        self.var_busqueda.trace("w", self.buscar_en_tiempo_real)
        
        # Datos para la búsqueda
        self.datos_completos = None
        self.datos_filtrados = None
        
        self.crear_vista_programacion()
        self.verificar_programacion_guardada()

    def crear_vista_programacion(self):
        frame_prog = ttk.Frame(self.frame_programacion, padding="0")
        frame_prog.pack(fill='both', expand=True)
        
        titulo_prog = ttk.Label(frame_prog, text="GESTIÓN DE PROGRAMACIÓN ACADÉMICA", 
                               font=('Segoe UI', 16, 'bold'))
        titulo_prog.pack(pady=(0, 20))
        
        # Frame superior con controles
        frame_controles = ttk.Frame(frame_prog)
        frame_controles.pack(fill='x', pady=(0, 15))
        
        # Frame para cargar programación
        frame_cargar = ttk.LabelFrame(frame_controles, text="CARGAR PROGRAMACIÓN", padding="10")
        frame_cargar.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        frame_archivo = ttk.Frame(frame_cargar)
        frame_archivo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame_archivo, text="Archivo de Programación:").pack(side='left')
        btn_cargar = ttk.Button(frame_archivo, text="📁 Seleccionar Archivo", 
                               command=self.cargar_programacion)
        btn_cargar.pack(side='right')
        
        self.label_archivo = ttk.Label(frame_cargar, text="No hay archivo cargado", 
                                      foreground="red")
        self.label_archivo.pack(anchor='w')
        
        # Frame para acciones
        frame_acciones = ttk.LabelFrame(frame_controles, text="ACCIONES", padding="10")
        frame_acciones.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        btn_exportar = ttk.Button(frame_acciones, text="💾 Exportar Programación Limpia", 
                                 command=self.exportar_programacion_limpia)
        btn_exportar.pack(fill='x')
        
        # Frame para búsqueda
        frame_busqueda = ttk.Frame(frame_prog)
        frame_busqueda.pack(fill='x', pady=(0, 15))
        
        ttk.Label(frame_busqueda, text="🔍 Buscar:").pack(side='left', padx=(0, 10))
        entry_busqueda = ttk.Entry(frame_busqueda, textvariable=self.var_busqueda, width=50)
        entry_busqueda.pack(side='left', fill='x', expand=True)
        
        btn_limpiar = ttk.Button(frame_busqueda, text="🗑️ Limpiar", 
                                command=self.limpiar_busqueda)
        btn_limpiar.pack(side='right', padx=(10, 0))

        
        # Área para mostrar programación
        frame_tabla = ttk.Frame(frame_prog)
        frame_tabla.pack(fill='both', expand=True, pady=(15, 0))
        
        # Treeview para mostrar programación con estilo mejorado
        columns_prog = ('Profesor', 'Documento', 'Materia', 'Aula', 'Día', 'Horario', 'Estudiantes')
        self.tree_programacion = ttk.Treeview(frame_tabla, columns=columns_prog, show='headings', height=15)
        
        # Configurar columnas con anchos específicos y alineación centrada
        column_widths = {
            'Profesor': 200,
            'Documento': 120,
            'Materia': 250,
            'Aula': 100,
            'Día': 100,
            'Horario': 130,
            'Estudiantes': 90
        }
        
        for col in columns_prog:
            self.tree_programacion.heading(col, text=col, anchor='center')
            self.tree_programacion.column(col, width=column_widths[col], anchor='center', minwidth=80)
        
        # Aplicar estilo a las filas (alternando colores)
        self.tree_programacion.tag_configure('oddrow', background='#f8f9fa', foreground='#212121')
        self.tree_programacion.tag_configure('evenrow', background='#ffffff', foreground='#212121')
        
        # Configurar estilo de selección
        style = ttk.Style()
        style.configure("Treeview", selectbackground="#e3f2fd", selectforeground="#1976d2")
        
        # Scrollbars
        scrollbar_vert = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_programacion.yview)
        scrollbar_horiz = ttk.Scrollbar(frame_tabla, orient='horizontal', command=self.tree_programacion.xview)
        
        self.tree_programacion.configure(yscrollcommand=scrollbar_vert.set, xscrollcommand=scrollbar_horiz.set)
        
        # Empaquetar con grid para mejor control
        self.tree_programacion.grid(row=0, column=0, sticky='nsew')
        scrollbar_vert.grid(row=0, column=1, sticky='ns')
        scrollbar_horiz.grid(row=1, column=0, sticky='ew')
        
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

    def verificar_programacion_guardada(self):
        """Verificar si existe una programación limpia guardada y cargarla automáticamente"""
        ruta_programacion = os.path.join("llaves_control", "data", "programacion_limpia_actual.xlsx")
        
        if os.path.exists(ruta_programacion):
            try:
                df = pd.read_excel(ruta_programacion)
                self.app.programacion = df
                self.datos_completos = df.copy()
                self.datos_filtrados = df.copy()
                
                self.label_archivo.config(
                    text=f"✅ Programación limpia cargada: {len(df)} registros", 
                    foreground="green"
                )
                
                self.mostrar_programacion_en_vista()
                
            except Exception as e:
                print(f"Error al cargar programación guardada: {e}")

    def buscar_en_tiempo_real(self, *args):
        """Buscar en tiempo real mientras el usuario escribe"""
        if self.datos_completos is None:
            return
        
        termino_busqueda = self.var_busqueda.get().lower().strip()
        
        if not termino_busqueda:
            self.datos_filtrados = self.datos_completos.copy()
        else:
            # Buscar en todas las columnas de texto
            mask = pd.Series([False] * len(self.datos_completos))
            
            for columna in self.datos_completos.select_dtypes(include=['object']).columns:
                mask |= self.datos_completos[columna].astype(str).str.lower().str.contains(termino_busqueda, na=False)
            
            # También buscar en columna de documento (que puede ser numérica)
            if 'nroidenti' in self.datos_completos.columns:
                mask |= self.datos_completos['nroidenti'].astype(str).str.contains(termino_busqueda, na=False)
            
            self.datos_filtrados = self.datos_completos[mask].copy()
        
        self.mostrar_programacion_filtrada()

    def limpiar_busqueda(self):
        """Limpiar el campo de búsqueda"""
        self.var_busqueda.set("")

    def mostrar_programacion_filtrada(self):
        """Mostrar la programación filtrada en el Treeview"""
        # Limpiar tabla
        for item in self.tree_programacion.get_children():
            self.tree_programacion.delete(item)
        
        if self.datos_filtrados is not None and not self.datos_filtrados.empty:
            for index, (_, fila) in enumerate(self.datos_filtrados.iterrows()):
                documento = str(fila.get('nroidenti', '')).replace('.0', '')
                estudiantes = fila.get('nro_estudiantes', 0)
                
                # Alternar colores de filas
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                
                self.tree_programacion.insert('', 'end', values=(
                    fila.get('profesor', ''),
                    documento,
                    fila.get('materia', ''),
                    fila.get('aula', ''),
                    fila.get('dia', ''),
                    fila.get('horario', ''),
                    estudiantes
                ), tags=(tag,))

    # ============ FUNCIONES VISTA PROGRAMACIÓN ============
    def cargar_programacion(self):
        """Cargar archivo de programación"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de programación",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if archivo:
            try:
                if archivo.endswith('.csv'):
                    df = pd.read_csv(archivo, encoding='utf-8')
                else:
                    df = pd.read_excel(archivo)
                
                # Verificar que tenga las columnas básicas
                columnas_requeridas = ['nroidenti', 'profesor', 'aula']
                columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                
                if columnas_faltantes:
                    messagebox.showerror("Error", 
                                       f"El archivo debe contener las columnas: {', '.join(columnas_faltantes)}")
                    return
                
                # Limpiar y procesar programación
                programacion_limpia = limpiar_programacion(df)
                
                # Guardar automáticamente la programación limpia
                ruta_guardado = os.path.join("llaves_control", "data", "programacion_limpia_actual.xlsx")
                os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
                programacion_limpia.to_excel(ruta_guardado, index=False)
                
                # Guardar en la aplicación
                self.app.programacion_original = df
                self.app.programacion = programacion_limpia
                self.datos_completos = programacion_limpia.copy()
                self.datos_filtrados = programacion_limpia.copy()
                
                self.label_archivo.config(text=f"✅ Archivo cargado: {len(programacion_limpia)} registros", 
                                        foreground="green")
                
                self.mostrar_programacion_en_vista()
                
                messagebox.showinfo("Éxito", 
                                  f"Programación cargada y guardada exitosamente\nRegistros: {len(programacion_limpia)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")

    def mostrar_programacion_en_vista(self):
        """Mostrar la programación en el Treeview"""
        # Limpiar tabla
        for item in self.tree_programacion.get_children():
            self.tree_programacion.delete(item)
        
        if self.app.programacion is not None and not self.app.programacion.empty:
            # Actualizar datos completos para búsqueda
            self.datos_completos = self.app.programacion.copy()
            self.datos_filtrados = self.app.programacion.copy()
            
            for index, (_, fila) in enumerate(self.app.programacion.iterrows()):
                documento = str(fila.get('nroidenti', '')).replace('.0', '')
                estudiantes = fila.get('nro_estudiantes', 0)
                
                # Alternar colores de filas
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                
                self.tree_programacion.insert('', 'end', values=(
                    fila.get('profesor', ''),
                    documento,
                    fila.get('materia', ''),
                    fila.get('aula', ''),
                    fila.get('dia', ''),
                    fila.get('horario', ''),
                    estudiantes
                ), tags=(tag,))

    def exportar_programacion_limpia(self):
        """Exportar la programación limpia actual"""
        if self.app.programacion is None or self.app.programacion.empty:
            messagebox.showwarning("Advertencia", "No hay programación cargada")
            return
        
        try:
            # Permitir al usuario elegir dónde guardar
            archivo_salida = filedialog.asksaveasfilename(
                title="Exportar Programación Limpia",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfilename=f"programacion_limpia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if archivo_salida:
                # Si hay datos filtrados, exportar esos; si no, exportar todos
                datos_a_exportar = self.datos_filtrados if self.datos_filtrados is not None else self.app.programacion
                datos_a_exportar.to_excel(archivo_salida, index=False)
                messagebox.showinfo("Éxito", f"Programación limpia exportada a: {archivo_salida}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
        # Limpiar tabla
        for item in self.tree_programacion.get_children():
            self.tree_programacion.delete(item)
        
        if self.app.programacion is not None and not self.app.programacion.empty:
            for _, fila in self.app.programacion.iterrows():
                documento = str(fila.get('nroidenti', '')).replace('.0', '')
                estudiantes = fila.get('nro_estudiantes', 0)
                
                self.tree_programacion.insert('', 'end', values=(
                    fila.get('profesor', ''),
                    documento,
                    fila.get('materia', ''),
                    fila.get('aula', ''),
                    fila.get('dia', ''),
                    fila.get('horario', ''),
                    estudiantes
                ))


