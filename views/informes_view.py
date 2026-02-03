"""
Vista de Informes del día
Muestra todos los registros de llaves del día con colores según el estado
"""
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from datetime import date
from application.historial_service import HistorialService
from application.llave_service import LlaveService
from infrastructure.repositories.llave_mongo_repository import LlaveMongoRepository
from services import TablaService, PaginacionService
from views.components import BuscadorComponent


class InformesView:
    """Vista para mostrar informes diarios de llaves"""
    
    # Colores
    COLOR_DEVUELTA = "#C8E6C9"   # Verde suave
    COLOR_PRESTAMO = "#FFE0B2"   # Naranja suave
    COLOR_RETRASO = "#FFCDD2"    # Rojo suave
    
    def __init__(self, parent_frame):
        repo_llaves = LlaveMongoRepository()
        self.historial_service = HistorialService(repo_llaves)
        self.llave_service = LlaveService(repo_llaves)
        
        # Servicio de paginación
        self.paginacion_service = PaginacionService(items_por_pagina=15)
        
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
        
        # Controles de paginación compactos a la derecha
        self.btn_siguiente = ttk.Button(frame_controles, text="▶", width=3, command=self._pagina_siguiente)
        self.btn_siguiente.pack(side='right', padx=(5, 0))
        
        self.label_pagina = ttk.Label(frame_controles, text="Página 1 de 1", font=('Segoe UI', 9))
        self.label_pagina.pack(side='right', padx=8)
        
        self.btn_anterior = ttk.Button(frame_controles, text="◀", width=3, command=self._pagina_anterior)
        self.btn_anterior.pack(side='right', padx=(0, 5))
        
        # Botón exportar a la derecha (después de los controles de paginación)
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
        """Configura columnas del Treeview (oculta Documento, Facultad y Día)"""
        columnas = (
            'Docente', 'Horario', 'Aula',
            'Materia', 'Hora Entrega', 'Hora Devolución',
            'Duración', 'Se reclamó a tiempo', 'Tiempo de retraso', 'Estado'
        )
        anchos = [180, 130, 90, 180, 110, 115, 115, 130, 120, 160]
        
        self.tree.configure(columns=columnas, show='headings', height=20)
        
        for col, ancho in zip(columnas, anchos):
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=ancho, anchor='center')
    
    def actualizar_datos(self):
        """Carga los datos del registro de llaves del día"""
        self.datos_dia = self._obtener_registros_dia()
        self.datos_filtrados = self.datos_dia.copy()
        self.paginacion_service.actualizar_datos(self.datos_filtrados)
        self._actualizar_tabla()
    
    def _pagina_anterior(self):
        """Va a página anterior"""
        self.paginacion_service.pagina_anterior()
        self._actualizar_tabla()
    
    def _pagina_siguiente(self):
        """Va a página siguiente"""
        self.paginacion_service.pagina_siguiente()
        self._actualizar_tabla()
    
    def _obtener_registros_dia(self):
        """Obtiene registros del día (entregadas hoy) y llaves en préstamo de días anteriores"""
        try:
            import pandas as pd
            
            df = self.historial_service.obtener_historial_completo()
            
            if df.empty:
                return []
            
            # Filtrar por:
            # 1. Fecha de entrega del día (entregadas hoy)
            # 2. O Estado = 'En Préstamo' (llaves que se deben desde días anteriores)
            fecha_hoy = date.today().strftime('%Y-%m-%d')
            df_entregadas_hoy = df[df['Fecha de entrega'].astype(str).str.contains(fecha_hoy, na=False)]
            df_en_prestamo = df[df['Estado'] == 'En Préstamo']
            
            # Combinar ambos filtros
            df_filtrado = pd.concat([df_entregadas_hoy, df_en_prestamo]).drop_duplicates()
            
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
        
        # Actualizar paginación con datos filtrados
        self.paginacion_service.actualizar_datos(self.datos_filtrados)
        self._actualizar_tabla()
    
    def _actualizar_tabla(self):
        """Actualiza la tabla con los datos filtrados"""
        from datetime import datetime, time, date
        
        # Obtener página actual
        datos_pagina, inicio, fin = self.paginacion_service.obtener_pagina_actual()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar datos con colores según estado (sin mostrar Documento, Facultad y Día)
        for idx, registro in enumerate(datos_pagina):
            # Determinar estado con indicador de retraso si aplica
            estado = registro.get('Estado', '')
            horario = registro.get('Horario', '')
            fecha_entrega_str = registro.get('Fecha de entrega', '')
            
            if estado == 'En Préstamo':
                if self.llave_service.evaluar_retraso_entrega(horario):
                    estado_mostrado = 'En Préstamo - Retraso en Entrega'
                else:
                    estado_mostrado = estado
            else:
                estado_mostrado = estado
            
            valores = (
                str(registro.get('Docente', '')),
                str(registro.get('Horario', '')),
                str(registro.get('Aula', '')),
                str(registro.get('Materia de la Clase', '')),
                str(registro.get('Hora de entrega', '')),
                str(registro.get('Hora de devolución', '') if registro.get('Hora de devolución') else ''),
                str(registro.get('Duración clase (entrega→devolución)', '')),
                str(registro.get('Se reclamó a tiempo', '')),
                str(registro.get('Tiempo de retraso', '')),
                estado_mostrado
            )
            
            # Determinar etiqueta de color según estado
            tag = ''
            
            if estado == 'Devuelta':
                tag = 'devuelta'
            elif estado == 'En Préstamo':
                # Verificar si hay retraso en entrega
                hay_retraso = False
                
                # Si es hoy: usar evaluar_retraso_entrega (> 1 hora después de fin de clase)
                try:
                    fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
                    if fecha_entrega == date.today():
                        hay_retraso = self.llave_service.evaluar_retraso_entrega(horario)
                    else:
                        # Si es de días anteriores: definitivamente está en retraso
                        hay_retraso = True
                except:
                    # Por defecto, usar evaluar_retraso_entrega
                    hay_retraso = self.llave_service.evaluar_retraso_entrega(horario)
                
                tag = 'retraso' if hay_retraso else 'prestamo'
            
            self.tree.insert('', 'end', values=valores, tags=(tag,))
        
        # Configurar estilos de etiquetas
        self.tree.tag_configure('devuelta', background=self.COLOR_DEVUELTA)
        self.tree.tag_configure('prestamo', background=self.COLOR_PRESTAMO)
        self.tree.tag_configure('retraso', background=self.COLOR_RETRASO)
        
        # Actualizar labels de paginación
        info = self.paginacion_service.obtener_info_paginacion()
        self.label_pagina.config(text=f"Página {info['pagina_actual']} de {info['total_paginas']}")
        self.label_info.config(text=f"{info['total_items']} registros")
        
        self.btn_anterior.config(state='normal' if info['tiene_anterior'] else 'disabled')
        self.btn_siguiente.config(state='normal' if info['tiene_siguiente'] else 'disabled')
    
    def _exportar_registros(self):
        """Exporta TODOS los registros de la base de datos a un archivo Excel"""
        try:
            import pandas as pd
            
            # Obtener TODOS los registros de la base de datos (no solo del día)
            df_completo = self.historial_service.obtener_historial_completo()
            
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
                'Fecha de devolución', 'Hora de devolución',
                'Duración clase (entrega→devolución)',
                'Se reclamó a tiempo',
                'Tiempo de retraso',
                'Retraso en entrega',
                'Estado'
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
