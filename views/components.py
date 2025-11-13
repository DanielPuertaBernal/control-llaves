"""
Componente de búsqueda reutilizable
Componente visual para búsqueda en tablas con debounce
"""
from tkinter import ttk


class BuscadorComponent:
    """Componente de búsqueda reutilizable para vistas"""
    
    def __init__(self, parent_frame, callback_busqueda, label_texto="Buscar:", placeholder=""):
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
        """Crea la interfaz del buscador"""
        # Frame contenedor
        self.frame = ttk.Frame(self.parent_frame)
        self.frame.pack(fill='x', pady=(0, 20))
        
        # Label
        ttk.Label(self.frame, text=label_texto).pack(side='left', padx=(0, 5))
        
        # Entry de búsqueda
        self.entry_busqueda = ttk.Entry(self.frame, width=40)
        self.entry_busqueda.pack(side='left', padx=(0, 10))
        
        if placeholder:
            self.entry_busqueda.insert(0, placeholder)
            self.entry_busqueda.config(foreground='gray')
            self.entry_busqueda.bind('<FocusIn>', self._on_focus_in)
            self.entry_busqueda.bind('<FocusOut>', self._on_focus_out)
        
        # Bind para búsqueda con debounce
        self.entry_busqueda.bind('<KeyRelease>', self._on_busqueda_cambio)
    
    def _on_focus_in(self, event):
        """Maneja el foco en el entry (quita placeholder)"""
        if self.entry_busqueda.get() == self.placeholder:
            self.entry_busqueda.delete(0, 'end')
            self.entry_busqueda.config(foreground='black')
    
    def _on_focus_out(self, event):
        """Maneja la pérdida de foco (restaura placeholder si está vacío)"""
        if not self.entry_busqueda.get():
            self.entry_busqueda.insert(0, self.placeholder)
            self.entry_busqueda.config(foreground='gray')
    
    def _on_busqueda_cambio(self, event=None):
        """Maneja cambio en búsqueda con debounce"""
        # Cancelar búsqueda anterior si existe
        if self.search_job:
            self.parent_frame.after_cancel(self.search_job)
        
        # Programar nueva búsqueda con debounce de 300ms
        self.search_job = self.parent_frame.after(300, self._ejecutar_busqueda)
    
    def _ejecutar_busqueda(self):
        """Ejecuta la búsqueda llamando al callback"""
        termino = self.obtener_termino()
        if self.callback_busqueda:
            self.callback_busqueda(termino)
    
    def obtener_termino(self):
        """Obtiene el término de búsqueda limpio"""
        return self.entry_busqueda.get().strip()
    
    def limpiar(self):
        """Limpia el campo de búsqueda"""
        self.entry_busqueda.delete(0, 'end')
    
    def get_frame(self):
        """Retorna el frame del componente"""
        return self.frame
