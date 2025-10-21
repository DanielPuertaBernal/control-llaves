from tkinter import ttk, messagebox, filedialog
from helpers.gestorProgramacion import GestorProgramacion

class VistaProgramacion:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_programacion = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_programacion, text="Programación")
        
        # Instanciar gestor de lógica de negocio
        self.gestor = GestorProgramacion()
        
        self.CrearVistaProgramacion()
        self.VerificarProgramacionGuardada()

    def CrearVistaProgramacion(self):
        # Frame principal con padding mejorado
        main_frame = ttk.Frame(self.frame_programacion, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # Título centrado con mejor estilo
        titulo_prog = ttk.Label(main_frame, text="GESTIÓN DE PROGRAMACIÓN ACADÉMICA", 
                               font=('Segoe UI', 18, 'bold'))
        titulo_prog.pack(pady=(0, 25))
        
        # Contenedor central para mejor organización
        contenedor_principal = ttk.Frame(main_frame)
        contenedor_principal.pack(fill='both', expand=True)
        
        # Frame superior reorganizado con mejor distribución
        frame_controles = ttk.Frame(contenedor_principal)
        frame_controles.pack(fill='x', pady=(0, 20))
        
        # Frame para cargar programación - más ancho y mejor diseño
        frame_cargar = ttk.LabelFrame(frame_controles, text="📁 CARGAR PROGRAMACIÓN", 
                                    padding="15", style="Card.TLabelframe")
        frame_cargar.pack(fill='x', pady=(0, 15))
        
        # Área de selección de archivo con mejor layout
        area_archivo = ttk.Frame(frame_cargar)
        area_archivo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(area_archivo, text="Seleccione el archivo de programación académica:", 
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 8))
        
        btn_cargar = ttk.Button(area_archivo, text="📁 Seleccionar Archivo Excel/CSV", 
                               command=self.CargarProgramacion,
                               style="Accent.TButton")
        btn_cargar.pack(pady=(0, 10))
        
        # Indicador de estado más visible
        self.label_archivo = ttk.Label(frame_cargar, text="❌ No hay archivo cargado", 
                                      foreground="#d32f2f", font=('Segoe UI', 10, 'bold'))
        self.label_archivo.pack(anchor='w')
        
        # Frame para acciones - diseño mejorado
        frame_acciones = ttk.LabelFrame(contenedor_principal, text="⚡ ACCIONES DISPONIBLES", 
                                      padding="15", style="Card.TLabelframe")
        frame_acciones.pack(fill='x', pady=(0, 15))
        
        # Descripción de la acción
        ttk.Label(frame_acciones, text="Exportar la programación procesada:", 
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 8))
        
        btn_exportar = ttk.Button(frame_acciones, text="💾 Exportar Programación Limpia", 
                                 command=self.ExportarProgramacionLimpia,
                                 style="Success.TButton")
        btn_exportar.pack(pady=(0, 5))

    def VerificarProgramacionGuardada(self):
        """Verificar si existe una programación limpia guardada y cargarla automáticamente"""
        existe, datos, mensaje = self.gestor.VerificarProgramacionExistente()
        
        if existe:
            # Actualizar aplicación con datos cargados
            self.app.programacion = datos
            
            # Actualizar interfaz
            self.label_archivo.config(
                text=mensaje, 
                foreground="#2e7d32", 
                font=('Segoe UI', 10, 'bold')
            )
            
            # Notificar a otras vistas que los datos están listos
            self.NotificarDatosCargados()
        else:
            self.label_archivo.config(
                text=mensaje, 
                foreground="#d32f2f", 
                font=('Segoe UI', 10, 'bold')
            )
    
    def NotificarDatosCargados(self):
        """Notificar a otras vistas que los datos están cargados"""
        # Verificar si vista_entrega existe y tiene el método
        if hasattr(self.app, 'vista_entrega') and hasattr(self.app.vista_entrega, 'CargarClasesDelDia'):
            self.app.vista_entrega.CargarClasesDelDia()

    def CargarProgramacion(self):
        """Cargar archivo de programación"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de programación",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if archivo:
            # Usar gestor para procesar archivo
            exito, datos_procesados, mensaje = self.gestor.CargarYProcesarArchivo(archivo)
            
            if exito:
                # Actualizar aplicación con datos procesados
                self.app.programacion_original = self.gestor.programacion_original
                self.app.programacion = datos_procesados
                
                # Actualizar interfaz
                self.label_archivo.config(
                    text=mensaje, 
                    foreground="#2e7d32", 
                    font=('Segoe UI', 10, 'bold')
                )
                
                # Notificar éxito
                messagebox.showinfo("✅ Carga Exitosa", 
                                  f"📊 Programación cargada y limpia guardada automáticamente\n\n" +
                                  f"🔢 Total de registros procesados: {len(datos_procesados)}\n" +
                                  f"📁 Guardada en: programacionLimpiaActual.xlsx")
                
                # Notificar a otras vistas
                self.NotificarDatosCargados()
                
            else:
                # Mostrar error
                messagebox.showerror("Error", mensaje)

    def ExportarProgramacionLimpia(self):
        """Exportar la programación limpia actual"""
        if self.gestor.ObtenerProgramacionActual() is None:
            messagebox.showwarning("⚠️ Sin Datos", 
                                 "No hay programación cargada para exportar\n\n"
                                 "Por favor, cargue primero un archivo de programación.")
            return
        
        try:
            # Permitir al usuario elegir dónde guardar
            nombre_sugerido = self.gestor.GenerarNombreArchivoExportacion()
            
            archivo_salida = filedialog.asksaveasfilename(
                title="💾 Exportar Programación Limpia - Seleccione ubicación",
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                initialfile=nombre_sugerido
            )
            
            if archivo_salida:
                # Usar gestor para exportar
                exito, mensaje = self.gestor.ExportarProgramacion(archivo_salida)
                
                if exito:
                    messagebox.showinfo("✅ Exportación Exitosa", mensaje)
                else:
                    messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado al exportar: {str(e)}")