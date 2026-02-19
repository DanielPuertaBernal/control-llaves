"""
Vista del sistema NFC y estado del lector de carnets
Muestra información en tiempo real del sistema de entregas/devoluciones
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class NFCView:
    """Vista para monitoreo del sistema NFC"""
    
    def __init__(self, parent, nfc_feedback_panel=None):
        """
        Args:
            parent: Frame padre
            nfc_feedback_panel: Obsoleto (se mantiene por compatibilidad)
        """
        self.parent = parent
        self.frame = None
        self._crear_vista()
    
    def _crear_vista(self):
        """Crea la vista del sistema NFC"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)
        
        # ========== ESTADO DEL SISTEMA ==========
        frame_estado = ttk.LabelFrame(self.frame, text="📊 ESTADO DEL SISTEMA", padding=15)
        frame_estado.pack(fill='x', padx=15, pady=(10, 20))
        
        # Indicador de conexión NFC
        frame_conexion = ttk.Frame(frame_estado)
        frame_conexion.pack(fill='x', pady=10)
        
        self.indicador_nfc = tk.Label(
            frame_conexion,
            text='●',
            font=('Arial', 16),
            fg='#4CAF50'
        )
        self.indicador_nfc.pack(side='left', padx=(0, 10))
        
        self.estado_nfc = ttk.Label(
            frame_conexion,
            text='Lector NFC Conectado',
            font=('Segoe UI', 12, 'bold')
        )
        self.estado_nfc.pack(side='left')
        
        # ========== ÚLTIMA OPERACIÓN ==========
        frame_operacion = ttk.LabelFrame(self.frame, text="📋 ÚLTIMA OPERACIÓN", padding=15)
        frame_operacion.pack(fill='both', expand=True, padx=15, pady=(0, 20))
        
        # Contenedor scrollable
        canvas = tk.Canvas(frame_operacion, bg='white', highlightthickness=0, height=300)
        scrollbar = ttk.Scrollbar(frame_operacion, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Detalles de operación
        self.frame_detalles = scrollable_frame
        
        # Mensaje inicial
        self.info_operacion = ttk.Label(
            self.frame_detalles,
            text='Esperando lectura de carnet...',
            font=('Segoe UI', 11),
            foreground='#666666',
            justify='left',
            wraplength=400
        )
        self.info_operacion.pack(pady=20, padx=20)
    
    def actualizar_operacion(self, resultado):
        """Actualiza la información de la última operación"""
        try:
            # Verificar que el widget sigue existiendo
            if not self.frame_detalles.winfo_exists():
                return
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Limpiar detalles anteriores
            for widget in self.frame_detalles.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
            
            if resultado['accion'] == 'entrega':
                self._mostrar_entrega(resultado, timestamp)
            elif resultado['accion'] == 'devolucion':
                self._mostrar_devolucion(resultado, timestamp)
            elif resultado['accion'] == 'advertencia':
                self._mostrar_advertencia(resultado, timestamp)
            elif resultado['accion'] == 'error':
                self._mostrar_error(resultado, timestamp)
        except Exception as e:
            print(f"Error al actualizar operación NFC: {e}")
    
    def _mostrar_entrega(self, resultado, timestamp):
        """Muestra detalles de entrega con diseño elegante y proporcional"""
        # Frame contenedor principal
        frame = ttk.Frame(self.frame_detalles)
        frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # === ENCABEZADO ===
        titulo_frame = tk.Frame(frame, bg='white', height=50)
        titulo_frame.pack(fill='x', padx=15, pady=0)
        
        ttk.Label(
            titulo_frame,
            text='✅ LLAVE ENTREGADA',
            font=('Segoe UI', 12, 'bold'),
            foreground='#2e7d32'
        ).pack(side='left', pady=10)
        
        ttk.Label(
            titulo_frame,
            text=f'({timestamp})',
            font=('Segoe UI', 9),
            foreground='#999999'
        ).pack(side='right', pady=10)
        
        # === CONTENIDO PRINCIPAL CENTRADO ===
        content_frame = tk.Frame(frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=15, pady=0)
        
        # Espaciador superior
        tk.Frame(content_frame).pack(fill='both', expand=True)
        
        # Docente (22px - principal)
        docente = resultado['datos_docente'].get('Nombre', 'N/A')
        tk.Label(
            content_frame,
            text=docente,
            font=('Segoe UI', 22, 'bold'),
            foreground='#1565C0',
            background='white'
        ).pack(pady=12)
        
        # Materia (15px)
        materia = resultado['datos_clase'].get('Materia', 'N/A')
        tk.Label(
            content_frame,
            text=materia,
            font=('Segoe UI', 15),
            foreground='#616161',
            background='white'
        ).pack(pady=8)
        
        # === HORARIO - Texto pequeño ===
        horario_frame = tk.Frame(content_frame, bg='white', relief='flat', bd=0)
        horario_frame.pack(fill='x', pady=20)
        
        horario = resultado['datos_clase'].get('Horario', 'N/A')
        tk.Label(
            horario_frame,
            text=horario,
            font=('Segoe UI', 20),
            foreground='#455A64',
            background='white'
        ).pack(expand=True, fill='both', pady=18, padx=20)
        
        # Aula (destacado en naranja)
        aula = resultado['datos_clase'].get('Aula', 'N/A')
        tk.Label(
            content_frame,
            text=f"Salón: {aula}",
            font=('Segoe UI', 32, 'bold'),
            foreground='#F57F17',
            background='white'
        ).pack(pady=12)
        
        # Espaciador inferior
        tk.Frame(content_frame).pack(fill='both', expand=True)
    
    def _mostrar_devolucion(self, resultado, timestamp):
        """Muestra detalles de devolución con diseño elegante y proporcional"""
        frame = ttk.Frame(self.frame_detalles)
        frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # === ENCABEZADO ===
        titulo_frame = tk.Frame(frame, bg='white', height=50)
        titulo_frame.pack(fill='x', padx=15, pady=0)
        
        ttk.Label(
            titulo_frame,
            text='🔄 LLAVE DEVUELTA',
            font=('Segoe UI', 12, 'bold'),
            foreground='#1565C0'
        ).pack(side='left', pady=10)
        
        ttk.Label(
            titulo_frame,
            text=f'({timestamp})',
            font=('Segoe UI', 9),
            foreground='#999999'
        ).pack(side='right', pady=10)
        
        # === CONTENIDO PRINCIPAL CENTRADO ===
        content_frame = tk.Frame(frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=15, pady=0)
        
        # Espaciador superior
        tk.Frame(content_frame).pack(fill='both', expand=True)
        
        # Docente (22px - principal)
        docente = resultado['datos_docente'].get('Nombre', 'N/A')
        tk.Label(
            content_frame,
            text=docente,
            font=('Segoe UI', 22, 'bold'),
            foreground='#1565C0',
            background='white'
        ).pack(pady=12)
        
        # Documento (15px)
        documento = resultado['datos_docente'].get('Numero de documento', 'N/A')
        tk.Label(
            content_frame,
            text=f"Doc: {documento}",
            font=('Segoe UI', 15),
            foreground='#616161',
            background='white'
        ).pack(pady=8)
        
        # === HORA DE DEVOLUCIÓN - Elemento destacado ===
        hora_frame = tk.Frame(content_frame, bg='white', relief='flat', bd=0)
        hora_frame.pack(fill='x', pady=20)
        
        hora = resultado['hora_devolucion']
        tk.Label(
            hora_frame,
            text=hora,
            font=('Segoe UI', 32, 'bold'),
            foreground='#0D47A1',
            background='white'
        ).pack(expand=True, fill='both', pady=18, padx=20)
        
        # Espaciador inferior
        tk.Frame(content_frame).pack(fill='both', expand=True)
    
    def _mostrar_advertencia(self, resultado, timestamp):
        """Muestra detalles de advertencia con mismo diseño elegante"""
        frame = ttk.Frame(self.frame_detalles)
        frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # === ENCABEZADO ===
        titulo_frame = tk.Frame(frame, bg='white', height=50)
        titulo_frame.pack(fill='x', padx=15, pady=0)
        
        ttk.Label(
            titulo_frame,
            text='⚠️ ADVERTENCIA',
            font=('Segoe UI', 12, 'bold'),
            foreground='#E65100'
        ).pack(side='left', pady=10)
        
        ttk.Label(
            titulo_frame,
            text=f'({timestamp})',
            font=('Segoe UI', 9),
            foreground='#999999'
        ).pack(side='right', pady=10)
        
        # === CONTENIDO PRINCIPAL CENTRADO ===
        content_frame = tk.Frame(frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=15, pady=0)
        
        # Espaciador superior
        tk.Frame(content_frame).pack(fill='both', expand=True)
        
        # Mensaje (18px)
        tk.Label(
            content_frame,
            text=resultado['mensaje'],
            font=('Segoe UI', 18),
            foreground='#E65100',
            background='white',
            wraplength=500,
            justify='center'
        ).pack(pady=15)
        
        # === TIEMPO FALTANTE - Elemento destacado ===
        tiempo_frame = tk.Frame(content_frame, bg='white', relief='flat', bd=0)
        tiempo_frame.pack(fill='x', pady=20)
        
        tiempo = resultado['tiempo_faltante']
        tk.Label(
            tiempo_frame,
            text=f"Falta: {tiempo}",
            font=('Segoe UI', 32, 'bold'),
            foreground='#E65100',
            background='white'
        ).pack(expand=True, fill='both', pady=18, padx=20)
        
        # === BOTONES DE CONFIRMACIÓN ===
        botones_frame = tk.Frame(content_frame, bg='white')
        botones_frame.pack(fill='x', pady=20)
        
        callback = resultado.get('callback_confirmar')
        
        # Botón Aceptar
        tk.Button(
            botones_frame,
            text='✅ Aceptar',
            font=('Segoe UI', 14, 'bold'),
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=30,
            pady=15,
            command=lambda: self._procesar_confirmacion(callback, True)
        ).pack(side='left', padx=15, expand=True, fill='both')
        
        # Botón Rechazar
        tk.Button(
            botones_frame,
            text='❌ Rechazar',
            font=('Segoe UI', 14, 'bold'),
            bg='#f44336',
            fg='white',
            activebackground='#da190b',
            activeforeground='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=30,
            pady=15,
            command=lambda: self._procesar_confirmacion(callback, False)
        ).pack(side='left', padx=15, expand=True, fill='both')
        
        # Espaciador inferior
        tk.Frame(content_frame).pack(fill='both', expand=True)
    
    def _mostrar_error(self, resultado, timestamp):
        """Muestra detalles de error"""
        frame = ttk.Frame(self.frame_detalles)
        frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # === ENCABEZADO ===
        titulo_frame = tk.Frame(frame, bg='white', height=50)
        titulo_frame.pack(fill='x', padx=15, pady=0)
        
        ttk.Label(
            titulo_frame,
            text='❌ ERROR',
            font=('Segoe UI', 12, 'bold'),
            foreground='#C62828'
        ).pack(side='left', pady=10)
        
        ttk.Label(
            titulo_frame,
            text=f'({timestamp})',
            font=('Segoe UI', 9),
            foreground='#999999'
        ).pack(side='right', pady=10)
        
        # === CONTENIDO PRINCIPAL CENTRADO ===
        content_frame = tk.Frame(frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=15, pady=0)
        
        # Espaciador superior
        tk.Frame(content_frame).pack(fill='both', expand=True)
        
        # Mensaje de error (grande y centrado)
        tk.Label(
            content_frame,
            text=resultado['mensaje'],
            font=('Segoe UI', 20),
            foreground='#C62828',
            background='white',
            wraplength=500,
            justify='center'
        ).pack(pady=20)
        
        # Espaciador inferior
        tk.Frame(content_frame).pack(fill='both', expand=True)
    
    def _procesar_confirmacion(self, callback, aceptado):
        """Procesa la confirmación del usuario"""
        if aceptado and callback:
            callback()
        # Limpiar vista después de confirmar
        for widget in self.frame_detalles.winfo_children():
            widget.destroy()
        # Recrear mensaje inicial
        self.info_operacion = ttk.Label(
            self.frame_detalles,
            text='Esperando lectura de carnet...',
            font=('Segoe UI', 11),
            foreground='#666666',
            justify='left',
            wraplength=400
        )
        self.info_operacion.pack(pady=20, padx=20)
