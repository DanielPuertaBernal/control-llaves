"""
Vista de retroalimentación visual para entregas/devoluciones NFC
Muestra información de forma temporal y automática
"""
import tkinter as tk
from tkinter import ttk


class FeedbackView:
    """Vista de retroalimentación para operaciones NFC"""
    
    def __init__(self, parent):
        self.parent = parent
        self.ventana = None
    
    def mostrar_entrega(self, datos_docente, datos_clase, duracion=2000):
        """
        Muestra retroalimentación de entrega de llave
        
        Args:
            datos_docente (dict): Información del docente
            datos_clase (dict): Información de la clase
            duracion (int): Tiempo en milisegundos antes de autocierre
        """
        if self.ventana:
            self.ventana.destroy()
        
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("Entrega de Llave")
        
        # Configurar ventana
        self._configurar_ventana(self.ventana, "#4CAF50")  # Verde
        
        # Contenido
        frame = ttk.Frame(self.ventana, padding="30")
        frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(
            frame,
            text="✅ LLAVE ENTREGADA",
            font=('Segoe UI', 24, 'bold'),
            foreground="#2e7d32"
        ).pack(pady=(0, 20))
        
        # Información del docente
        ttk.Label(
            frame,
            text=f"👤 {datos_docente.get('Nombre', 'N/A')}",
            font=('Segoe UI', 16)
        ).pack(pady=5)
        
        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Información de la clase
        ttk.Label(
            frame,
            text=f"📚 Materia: {datos_clase.get('Materia', 'N/A')}",
            font=('Segoe UI', 14)
        ).pack(pady=5)
        
        ttk.Label(
            frame,
            text=f"🚪 Salón: {datos_clase.get('Aula', 'N/A')}",
            font=('Segoe UI', 14, 'bold'),
            foreground="#1976D2"
        ).pack(pady=5)
        
        ttk.Label(
            frame,
            text=f"🕐 Horario: {datos_clase.get('Horario', 'N/A')}",
            font=('Segoe UI', 14)
        ).pack(pady=5)
        
        # Auto-cerrar
        self.ventana.after(duracion, self._cerrar)
    
    def mostrar_devolucion(self, datos_docente, hora_devolucion, duracion=2000):
        """
        Muestra retroalimentación de devolución de llave
        
        Args:
            datos_docente (dict): Información del docente
            hora_devolucion (str): Hora de devolución
            duracion (int): Tiempo en milisegundos antes de autocierre
        """
        if self.ventana:
            self.ventana.destroy()
        
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("Devolución de Llave")
        
        # Configurar ventana
        self._configurar_ventana(self.ventana, "#2196F3")  # Azul
        
        # Contenido
        frame = ttk.Frame(self.ventana, padding="30")
        frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(
            frame,
            text="🔄 LLAVE DEVUELTA",
            font=('Segoe UI', 24, 'bold'),
            foreground="#1565C0"
        ).pack(pady=(0, 20))
        
        # Información del docente
        ttk.Label(
            frame,
            text=f"👤 {datos_docente.get('Nombre', 'N/A')}",
            font=('Segoe UI', 16)
        ).pack(pady=5)
        
        ttk.Label(
            frame,
            text=f"📄 Documento: {datos_docente.get('Numero de documento', 'N/A')}",
            font=('Segoe UI', 14)
        ).pack(pady=5)
        
        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Hora de devolución
        ttk.Label(
            frame,
            text=f"🕐 Hora de devolución: {hora_devolucion}",
            font=('Segoe UI', 16, 'bold'),
            foreground="#0D47A1"
        ).pack(pady=10)
        
        # Auto-cerrar
        self.ventana.after(duracion, self._cerrar)
    
    def mostrar_advertencia(self, mensaje, tiempo_faltante, callback_confirmar):
        """
        Muestra advertencia cuando falta mucho tiempo para la clase
        
        Args:
            mensaje (str): Mensaje de advertencia
            tiempo_faltante (str): Tiempo que falta para la clase
            callback_confirmar (function): Función a llamar si se confirma
        """
        if self.ventana:
            self.ventana.destroy()
        
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("Advertencia")
        
        # Configurar ventana (sin auto-cierre)
        self._configurar_ventana(self.ventana, "#FF9800", autoclose=False)
        
        # Contenido
        frame = ttk.Frame(self.ventana, padding="30")
        frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(
            frame,
            text="⚠️ ADVERTENCIA",
            font=('Segoe UI', 20, 'bold'),
            foreground="#E65100"
        ).pack(pady=(0, 20))
        
        # Mensaje
        ttk.Label(
            frame,
            text=mensaje,
            font=('Segoe UI', 14),
            wraplength=450,
            justify='center'
        ).pack(pady=10)
        
        ttk.Label(
            frame,
            text=f"⏰ Falta: {tiempo_faltante}",
            font=('Segoe UI', 16, 'bold'),
            foreground="#F57C00"
        ).pack(pady=10)
        
        # Botones
        frame_botones = ttk.Frame(frame)
        frame_botones.pack(pady=20)
        
        ttk.Button(
            frame_botones,
            text="✅ Confirmar Entrega",
            command=lambda: self._confirmar_y_cerrar(callback_confirmar)
        ).pack(side='left', padx=10)
        
        ttk.Button(
            frame_botones,
            text="❌ Cancelar",
            command=self._cerrar
        ).pack(side='left', padx=10)
    
    def mostrar_error(self, mensaje, duracion=3000):
        """
        Muestra mensaje de error
        
        Args:
            mensaje (str): Mensaje de error
            duracion (int): Tiempo en milisegundos antes de autocierre
        """
        if self.ventana:
            self.ventana.destroy()
        
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("Error")
        
        # Configurar ventana
        self._configurar_ventana(self.ventana, "#F44336")  # Rojo
        
        # Contenido
        frame = ttk.Frame(self.ventana, padding="30")
        frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(
            frame,
            text="❌ ERROR",
            font=('Segoe UI', 20, 'bold'),
            foreground="#C62828"
        ).pack(pady=(0, 20))
        
        # Mensaje
        ttk.Label(
            frame,
            text=mensaje,
            font=('Segoe UI', 14),
            wraplength=450,
            justify='center'
        ).pack(pady=10)
        
        # Auto-cerrar
        self.ventana.after(duracion, self._cerrar)
    
    def _configurar_ventana(self, ventana, color_borde, autoclose=True):
        """Configura apariencia y comportamiento de la ventana"""
        # Centrar en pantalla
        ancho = 550
        alto = 400
        
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Sin bordes de sistema (ventana moderna)
        ventana.overrideredirect(True)
        
        # Borde personalizado
        ventana.configure(bg=color_borde, highlightthickness=3, highlightbackground=color_borde)
        
        # Siempre al frente
        ventana.attributes('-topmost', True)
        
        # Si es auto-close, permitir cerrar con clic
        if autoclose:
            ventana.bind('<Button-1>', lambda e: self._cerrar())
    
    def _cerrar(self):
        """Cierra la ventana de feedback"""
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None
    
    def _confirmar_y_cerrar(self, callback):
        """Ejecuta callback de confirmación y cierra ventana"""
        self._cerrar()
        if callback:
            callback()
