"""
Vista de programación académica
Maneja solo la presentación de carga de programación
"""
from tkinter import ttk, messagebox, filedialog
import tkinter as tk


class ProgramacionView:
    """Vista para gestión de programación académica"""
    
    def __init__(self, notebook, programacion_controller):
        self.programacion_controller = programacion_controller
        
        # Frame principal
        self.frame = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame, text="Programación")
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Verificar programación guardada
        self._verificar_programacion()
    
    def _crear_interfaz(self):
        """Crea los componentes visuales"""
        # Frame principal
        main_frame = ttk.Frame(self.frame, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame,
            text="GESTIÓN DE PROGRAMACIÓN ACADÉMICA",
            font=('Segoe UI', 18, 'bold')
        )
        titulo.pack(pady=(0, 25))
        
        # Frame para cargar programación
        frame_cargar = ttk.LabelFrame(main_frame, text="📁 CARGAR PROGRAMACIÓN", padding="15")
        frame_cargar.pack(fill='x', pady=(0, 15))
        
        ttk.Label(
            frame_cargar,
            text="Seleccione el archivo de programación académica:",
            font=('Segoe UI', 10)
        ).pack(anchor='w', pady=(0, 8))
        
        btn_cargar = ttk.Button(
            frame_cargar,
            text="📁 Seleccionar Archivo Excel/CSV",
            command=self._cargar_programacion
        )
        btn_cargar.pack(pady=(0, 10))
        
        # Label de estado
        self.label_archivo = ttk.Label(
            frame_cargar,
            text="❌ No hay archivo cargado",
            foreground="#d32f2f",
            font=('Segoe UI', 10, 'bold')
        )
        self.label_archivo.pack(anchor='w')
    
    def _verificar_programacion(self):
        """Verifica si hay programación guardada"""
        exito, df, mensaje = self.programacion_controller.cargar_programacion_inicial()
        
        if exito:
            self.label_archivo.config(text=mensaje, foreground="#2e7d32")
        else:
            self.label_archivo.config(text=mensaje, foreground="#d32f2f")
    
    def _cargar_programacion(self):
        """Carga un nuevo archivo de programación"""
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de programación",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not ruta_archivo:
            return
        
        # Procesar archivo
        exito, df, mensaje = self.programacion_controller.cargar_desde_archivo(ruta_archivo)
        
        if exito:
            self.label_archivo.config(text=mensaje, foreground="#2e7d32")
            messagebox.showinfo("Éxito", mensaje)
        else:
            self.label_archivo.config(text=mensaje, foreground="#d32f2f")
            messagebox.showerror("Error", mensaje)
