"""
Vista de Informes del día
Muestra todos los registros de llaves del día con colores según el estado
"""
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from datetime import date
from controllers import LlaveController
from services import TablaService
from views.components import BuscadorComponent


class InformesView:
    """Vista para mostrar informes diarios de llaves"""
    
    # Colores
    COLOR_DEVUELTA = "#C8E6C9"   # Verde suave
    COLOR_PRESTAMO = "#FFE0B2"   # Naranja suave
    
    def __init__(self, parent_frame):
        self.llave_controller = LlaveController()
        
        # Frame principal
        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)
        
        # Datos
        self.datos_dia = []
        self.datos_filtrados = []
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Cargar datos
        self.actualizar_datos()
    
    def _crear_interfaz(self):
        """Crea los componentes visuales"""
        # Componente de búsqueda
        self.buscador = BuscadorComponent(
            self.frame,
            callback_busqueda=self._realizar_busqueda,
            label_texto="Buscar:",
            placeholder="Por documento, docente, aula o materia..."
        )
        
        # Frame superior con botones de control
        frame_controles = ttk.Frame(self.frame)
        frame_controles.pack(fill='x', pady=(0, 15))
        
        # Botón actualizar a la izquierda
        btn_actualizar = ttk.Button(
            frame_controles,
            text="🔄 Actualizar",
            command=self.actualizar_datos
        )
        btn_actualizar.pack(side='left', padx=(0, 20))
        
        # Información de registros
        self.label_info = ttk.Label(
            frame_controles,
            text="0 registros",
            font=('Segoe UI', 9)
        )
        self.label_info.pack(side='left')
        
        # Botón exportar a la derecha
        btn_exportar = ttk.Button(
            frame_controles,
            text="📊 Exportar a Excel",
            command=self._exportar_registros
        )
        btn_exportar.pack(side='right', padx=(10, 0))
        
        # Frame de la tabla
        frame_tabla = ttk.Frame(self.frame)
        frame_tabla.pack(fill='both', expand=True)
        
        # Crear Treeview
        self.tree = ttk.Treeview(frame_tabla, height=20)
        self._configurar_treeview()
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(frame_tabla, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
    
    def _configurar_treeview(self):
        """Configura las columnas del Treeview (sin mostrar Documento, Facultad y Día)"""
        columnas = (
            'Docente', 'Horario', 'Aula',
            'Materia', 'Hora Entrega', 'Hora Devolución', 'Estado'
        )
        anchos = [180, 150, 90, 220, 120, 130, 100]
        
        self.tree.configure(columns=columnas, show='headings', height=20)
        
        for col, ancho in zip(columnas, anchos):
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=ancho, anchor='center')
    
    def actualizar_datos(self):
        """Carga los datos del registro de llaves del día"""
        self.datos_dia = self._obtener_registros_dia()
        self.datos_filtrados = self.datos_dia.copy()
        self._actualizar_tabla()
    
    def _obtener_registros_dia(self):
        """Obtiene todos los registros del día (en préstamo y devueltos)"""
        try:
            from models import LlaveModel
            import pandas as pd
            
            modelo = LlaveModel()
            df = modelo.obtener_historial_completo()
            
            if df.empty:
                return []
            
            # Filtrar por fecha de entrega del día
            fecha_hoy = date.today().strftime('%Y-%m-%d')
            df_filtrado = df[df['Fecha de entrega'].astype(str).str.contains(fecha_hoy, na=False)]
            
            # Convertir a lista de diccionarios
            registros = df_filtrado.to_dict('records')
            return registros
            
        except Exception as e:
            print(f"Error al obtener registros del día: {e}")
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            return []
    
    def _realizar_busqueda(self):
        """Filtra los datos según el término de búsqueda"""
        termino = self.buscador.obtener_termino()
        
        if not termino:
            # Sin búsqueda, mostrar todos los datos
            self.datos_filtrados = self.datos_dia.copy()
        else:
            # Normalizar término
            termino_normalizado = self.buscador.normalizar_texto(termino)
            
            # Filtrar por múltiples campos (incluyendo documento y facultad aunque no se vean)
            self.datos_filtrados = [
                registro for registro in self.datos_dia
                if (termino_normalizado in self.buscador.normalizar_texto(str(registro.get('Número de Documento', ''))) or
                    termino_normalizado in self.buscador.normalizar_texto(str(registro.get('Docente', ''))) or
                    termino_normalizado in self.buscador.normalizar_texto(str(registro.get('Aula', ''))) or
                    termino_normalizado in self.buscador.normalizar_texto(str(registro.get('Materia de la Clase', ''))) or
                    termino_normalizado in self.buscador.normalizar_texto(str(registro.get('Facultad', ''))))
            ]
        
        self._actualizar_tabla()
    
    def _actualizar_tabla(self):
        """Actualiza la tabla con los datos filtrados"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar datos con colores según estado (sin mostrar Documento, Facultad y Día)
        for idx, registro in enumerate(self.datos_filtrados):
            valores = (
                str(registro.get('Docente', '')),
                str(registro.get('Horario', '')),
                str(registro.get('Aula', '')),
                str(registro.get('Materia de la Clase', '')),
                str(registro.get('Hora de entrega', '')),
                str(registro.get('Hora de devolución', '') if registro.get('Hora de devolución') else ''),
                str(registro.get('Estado', ''))
            )
            
            # Determinar etiqueta de color según estado
            estado = registro.get('Estado', '')
            if estado == 'Devuelta':
                tag = 'devuelta'
            elif estado == 'En Préstamo':
                tag = 'prestamo'
            else:
                tag = ''
            
            self.tree.insert('', 'end', values=valores, tags=(tag,))
        
        # Configurar estilos de etiquetas
        self.tree.tag_configure('devuelta', background=self.COLOR_DEVUELTA)
        self.tree.tag_configure('prestamo', background=self.COLOR_PRESTAMO)
        
        # Actualizar etiqueta de información (solo total)
        total = len(self.datos_filtrados)
        self.label_info.config(text=f"{total} registros")
    
    def _exportar_registros(self):
        """Exporta TODOS los registros de la base de datos a un archivo Excel"""
        try:
            from models import LlaveModel
            import pandas as pd
            
            # Obtener TODOS los registros de la base de datos (no solo del día)
            modelo = LlaveModel()
            df_completo = modelo.obtener_historial_completo()
            
            if df_completo.empty:
                messagebox.showwarning("Advertencia", "No hay registros para exportar")
                return
            
            # Seleccionar ubicación de guardado
            fecha_hoy = date.today().strftime('%Y-%m-%d')
            nombre_archivo = f"Registro_Completo_Llaves_{fecha_hoy}.xlsx"
            
            ruta_guardado = filedialog.asksaveasfilename(
                title="Guardar registro completo de llaves",
                defaultextension=".xlsx",
                filetypes=[
                    ("Archivo Excel", "*.xlsx"),
                    ("Todos los archivos", "*.*")
                ],
                initialfile=nombre_archivo
            )
            
            if not ruta_guardado:
                return
            
            # Mantener el orden original de columnas tal como están en el archivo
            columnas_orden = [
                'Número de Documento', 'Docente', 'Día', 'Horario', 'Aula', 'Facultad',
                'Materia de la Clase', 'Fecha de entrega', 'Hora de entrega',
                'Fecha de devolución', 'Hora de devolución', 'Estado'
            ]
            
            # Seleccionar solo las columnas que existan en el DataFrame
            columnas_validas = [col for col in columnas_orden if col in df_completo.columns]
            df_exportar = df_completo[columnas_validas]
            
            # Exportar a Excel
            df_exportar.to_excel(ruta_guardado, index=False, engine='openpyxl')
            
            total_registros = len(df_exportar)
            messagebox.showinfo("Éxito", f"Registro completo exportado ({total_registros} registros)\nUbicación:\n{ruta_guardado}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")
