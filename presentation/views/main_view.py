"""
Vista de interfaz principal con menú lateral moderno
Maneja solo la presentación y componentes visuales
"""
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from controllers import ProgramacionController, LlaveController
from presentation.views.entrega_view import EntregaView
from presentation.views.programacion_view import ProgramacionView
from presentation.views.historial_view import HistorialView
from presentation.views.informes_view import InformesView
from presentation.nfc_presenter import NFCPresenter
from presentation.views.nfc_view import NFCView


class MainView:
    """Vista principal de la aplicación con menú lateral"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Llaves")
        self.root.geometry("1280x820")
        self.root.minsize(1024, 600)
        
        # Inicializar variables ANTES de crear interfaz
        self.vista_actual = None
        self.botones_menu = {}
        
        # Controladores
        self.programacion_controller = ProgramacionController()
        self.llave_controller = LlaveController()
        
        # Crear interfaz primero
        self._crear_interfaz()
        
        # Presenter NFC
        self.nfc_presenter = NFCPresenter(self.root)
        
        # Establecer callback para ir a vista NFC automáticamente
        self.nfc_presenter.establecer_callback_ir_nfc(lambda: self._mostrar_vista("nfc"))
        
        # Cargar programación inicial
        self._cargar_programacion_inicial()
        
        # Mostrar vista inicial
        self._mostrar_vista("programacion")
        
        # Inicializar NFC con callback de actualización
        self.nfc_presenter.inicializar(self._actualizar_vistas_despues_operacion)
    
    def _cargar_programacion_inicial(self):
        """Carga la programación guardada al iniciar"""
        exito, df, mensaje = self.programacion_controller.cargar_programacion_inicial()
        if exito:
            print(mensaje)
    
    def _crear_interfaz(self):
        """Crea la interfaz principal con menú lateral fijo"""
        # Container principal
        container = tk.Frame(self.root, bg="#F5F7FA")
        container.pack(fill=tk.BOTH, expand=True)
        
        # ============ SIDEBAR (Panel Lateral) ============
        self.sidebar = tk.Frame(container, bg="#37474F", width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)  # Mantener ancho fijo
        
        # Avatar/Logo en la parte superior
        avatar_frame = tk.Frame(self.sidebar, bg="#37474F")
        avatar_frame.pack(pady=(30, 20))
        
        # Círculo para avatar
        avatar_canvas = tk.Canvas(avatar_frame, width=80, height=80, 
                                 bg="#37474F", highlightthickness=0)
        avatar_canvas.pack()
        
        # Dibujar círculo
        avatar_canvas.create_oval(5, 5, 75, 75, fill="#1976D2", outline="#42A5F5", width=3)
        avatar_canvas.create_text(40, 40, text="🔑", font=('Segoe UI', 32))
        
        # Nombre del sistema
        titulo_sidebar = tk.Label(
            self.sidebar,
            text="Control de\nLlaves",
            font=('Segoe UI', 14, 'bold'),
            bg="#37474F",
            fg="#FFFFFF",
            justify=tk.CENTER
        )
        titulo_sidebar.pack(pady=(5, 30))
        
        # Separador
        separador = tk.Frame(self.sidebar, bg="#64B5F6", height=2)
        separador.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Opciones del menú
        opciones_menu = [
            {"texto": "  📋 Programación", "vista": "programacion", "icono": "📋"},
            {"texto": "  📅 Programación del Día", "vista": "entrega", "icono": "📅"},
            {"texto": "  🔓 Llaves en Préstamo", "vista": "historial", "icono": "🔓"},
            {"texto": "  📊 Informes del Día", "vista": "informes", "icono": "📊"},
            {"texto": "  📡 Sistema NFC", "vista": "nfc", "icono": "📡"}
        ]
        
        # Crear botones del menú
        for opcion in opciones_menu:
            btn = self._crear_boton_menu(
                self.sidebar,
                opcion["texto"],
                lambda v=opcion["vista"]: self._mostrar_vista(v)
            )
            self.botones_menu[opcion["vista"]] = btn
        
        # Espaciador
        tk.Frame(self.sidebar, bg="#37474F").pack(fill=tk.BOTH, expand=True)
        
        # Separador inferior
        separador_inferior = tk.Frame(self.sidebar, bg="#64B5F6", height=2)
        separador_inferior.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Botón de salir
        btn_salir = tk.Button(
            self.sidebar,
            text="  🚪 Salir",
            font=('Segoe UI', 11, 'bold'),
            bg="#EF5350",
            fg="#FFFFFF",
            activebackground="#E53935",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            anchor="w",
            padx=20,
            pady=12,
            bd=0,
            command=self._salir_aplicacion
        )
        btn_salir.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Efectos hover para botón salir
        btn_salir.bind("<Enter>", lambda e: btn_salir.config(bg="#E53935"))
        btn_salir.bind("<Leave>", lambda e: btn_salir.config(bg="#EF5350"))
        
        # ============ ÁREA DE CONTENIDO PRINCIPAL ============
        self.content_area = tk.Frame(container, bg="#F5F7FA")
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Header del área de contenido
        header_frame = tk.Frame(self.content_area, bg="#F5F7FA", height=80)
        header_frame.pack(fill=tk.X, padx=25, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        self.titulo_contenido = tk.Label(
            header_frame,
            text="SISTEMA DE CONTROL DE LLAVES",
            font=('Segoe UI', 22, 'bold'),
            bg="#F5F7FA",
            fg="#263238",
            anchor="w"
        )
        self.titulo_contenido.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Contenedor principal con bordes redondeados (efecto visual)
        self.main_container = tk.Frame(
            self.content_area,
            bg="#E0E0E0",
            relief=tk.FLAT,
            bd=0
        )
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))
        
        # Agregar efecto de sombra visual (borde sutil)
        shadow_frame = tk.Frame(self.main_container, bg="#CFD8DC", height=3)
        shadow_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Frame para contenido dinámico
        self.content_frame = tk.Frame(self.main_container, bg="#E0E0E0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def _crear_boton_menu(self, parent, texto, comando):
        """Crea un botón estilizado para el menú lateral"""
        btn = tk.Button(
            parent,
            text=texto,
            font=('Segoe UI', 11),
            bg="#37474F",
            fg="#FFFFFF",
            activebackground="#455A64",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            anchor="w",
            padx=20,
            pady=15,
            bd=0,
            command=comando
        )
        btn.pack(fill=tk.X, padx=15, pady=5)
        
        # Efectos hover
        btn.bind("<Enter>", lambda e: btn.config(bg="#455A64"))
        btn.bind("<Leave>", lambda e: self._actualizar_color_boton(btn))
        
        return btn
    
    def _actualizar_color_boton(self, boton):
        """Actualiza el color del botón según si está activo"""
        for vista, btn in self.botones_menu.items():
            if btn == boton and self.vista_actual == vista:
                btn.config(bg="#1976D2")
            elif btn == boton:
                btn.config(bg="#37474F")
    
    def _mostrar_vista(self, nombre_vista):
        """Muestra la vista seleccionada"""
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Actualizar vista actual
        self.vista_actual = nombre_vista
        
        # Actualizar colores de botones
        for vista, btn in self.botones_menu.items():
            if vista == nombre_vista:
                btn.config(bg="#1976D2", font=('Segoe UI', 11, 'bold'))
            else:
                btn.config(bg="#37474F", font=('Segoe UI', 11))
        
        # Crear frame temporal para la vista
        vista_frame = ttk.Frame(self.content_frame)
        vista_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cargar vista correspondiente
        if nombre_vista == "programacion":
            self.titulo_contenido.config(text="GESTIÓN DE PROGRAMACIÓN ACADÉMICA")
            self.vista_programacion = ProgramacionView(vista_frame, self.programacion_controller)
        elif nombre_vista == "entrega":
            dia_actual = self._obtener_dia_actual()
            self.titulo_contenido.config(text=f"PROGRAMACIÓN DEL DÍA - {dia_actual}")
            self.vista_entrega = EntregaView(vista_frame, self.programacion_controller)
        elif nombre_vista == "historial":
            dia_actual = self._obtener_dia_actual()
            self.titulo_contenido.config(text=f"LLAVES EN PRÉSTAMO DEL DÍA - {dia_actual}")
            self.vista_historial = HistorialView(vista_frame)
            self.vista_historial.actualizar_datos()
        elif nombre_vista == "informes":
            dia_actual = self._obtener_dia_actual()
            self.titulo_contenido.config(text=f"INFORME DE LLAVES DEL DÍA - {dia_actual}")
            self.vista_informes = InformesView(vista_frame)
        elif nombre_vista == "nfc":
            self.titulo_contenido.config(text="MONITOREO DEL SISTEMA NFC")
            self.vista_nfc = NFCView(vista_frame, None)
            # Establecer referencia en el presenter NFC para actualizaciones en tiempo real
            self.nfc_presenter.establecer_nfc_view(self.vista_nfc)
    
    def _obtener_dia_actual(self):
        """Obtiene el día actual en español"""
        dias = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
        return dias[datetime.now().weekday()]
    
    def _salir_aplicacion(self):
        """Cierra la aplicación"""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir?"):
            # Desconectar NFC antes de cerrar
            self.nfc_presenter.desconectar()
            self.root.quit()
    
    def _actualizar_vistas_despues_operacion(self):
        """Actualiza las vistas después de una operación de entrega/devolución"""
        try:
            # Actualizar vista de entrega si está activa
            if hasattr(self, 'vista_entrega') and self.vista_actual == "entrega":
                self.vista_entrega.cargar_clases_del_dia()
            
            # Actualizar vista de historial si está activa
            if hasattr(self, 'vista_historial') and self.vista_actual == "historial":
                self.vista_historial.actualizar_datos()
            
            # Actualizar vista de informes si está activa
            if hasattr(self, 'vista_informes') and self.vista_actual == "informes":
                self.vista_informes.actualizar_datos()
        
        except Exception as e:
            print(f"Error al actualizar vistas: {e}")
