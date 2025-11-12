"""
Vista de interfaz principal
Maneja solo la presentación y componentes visuales
"""
from tkinter import ttk
import tkinter as tk
from controllers import ProgramacionController
from views.entrega_view import EntregaView
from views.programacion_view import ProgramacionView
from views.historial_view import HistorialView


class MainView:
    """Vista principal de la aplicación"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Llaves")
        self.root.geometry("1200x800")
        
        # Controlador de programación compartido
        self.programacion_controller = ProgramacionController()
        
        # Cargar programación inicial
        self._cargar_programacion_inicial()
        
        # Crear interfaz
        self._crear_interfaz()
    
    def _cargar_programacion_inicial(self):
        """Carga la programación guardada al iniciar"""
        exito, df, mensaje = self.programacion_controller.cargar_programacion_inicial()
        if exito:
            print(mensaje)
    
    def _crear_interfaz(self):
        """Crea la interfaz principal con pestañas"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame, 
            text="SISTEMA DE CONTROL DE LLAVES", 
            font=('Segoe UI', 18, 'bold')
        )
        titulo.pack(pady=(0, 20))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear vistas
        self.vista_programacion = ProgramacionView(self.notebook, self.programacion_controller)
        self.vista_entrega = EntregaView(self.notebook, self.programacion_controller)
        self.vista_historial = HistorialView(self.notebook)
        
        # Evento de cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _on_tab_changed(self, event):
        """Maneja el cambio de pestaña"""
        try:
            tab_seleccionada = self.notebook.select()
            tab_text = self.notebook.tab(tab_seleccionada, "text")
            
            # Recargar historial al seleccionar esa pestaña
            if "Préstamo" in tab_text:
                self.vista_historial.actualizar_datos()
        except:
            pass
