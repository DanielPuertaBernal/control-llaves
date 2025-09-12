from tkinter import ttk
import tkinter as tk
from helpers.gestion_excel import inicializar_registro
from assets.estilo_tkinter import aplicar_estilo
from .entrega_devolucion import VistaEntregaDevolucion
from .programacion import VistaProgramacion
from .informes import VistaInformes

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Llaves - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.programacion = None
        self.programacion_original = None
        
        inicializar_registro()
        aplicar_estilo(root)
        self.crear_interfaz_principal()

    def crear_interfaz_principal(self):
        """Crea la interfaz principal con pestañas"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(main_frame, text="SISTEMA DE CONTROL DE LLAVES", 
                          font=('Segoe UI', 18, 'bold'))
        titulo.pack(pady=(0, 20))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Instanciar las vistas modulares
        self.vista_entrega = VistaEntregaDevolucion(self.notebook, self)
        self.vista_programacion = VistaProgramacion(self.notebook, self)
        self.vista_informes = VistaInformes(self.notebook, self)
