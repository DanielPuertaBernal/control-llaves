"""
Componente de búsqueda reutilizable
Componente visual para búsqueda en tablas con debounce y diseño moderno
"""
from tkinter import ttk
import tkinter as tk


class BuscadorComponent:
    """Componente de búsqueda reutilizable para vistas con diseño uniforme"""
    
    def __init__(self, parent_frame, callback_busqueda, label_texto="Buscar:", placeholder="Escriba para buscar..."):
        """
        Inicializa el componente de búsqueda
        
        Args:
            parent_frame: Frame padre donde se colocará el buscador
            callback_busqueda: Función a llamar cuando se realice una búsqueda
            label_texto: Texto del label (por defecto "Buscar:")
            placeholder: Texto placeholder para el entry
        """
        self.parent_frame = parent_frame
        self.callback_busqueda = callback_busqueda
        self.search_job = None
        self.placeholder = placeholder
        self.has_placeholder = False
        
        # Crear componentes visuales
        self._crear_interfaz(label_texto, placeholder)
    
    @staticmethod
    def normalizar_texto(texto):
        """
        Normaliza texto para búsqueda eliminando guiones, espacios y convirtiendo a minúsculas
        Esto permite buscar M303 y encontrar M-303, o Co101 y encontrar co-101
        """
        if not texto:
            return ""
        return texto.lower().replace('-', '').replace('_', '').replace(' ', '').strip()
    
    def _crear_interfaz(self, label_texto, placeholder):
        """Crea la interfaz del buscador con diseño moderno y uniforme"""
        # Frame contenedor con fondo de tarjeta
        self.container = tk.Frame(self.parent_frame, bg="#FFFFFF", relief=tk.FLAT)
        self.container.pack(fill='x', pady=(0, 20))
        
        # Frame interno con padding
        self.frame = tk.Frame(self.container, bg="#FFFFFF")
        self.frame.pack(fill='x', padx=15, pady=12)
        
        # Label con estilo
        label = tk.Label(
            self.frame,
            text=label_texto,
            font=('Segoe UI', 10, 'bold'),
            bg="#FFFFFF",
            fg="#424242"
        )
        label.pack(side='left', padx=(0, 10))
        
        # Frame para el entry con borde
        entry_container = tk.Frame(
            self.frame,
            bg="#42A5F5",
            bd=0,
            relief=tk.FLAT
        )
        entry_container.pack(side='left', fill='x', expand=True)
        
        # Entry de búsqueda con estilo moderno
        self.entry_busqueda = tk.Entry(
            entry_container,
            font=('Segoe UI', 10),
            bg="#FFFFFF",
            fg="#263238",
            relief=tk.FLAT,
            bd=0,
            insertbackground="#1976D2"
        )
        self.entry_busqueda.pack(fill='both', expand=True, padx=2, pady=2, ipady=8, ipadx=10)
        
        # Agregar placeholder
        if placeholder:
            self._mostrar_placeholder()
            self.entry_busqueda.bind('<FocusIn>', self._on_focus_in)
            self.entry_busqueda.bind('<FocusOut>', self._on_focus_out)
        
        # Bind para búsqueda con debounce
        self.entry_busqueda.bind('<KeyRelease>', self._on_busqueda_cambio)
        
        # Icono de búsqueda
        icono_busqueda = tk.Label(
            self.frame,
            text="🔍",
            font=('Segoe UI', 12),
            bg="#FFFFFF",
            fg="#757575"
        )
        icono_busqueda.pack(side='left', padx=(10, 0))
    
    def _mostrar_placeholder(self):
        """Muestra el placeholder"""
        self.entry_busqueda.insert(0, self.placeholder)
        self.entry_busqueda.config(fg='#90A4AE')
        self.has_placeholder = True
    
    def _on_focus_in(self, event):
        """Maneja el foco en el entry (quita placeholder)"""
        if self.has_placeholder and self.entry_busqueda.get() == self.placeholder:
            self.entry_busqueda.delete(0, 'end')
            self.entry_busqueda.config(fg='#263238')
            self.has_placeholder = False
    
    def _on_focus_out(self, event):
        """Maneja la pérdida de foco (restaura placeholder si está vacío)"""
        if not self.entry_busqueda.get():
            self._mostrar_placeholder()
    
    def _on_busqueda_cambio(self, event=None):
        """Maneja cambio en búsqueda con debounce"""
        # No buscar si es solo el placeholder
        if self.has_placeholder:
            return
            
        # Cancelar búsqueda anterior si existe
        if self.search_job:
            self.parent_frame.after_cancel(self.search_job)
        
        # Programar nueva búsqueda con debounce de 300ms
        self.search_job = self.parent_frame.after(300, self._ejecutar_busqueda)
    
    def _ejecutar_busqueda(self):
        """Ejecuta la búsqueda llamando al callback"""
        if not self.has_placeholder:
            termino = self.obtener_termino()
            if self.callback_busqueda:
                self.callback_busqueda()
    
    def obtener_termino(self):
        """Obtiene el término de búsqueda limpio"""
        if self.has_placeholder:
            return ""
        return self.entry_busqueda.get().strip()
    
    def limpiar(self):
        """Limpia el campo de búsqueda"""
        self.entry_busqueda.delete(0, 'end')
        self._mostrar_placeholder()
    
    def get_frame(self):
        """Retorna el frame del componente"""
        return self.container
