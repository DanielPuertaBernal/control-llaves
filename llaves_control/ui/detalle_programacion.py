from tkinter import ttk, messagebox
import tkinter as tk
import pandas as pd

class VentanaDetalleProgramacion:
    """Ventana emergente para mostrar detalles completos de un registro de programación"""
    
    def __init__(self, parent, fila_datos):
        """
        Inicializar la ventana de detalles
        
        Args:
            parent: Ventana padre
            fila_datos: Serie de pandas con los datos del registro
        """
        self.parent = parent
        self.fila_datos = fila_datos
        self.ventana = None
        self.crear_ventana()
    
    def crear_ventana(self):
        """Crear y configurar la ventana emergente"""
        # Crear ventana emergente
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("📋 Detalles de la Programación")
        self.ventana.configure(bg='#f5f5f5')
        
        # Configurar ventana modal
        self.ventana.transient(self.parent)
        self.ventana.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.ventana, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        self.crear_titulo(main_frame)
        self.crear_tabla_datos(main_frame)
        self.crear_botones(main_frame)
        self.configurar_dimensiones()
    
    def crear_titulo(self, parent):
        """Crear el título de la ventana"""
        titulo = ttk.Label(parent, text="INFORMACIÓN COMPLETA DEL REGISTRO", 
                          font=('Segoe UI', 16, 'bold'))
        titulo.pack(pady=(0, 25))
    
    def crear_tabla_datos(self, parent):
        """Crear la tabla con los datos del registro"""
        # Frame para la tabla de datos
        self.tabla_frame = ttk.LabelFrame(parent, text="Detalles del Registro", padding="20")
        self.tabla_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Configurar grid para tabla
        self.tabla_frame.grid_columnconfigure(1, weight=1)
        
        self.llenar_datos()
    
    def llenar_datos(self):
        """Llenar la tabla con los datos del registro"""
        row_num = 0
        
        # Campos importantes primero
        campos_principales = ['profesor', 'nroidenti', 'materia', 'aula', 'dia', 'horario', 'nro_estudiantes']
        campos_mostrados = set()
        
        # Mostrar campos principales primero
        for campo in campos_principales:
            if campo in self.fila_datos.index:
                self.agregar_fila_dato(campo, self.fila_datos[campo], row_num, es_principal=True)
                campos_mostrados.add(campo)
                row_num += 1
        
        # Mostrar campos restantes
        for columna, valor in self.fila_datos.items():
            if columna not in campos_mostrados:
                self.agregar_fila_dato(columna, valor, row_num, es_principal=False)
                row_num += 1
    
    def agregar_fila_dato(self, campo, valor, row_num, es_principal=True):
        """
        Agregar una fila de datos a la tabla
        
        Args:
            campo: Nombre del campo
            valor: Valor del campo
            row_num: Número de fila
            es_principal: Si es un campo principal o secundario
        """
        # Formatear valor
        if pd.isna(valor):
            valor_mostrar = "N/A"
        else:
            valor_mostrar = str(valor)
        
        # Etiqueta del campo
        etiqueta = ttk.Label(self.tabla_frame, 
                           text=f"{self.obtener_nombre_campo(campo)}:", 
                           font=('Segoe UI', 11, 'bold'), 
                           foreground='#2E7D32')
        etiqueta.grid(row=row_num, column=0, sticky='w', padx=(0, 15), pady=8)
        
        # Valor del campo
        valor_label = ttk.Label(self.tabla_frame, 
                              text=valor_mostrar, 
                              font=('Segoe UI', 11), 
                              foreground='#424242',
                              background='white', 
                              relief='solid', 
                              borderwidth=1)
        valor_label.grid(row=row_num, column=1, sticky='ew', padx=(0, 0), 
                        pady=8, ipady=5, ipadx=10)
    
    def crear_botones(self, parent):
        """Crear el frame con botones de acción"""
        # Frame para botones con estilo mejorado
        frame_botones = ttk.Frame(parent)
        frame_botones.pack(fill='x', pady=(15, 0))
        
        # Botón cerrar con estilo personalizado
        style = ttk.Style()
        style.configure("Cerrar.TButton",
                       padding=(20, 10),
                       font=('Segoe UI', 11, 'bold'),
                       relief="raised")
        
        btn_cerrar = ttk.Button(frame_botones, 
                               text="✖ Cerrar Ventana", 
                               command=self.cerrar_ventana,
                               style="Cerrar.TButton")
        btn_cerrar.pack(side='right', padx=(10, 0))
    
    def configurar_dimensiones(self):
        """Configurar el tamaño y posición de la ventana"""
        # Ajustar tamaño de ventana al contenido sin scroll
        self.ventana.update_idletasks()
        
        # Calcular el tamaño real necesario
        tabla_width = self.tabla_frame.winfo_reqwidth()
        tabla_height = self.tabla_frame.winfo_reqheight()
        
        # Calcular tamaño total de la ventana
        # Añadir espacio para padding, título, botones, etc.
        total_width = max(650, tabla_width + 100)  # Mínimo 650px
        total_height = tabla_height + 200  # Espacio para título, padding y botón
        
        # Obtener dimensiones de pantalla
        screen_width = self.ventana.winfo_screenwidth()
        screen_height = self.ventana.winfo_screenheight()
        
        # Limitar a un máximo del 90% de la pantalla para que siempre quepa
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)
        
        # Aplicar límites si es necesario
        final_width = min(total_width, max_width)
        final_height = min(total_height, max_height)
        
        # Centrar en pantalla
        x = (screen_width - final_width) // 2
        y = (screen_height - final_height) // 2
        
        # Asegurar que la ventana no se salga de la pantalla
        x = max(10, min(x, screen_width - final_width - 10))
        y = max(10, min(y, screen_height - final_height - 10))
        
        self.ventana.geometry(f"{final_width}x{final_height}+{x}+{y}")
        self.ventana.resizable(True, True)  # Permitir redimensionar si el usuario lo necesita
    
    def obtener_nombre_campo(self, campo):
        """
        Convertir nombres de campos a nombres más legibles
        
        Args:
            campo: Nombre del campo técnico
            
        Returns:
            str: Nombre legible del campo
        """
        nombres_campo = {
            'profesor': 'Profesor',
            'nroidenti': 'Documento',
            'materia': 'Materia',
            'aula': 'Aula',
            'dia': 'Día',
            'horario': 'Horario',
            'nro_estudiantes': 'Nº Estudiantes',
            'hora_ini': 'Hora Inicio',
            'hora_fin': 'Hora Fin',
            'grupo': 'Grupo',
            'nivel_grupo': 'Nivel del Grupo',
            'semestre': 'Semestre',
            'PROGRAMA': 'Programa',
            'TOTAL': 'Total'
        }
        return nombres_campo.get(campo.lower(), campo.title())
    
    def cerrar_ventana(self):
        """Cerrar la ventana de detalles"""
        if self.ventana:
            self.ventana.destroy()
    
    def mostrar(self):
        """Mostrar la ventana (método público para usar desde fuera)"""
        if self.ventana:
            self.ventana.focus_set()
