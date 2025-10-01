from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import pandas as pd
from datetime import datetime
import os
from helpers.limpiezaProgramacion import (
    LimpiarProgramacion, 
    GuardarProgramacionLimpia, 
    VerificarProgramacionGuardada, 
    GuardarProgramacionActual
)

# Obtener la ruta del directorio llaves_control
def ObtenerRutaData():
    """Obtiene la ruta correcta del directorio data dentro de llaves_control"""
    ruta_actual = os.path.dirname(os.path.abspath(__file__))  # ui
    ruta_llaves_control = os.path.dirname(ruta_actual)  # llaves_control
    return os.path.join(ruta_llaves_control, "data")

def ObtenerRutaArchivo(nombre_archivo):
    """Obtiene la ruta completa de un archivo en el directorio data"""
    return os.path.join(ObtenerRutaData(), nombre_archivo)

class VistaProgramacion:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_programacion = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_programacion, text="📅 Programación")
        
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
        ruta_programacion = ObtenerRutaArchivo("programacionLimpiaActual.xlsx")
        
        if os.path.exists(ruta_programacion):
            try:
                df = pd.read_excel(ruta_programacion)
                
                self.app.programacion = df
                self.datos_completos = df.copy()
                self.datos_filtrados = df.copy()
                
                self.label_archivo.config(
                    text=f"✅ Programación cargada automáticamente: {len(df)} registros procesados", 
                    foreground="#2e7d32", font=('Segoe UI', 10, 'bold')
                )
                
                self.MostrarProgramacionEnVista()
                
                # Notificar a otras vistas que los datos están listos
                self.NotificarDatosCargados()
                
            except Exception as e:
                # Error silencioso, mantener funcionamiento
                pass
    
    def NotificarDatosCargados(self):
        """Notificar a otras vistas que los datos están cargados"""
        # Verificar si vista_entrega existe y tiene el método
        if hasattr(self.app, 'vista_entrega') and hasattr(self.app.vista_entrega, 'CargarClasesDelDia'):
            self.app.vista_entrega.CargarClasesDelDia()

    # ============ FUNCIONES VISTA PROGRAMACIÓN ============
    def CargarProgramacion(self):
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
                programacion_limpia = LimpiarProgramacion(df)
                
                # Guardar automáticamente la programación limpia
                ruta_guardado = ObtenerRutaArchivo("programacionLimpiaActual.xlsx")
                os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
                programacion_limpia.to_excel(ruta_guardado, index=False)
                
                # Guardar en la aplicación
                self.app.programacion_original = df
                self.app.programacion = programacion_limpia
                
                self.label_archivo.config(
                    text=f"✅ Archivo procesado exitosamente: {len(programacion_limpia)} registros listos", 
                    foreground="#2e7d32", font=('Segoe UI', 10, 'bold')
                )
                
                self.MostrarProgramacionEnVista()
                
                messagebox.showinfo("✅ Carga Exitosa", 
                                  f"📊 Programación cargada y limpia guardada automáticamente\n\n" +
                                  f"🔢 Total de registros procesados: {len(programacion_limpia)}\n" +
                                  f"📁 Guardada en: programacionLimpiaActual.xlsx")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")

    def MostrarProgramacionEnVista(self):
        """Función simplificada - ya no necesita procesar datos para mostrar"""
        pass

    def ExportarProgramacionLimpia(self):
        """Exportar la programación limpia actual"""
        if self.app.programacion is None or self.app.programacion.empty:
            messagebox.showwarning("⚠️ Sin Datos", "No hay programación cargada para exportar\n\nPor favor, cargue primero un archivo de programación.")
            return
        
        try:
            # Permitir al usuario elegir dónde guardar
            archivo_salida = filedialog.asksaveasfilename(
                title="💾 Exportar Programación Limpia - Seleccione ubicación",
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                initialfile=f"programacionLimpia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if archivo_salida:
                # Exportar toda la programación cargada
                total_registros = len(self.app.programacion)
                self.app.programacion.to_excel(archivo_salida, index=False)
                
                messagebox.showinfo("✅ Exportación Exitosa", 
                                   f"📊 Programación exportada correctamente\n\n" +
                                   f"📁 Archivo: {os.path.basename(archivo_salida)}\n" +
                                   f"📍 Ubicación: {os.path.dirname(archivo_salida)}\n" +
                                   f"🔢 Registros exportados: {total_registros}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def MostrarDetalleFila(self, event):
        """Función eliminada - ya no hay tabla para hacer clic"""
        pass


