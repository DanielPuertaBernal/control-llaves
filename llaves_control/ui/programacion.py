from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import pandas as pd
from datetime import datetime
from helpers.limpieza_programacion import limpiar_programacion, guardar_programacion_limpia

class VistaProgramacion:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_programacion = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_programacion, text="📅 Programación")
        self.crear_vista_programacion()

    def crear_vista_programacion(self):
        frame_prog = ttk.Frame(self.frame_programacion, padding="0")
        frame_prog.pack(fill='both', expand=True)
        titulo_prog = ttk.Label(frame_prog, text="GESTIÓN DE PROGRAMACIÓN ACADÉMICA", font=('Segoe UI', 16, 'bold'))
        titulo_prog.pack(pady=(0, 20))
        frame_controles = ttk.Frame(frame_prog)
        frame_controles.pack(fill='x', pady=(0, 15))
        frame_cargar = ttk.LabelFrame(frame_controles, text="CARGAR PROGRAMACIÓN", padding="10")
        frame_cargar.pack(side='left', fill='x', expand=True, padx=(0, 10))
        frame_archivo = ttk.Frame(frame_cargar)
        frame_archivo.pack(fill='x', pady=(0, 10))
        ttk.Label(frame_archivo, text="Archivo de Programación:").pack(side='left')
        btn_cargar = ttk.Button(frame_archivo, text="📁 Seleccionar Archivo", command=self.cargar_programacion)
        btn_cargar.pack(side='right')
        self.label_archivo = ttk.Label(frame_cargar, text="No hay archivo cargado", foreground="red")
        self.label_archivo.pack(anchor='w')
        frame_filtros = ttk.LabelFrame(frame_controles, text="FILTROS RÁPIDOS", padding="10")
        frame_filtros.pack(side='right', fill='x', expand=True, padx=(10, 0))
        frame_dia = ttk.Frame(frame_filtros)
        frame_dia.pack(fill='x', pady=(0, 5))
        ttk.Label(frame_dia, text="Día:").pack(side='left')
        self.combo_dia_prog = ttk.Combobox(frame_dia, values=['TODOS', 'LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO'], state="readonly", width=12)
        self.combo_dia_prog.set('TODOS')
        self.combo_dia_prog.pack(side='right')

        # Área para mostrar programación
        frame_tabla = ttk.Frame(frame_prog)
        frame_tabla.pack(fill='both', expand=True, pady=(15, 0))
        
        # Treeview para mostrar programación
        columns_prog = ('Profesor', 'Documento', 'Materia', 'Aula', 'Día', 'Horario', 'Estudiantes')
        self.tree_programacion = ttk.Treeview(frame_tabla, columns=columns_prog, show='headings')
        
        for col in columns_prog:
            self.tree_programacion.heading(col, text=col)
            self.tree_programacion.column(col, width=100)
        
        scrollbar_prog = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_programacion.yview)
        self.tree_programacion.configure(yscrollcommand=scrollbar_prog.set)
        
        self.tree_programacion.pack(side='left', fill='both', expand=True)
        scrollbar_prog.pack(side='right', fill='y')

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
                
                # Guardar en la aplicación
                self.app.programacion_original = df
                self.app.programacion = programacion_limpia
                
                self.label_archivo.config(text=f"✅ Archivo cargado: {len(programacion_limpia)} registros", 
                                        foreground="green")
                
                self.mostrar_programacion_en_vista()
                
                messagebox.showinfo("Éxito", 
                                  f"Programación cargada exitosamente\nRegistros: {len(programacion_limpia)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")

    def mostrar_programacion_en_vista(self):
        """Mostrar la programación en el Treeview"""
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

    def filtrar_programacion_rapido(self, event=None):
        """Filtrar programación por día seleccionado"""
        pass

    def limpiar_filtros_prog(self):
        """Limpiar todos los filtros"""
        self.combo_dia_prog.set('TODOS')
        self.mostrar_programacion_en_vista()

    def exportar_programacion_actual(self):
        """Exportar la programación actual"""
        if self.app.programacion is None or self.app.programacion.empty:
            messagebox.showwarning("Advertencia", "No hay programación cargada")
            return
        
        try:
            archivo_salida = filedialog.asksaveasfilename(
                title="Exportar Programación",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if archivo_salida:
                self.app.programacion.to_excel(archivo_salida, index=False)
                messagebox.showinfo("Éxito", f"Programación exportada a: {archivo_salida}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def mostrar_estadisticas_prog(self):
        """Mostrar estadísticas de la programación"""
        if self.app.programacion is None or self.app.programacion.empty:
            messagebox.showwarning("Advertencia", "No hay programación cargada")
            return
        
        df = self.app.programacion
        stats_text = f"""
ESTADÍSTICAS DE PROGRAMACIÓN

Total de registros: {len(df)}
Profesores únicos: {df['profesor'].nunique() if 'profesor' in df.columns else 0}
Aulas únicas: {df['aula'].nunique() if 'aula' in df.columns else 0}
Materias únicas: {df['materia'].nunique() if 'materia' in df.columns else 0}
        """
        
        messagebox.showinfo("Estadísticas", stats_text)
