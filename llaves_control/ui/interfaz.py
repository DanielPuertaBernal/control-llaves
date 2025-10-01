from tkinter import ttk
import tkinter as tk
import pandas as pd
import os
from helpers.gestionExcel import InicializarRegistro
from assets.estiloTkinter import aplicar_estilo
from .entregaDevolucion import VistaEntregaDevolucion
from .programacion import VistaProgramacion
from ui.programacion import VistaProgramacion
from ui.entregaDevolucion import VistaEntregaDevolucion
from ui.historialLlaves import VistaHistorialLlaves

# Obtener la ruta del directorio llaves_control
def ObtenerRutaData():
    """Obtiene la ruta correcta del directorio data dentro de llaves_control"""
    ruta_actual = os.path.dirname(os.path.abspath(__file__))  # ui
    ruta_llaves_control = os.path.dirname(ruta_actual)  # llaves_control
    return os.path.join(ruta_llaves_control, "data")

def ObtenerRutaArchivo(nombre_archivo):
    """Obtiene la ruta completa de un archivo en el directorio data"""
    return os.path.join(ObtenerRutaData(), nombre_archivo)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Llaves - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.programacion = None
        self.programacion_original = None
        
        InicializarRegistro()
        aplicar_estilo(root)
        
        # Cargar programación antes de crear la interfaz
        self.CargarProgramacionInicial()
        
        self.CrearInterfazPrincipal()
    
    def CargarProgramacionInicial(self):
        """Cargar la programación desde el archivo guardado"""
        ruta_programacion = ObtenerRutaArchivo("programacion_limpia_actual.xlsx")
        
        if os.path.exists(ruta_programacion):
            try:
                df = pd.read_excel(ruta_programacion)
                self.programacion = df
            except Exception as e:
                pass  # Error silencioso, la aplicación continuará funcionando

    def CrearInterfazPrincipal(self):
        """Crea la interfaz principal con pestañas"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(main_frame, text="SISTEMA DE CONTROL DE LLAVES", 
                          font=('Segoe UI', 18, 'bold'))
        titulo.pack(pady=(0, 20))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Instanciar las vistas modulares - PROGRAMACIÓN PRIMERO para cargar datos
        self.vista_programacion = VistaProgramacion(self.notebook, self)
        self.vista_entrega = VistaEntregaDevolucion(self.notebook, self)
        self.vista_historial = VistaHistorialLlaves(self.notebook, self)
        
        # Agregar evento para actualizar vista al cambiar de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.OnTabChanged)
        
        # Notificar que los datos están listos después de crear ambas vistas
        if self.programacion is not None and not self.programacion.empty:
            self.vista_entrega.cargar_clases_del_dia()

    def OnTabChanged(self, event):
        """Evento que se ejecuta cuando se cambia de pestaña"""
        try:
            # Obtener la pestaña seleccionada
            tab_seleccionada = self.notebook.select()
            tab_text = self.notebook.tab(tab_seleccionada, "text")
            
            # Si se selecciona la pestaña del historial, actualizar los datos
            if "Préstamo" in tab_text and hasattr(self, 'vista_historial'):
                self.vista_historial.cargar_historial()
                
        except Exception:
            pass  # Error silencioso
