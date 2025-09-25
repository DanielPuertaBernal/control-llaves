from tkinter import ttk
import tkinter as tk
import pandas as pd
import os
from helpers.gestion_excel import inicializar_registro
from assets.estilo_tkinter import aplicar_estilo
from .entrega_devolucion import VistaEntregaDevolucion
from .programacion import VistaProgramacion
from ui.programacion import VistaProgramacion
from ui.entrega_devolucion import VistaEntregaDevolucion
from ui.historial_llaves import VistaHistorialLlaves

# Obtener la ruta del directorio llaves_control
def obtener_ruta_data():
    """Obtiene la ruta correcta del directorio data dentro de llaves_control"""
    ruta_actual = os.path.dirname(os.path.abspath(__file__))  # ui
    ruta_llaves_control = os.path.dirname(ruta_actual)  # llaves_control
    return os.path.join(ruta_llaves_control, "data")

def obtener_ruta_archivo(nombre_archivo):
    """Obtiene la ruta completa de un archivo en el directorio data"""
    return os.path.join(obtener_ruta_data(), nombre_archivo)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Llaves - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.programacion = None
        self.programacion_original = None
        
        inicializar_registro()
        aplicar_estilo(root)
        
        # Cargar programación antes de crear la interfaz
        self.cargar_programacion_inicial()
        
        self.crear_interfaz_principal()
    
    def cargar_programacion_inicial(self):
        """Cargar la programación desde el archivo guardado"""
        ruta_programacion = obtener_ruta_archivo("programacion_limpia_actual.xlsx")
        
        if os.path.exists(ruta_programacion):
            try:
                df = pd.read_excel(ruta_programacion)
                self.programacion = df
            except Exception as e:
                pass  # Error silencioso, la aplicación continuará funcionando

    def crear_interfaz_principal(self):
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
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Notificar que los datos están listos después de crear ambas vistas
        if self.programacion is not None and not self.programacion.empty:
            self.vista_entrega.cargar_clases_del_dia()

    def on_tab_changed(self, event):
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
