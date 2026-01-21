"""
Vista de programación académica
Maneja solo la presentación de carga de programación
"""
from tkinter import ttk, messagebox, filedialog
import tkinter as tk


class ProgramacionView:
    """Vista para gestión de programación académica"""
    
    def __init__(self, parent_frame, programacion_controller):
        self.programacion_controller = programacion_controller
        
        # Frame principal - ahora recibe el parent directamente
        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Verificar programación guardada
        self._verificar_programacion()
    
    def _crear_interfaz(self):
        """Crea los componentes visuales"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.frame, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # Título eliminado (ahora está en el header principal)
        
        # Frame para cargar programación - Diseño de tarjeta moderna
        frame_cargar = ttk.LabelFrame(main_frame, text="📁 CARGAR PROGRAMACIÓN", padding="20")
        frame_cargar.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            frame_cargar,
            text="Seleccione el archivo de programación académica:",
            font=('Segoe UI', 10)
        ).pack(anchor='w', pady=(0, 12))
        
        btn_cargar = ttk.Button(
            frame_cargar,
            text="📁 Seleccionar Archivo Excel/CSV",
            command=self._cargar_programacion
        )
        btn_cargar.pack(pady=(0, 12))
        
        # Label de estado
        self.label_archivo = ttk.Label(
            frame_cargar,
            text="❌ No hay archivo cargado",
            foreground="#d32f2f",
            font=('Segoe UI', 10, 'bold')
        )
        self.label_archivo.pack(anchor='w')
        
        # Frame para exportar programación limpia
        frame_exportar = ttk.LabelFrame(main_frame, text="💾 EXPORTAR PROGRAMACIÓN LIMPIA", padding="20")
        frame_exportar.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            frame_exportar,
            text="Exportar la programación limpia (solo columnas necesarias):",
            font=('Segoe UI', 10)
        ).pack(anchor='w', pady=(0, 12))
        
        btn_exportar = ttk.Button(
            frame_exportar,
            text="💾 Exportar a Excel",
            command=self._exportar_programacion
        )
        btn_exportar.pack()
    
    def _verificar_programacion(self):
        """Verifica si hay programación guardada"""
        # Si ya hay programación en memoria, no intentes recargar
        df_actual = self.programacion_controller.obtener_programacion_completa()
        if df_actual is not None and not df_actual.empty:
            self.label_archivo.config(
                text=f"✅ Programación cargada: {len(df_actual)} registros",
                foreground="#2e7d32"
            )
            return

        # Si no hay en memoria, intenta cargar la guardada
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
    
    def _exportar_programacion(self):
        """Exporta la programación limpia a un archivo Excel"""
        # Verificar si hay programación cargada
        exito, df, mensaje = self.programacion_controller.cargar_programacion_inicial()
        
        if not exito or df is None or df.empty:
            messagebox.showwarning("Advertencia", "No hay programación cargada para exportar")
            return
        
        # Seleccionar ubicación de guardado
        ruta_guardado = filedialog.asksaveasfilename(
            title="Guardar programación limpia",
            defaultextension=".xlsx",
            filetypes=[
                ("Archivo Excel", "*.xlsx"),
                ("Todos los archivos", "*.*")
            ],
            initialfile="programacion_limpia.xlsx"
        )
        
        if not ruta_guardado:
            return
        
        # Exportar programación
        exito_exportar, mensaje_exportar = self.programacion_controller.exportar_programacion(
            df, ruta_guardado
        )
        
        if exito_exportar:
            messagebox.showinfo("Éxito", mensaje_exportar)
        else:
            messagebox.showerror("Error", mensaje_exportar)
