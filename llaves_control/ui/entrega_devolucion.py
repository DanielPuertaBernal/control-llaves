from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from datetime import datetime
import locale
from openpyxl import Workbook
from helpers.gestion_excel import (registrar_entrega, registrar_devolucion, 
                                 obtener_llaves_pendientes, limpiar_numero_documento, 
                                 obtener_historial_completo, verificar_llave_entregada)
from helpers.limpieza_programacion import limpiar_programacion

class VistaEntregaDevolucion:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_entrega = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_entrega, text="🔑 Devolución de Llaves")
        
        # Variables para paginación
        self.pagina_actual = 1
        self.items_por_pagina = 15  # Cambiado de 20 a 15
        self.datos_filtrados = []
        self.total_paginas = 1
        
        # Variable para el temporizador de actualización automática
        self.auto_update_job = None
        
        self.crear_vista_entrega_devolucion()
        self.iniciar_actualizacion_automatica()

    def crear_vista_entrega_devolucion(self):
        # Obtener día actual directamente en el formato que usa el archivo
        dia_numero = datetime.now().weekday()  # 0=Monday, 6=Sunday
        dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        dia_actual = dias_espanol[dia_numero]
        
        # Título único que incluye el día
        self.label_dia = ttk.Label(self.frame_entrega, 
                                  text=f"CLASES DEL DÍA: {dia_actual}", 
                                  font=('Segoe UI', 16, 'bold'))
        self.label_dia.pack(pady=(0, 20))

        # Frame para búsqueda
        frame_busqueda = ttk.Frame(self.frame_entrega)
        frame_busqueda.pack(fill='x', pady=(0, 20))
        
        ttk.Label(frame_busqueda, text="Buscar por Número de Documento:").pack(anchor='w', pady=(0, 5))
        
        self.entry_busqueda = ttk.Entry(frame_busqueda, font=('Segoe UI', 11))
        self.entry_busqueda.pack(fill='x')
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_por_documento)

        # Frame para controles de paginación (movido más arriba)
        frame_paginacion = ttk.Frame(self.frame_entrega)
        frame_paginacion.pack(fill='x', pady=(15, 10))
        
        # Botones de navegación
        self.btn_anterior = ttk.Button(frame_paginacion, text="◀ Anterior", 
                                      command=self.pagina_anterior, state='disabled')
        self.btn_anterior.pack(side='left')
        
        self.btn_siguiente = ttk.Button(frame_paginacion, text="Siguiente ▶", 
                                       command=self.pagina_siguiente, state='disabled')
        self.btn_siguiente.pack(side='right')
        
        # Label de información de página
        self.label_pagina = ttk.Label(frame_paginacion, text="Página 1 de 1 (0 registros)")
        self.label_pagina.pack(expand=True)

        # Frame para la tabla principal
        frame_tabla = ttk.Frame(self.frame_entrega)
        frame_tabla.pack(fill='both', expand=True, pady=(0, 15))

        # Configurar tabla con las columnas requeridas
        columnas = ('Documento', 'Docente', 'Aula', 'Horario', 'Materia')
        self.tree_clases = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)
        
        # Configurar encabezados y anchos de columnas
        anchos = [120, 180, 80, 120, 200]
        for col, ancho in zip(columnas, anchos):
            self.tree_clases.heading(col, text=col, anchor='center')  # Centrar encabezados
            self.tree_clases.column(col, width=ancho, anchor='center')  # Centrar contenido

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_clases.yview)
        self.tree_clases.configure(yscrollcommand=scrollbar.set)
        self.tree_clases.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Botón para actualizar datos
        btn_actualizar = ttk.Button(self.frame_entrega, text="🔄 Actualizar Datos", 
                                   command=self.cargar_clases_del_dia, style="Accent.TButton")
        btn_actualizar.pack(pady=(15, 0))

        # Label de información de actualización automática
        self.label_auto_update = ttk.Label(self.frame_entrega, 
                                          text="⏰ Actualización automática cada 10 minutos", 
                                          font=('Segoe UI', 9), 
                                          foreground='gray')
        self.label_auto_update.pack(pady=(5, 0))

        # NO cargar datos iniciales aquí - se cargará después de que la programación esté disponible

    # ============ FUNCIONES PRINCIPALES ============
    
    def cargar_clases_del_dia(self):
        """Carga y muestra las clases del día actual desde programacion_limpia_actual.xlsx"""
        if self.app.programacion is None or self.app.programacion.empty:
            messagebox.showwarning("Advertencia", 
                                 "No hay programación cargada. Por favor, cargue la programación primero.")
            return

        try:
            # Obtener día actual directamente en el formato del archivo (MAYÚSCULAS, español)
            dia_numero = datetime.now().weekday()  # 0=Monday, 6=Sunday
            dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            dia_actual = dias_espanol[dia_numero]
            
            # Actualizar label del día
            self.label_dia.config(text=f"CLASES DEL DÍA: {dia_actual}")
            
            # Filtrar por día actual directamente - sin complicaciones
            df = self.app.programacion
            if 'Día' not in df.columns:
                messagebox.showwarning("Advertencia", f"Columnas disponibles: {list(df.columns)}")
                # Buscar columnas que contengan 'día' (insensible a mayúsculas)
                columna_dia = None
                for col in df.columns:
                    if 'día' in col.lower():
                        columna_dia = col
                        break
                if columna_dia is None:
                    messagebox.showerror("Error", "No se encontró ninguna columna de día en la programación")
                    return
            else:
                columna_dia = 'Día'
                
            self.datos_filtrados = df[df[columna_dia] == dia_actual].copy()
            
            # Ordenar por horario
            if 'Horario' in self.datos_filtrados.columns:
                self.datos_filtrados = self.datos_filtrados.sort_values(by='Horario')
            
            # Eliminar clases cuyo horario ya pasó
            self.eliminar_clases_pasadas()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar las clases del día: {str(e)}")
    
    def buscar_por_documento(self, event=None):
        """Busca clases por número de documento del docente"""
        termino = self.entry_busqueda.get().strip()
        
        if not termino:
            # Si no hay término, mostrar todas las clases del día
            self.cargar_clases_del_dia()
            return
        
        if self.app.programacion is None or self.app.programacion.empty:
            messagebox.showwarning("Advertencia", 
                                 "No hay programación cargada. Por favor, cargue la programación primero.")
            return
        
        try:
            # Obtener día actual directamente en el formato del archivo
            dia_numero = datetime.now().weekday()  # 0=Monday, 6=Sunday
            dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            dia_actual = dias_espanol[dia_numero]
            
            # Filtrar por día actual
            df = self.app.programacion
            if 'Día' not in df.columns:
                # Buscar columnas que contengan 'día' (insensible a mayúsculas)
                columna_dia = None
                for col in df.columns:
                    if 'día' in col.lower():
                        columna_dia = col
                        break
                if columna_dia is None:
                    messagebox.showerror("Error", "No se encontró ninguna columna de día en la programación")
                    return
            else:
                columna_dia = 'Día'
                
            datos_del_dia = df[df[columna_dia] == dia_actual].copy()
            
            # Verificar que existe la columna de documento
            if 'Número de Documento' not in datos_del_dia.columns:
                messagebox.showerror("Error", "No se encontró la columna 'Número de Documento' en la programación")
                return
            
            # Limpiar números de documento y buscar
            datos_del_dia['nroidenti_limpio'] = datos_del_dia['Número de Documento'].astype(str).apply(limpiar_numero_documento)
            mascara_documento = datos_del_dia['nroidenti_limpio'].str.contains(termino, na=False, case=False)
            
            # Aplicar filtro
            self.datos_filtrados = datos_del_dia[mascara_documento].copy()
            
            # Ordenar por horario
            if 'Horario' in self.datos_filtrados.columns:
                self.datos_filtrados = self.datos_filtrados.sort_values(by='Horario')
            
            # Reiniciar paginación
            self.pagina_actual = 1
            self.calcular_paginacion()
            self.mostrar_pagina_actual()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def eliminar_clases_pasadas(self):
        """Elimina de la tabla las clases que ya terminaron."""
        try:
            ahora = datetime.now()
            
            # Filtrar las clases que aún no han terminado
            if 'Hora Fin' in self.datos_filtrados.columns:
                def convertir_hora_fin(hora_fin):
                    try:
                        # Manejar formato HH:MM:SS
                        if isinstance(hora_fin, str):
                            if len(hora_fin.split(':')) == 3:
                                return datetime.strptime(hora_fin, '%H:%M:%S').time()
                            else:
                                return datetime.strptime(hora_fin, '%H:%M').time()
                        return None
                    except ValueError:
                        return None
                
                self.datos_filtrados['Hora_Fin_Convertida'] = self.datos_filtrados['Hora Fin'].apply(convertir_hora_fin)
                self.datos_filtrados = self.datos_filtrados[self.datos_filtrados['Hora_Fin_Convertida'].notnull()]
                self.datos_filtrados = self.datos_filtrados[self.datos_filtrados['Hora_Fin_Convertida'] > ahora.time()]
                
                # Reiniciar paginación y mostrar datos actualizados
                self.pagina_actual = 1
                self.calcular_paginacion()
                self.mostrar_pagina_actual()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar clases pasadas: {str(e)}")
    
    def calcular_paginacion(self):
        """Calcula el número total de páginas"""
        total_items = len(self.datos_filtrados)
        self.total_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        
        # Asegurar que la página actual esté dentro del rango
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas
    
    def mostrar_pagina_actual(self):
        """Muestra los datos de la página actual en la tabla"""
        # Limpiar tabla
        for item in self.tree_clases.get_children():
            self.tree_clases.delete(item)
        
        if self.datos_filtrados.empty:
            self.actualizar_info_pagina()
            return
        
        # Calcular índices para la página actual
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        datos_pagina = self.datos_filtrados.iloc[inicio:fin]
        
        # Insertar datos en la tabla
        for _, fila in datos_pagina.iterrows():
            # Obtener documento (columna exacta: "Número de Documento")
            documento = str(fila.get('Número de Documento', ''))
            documento_limpio = limpiar_numero_documento(documento)
            
            # Obtener docente (columna exacta: "Docente")
            docente = str(fila.get('Docente', 'N/A'))
                
            # Obtener aula (columna exacta: "Aula")
            aula = str(fila.get('Aula', 'N/A'))
            
            # Obtener horario (columna exacta: "Horario")
            horario = str(fila.get('Horario', 'N/A'))
            
            # Obtener materia (columna exacta: "Materia de la Clase")
            materia = str(fila.get('Materia de la Clase', 'N/A'))
            
            self.tree_clases.insert('', 'end', values=(
                documento_limpio,
                docente,
                aula,
                horario,
                materia
            ))
        
        self.actualizar_info_pagina()
        self.actualizar_botones_navegacion()
    
    def actualizar_info_pagina(self):
        """Actualiza la información de paginación"""
        total_items = len(self.datos_filtrados)
        self.label_pagina.config(text=f"Página {self.pagina_actual} de {self.total_paginas} ({total_items} registros)")
    
    def actualizar_botones_navegacion(self):
        """Actualiza el estado de los botones de navegación"""
        # Botón anterior
        if self.pagina_actual <= 1:
            self.btn_anterior.config(state='disabled')
        else:
            self.btn_anterior.config(state='normal')
        
        # Botón siguiente
        if self.pagina_actual >= self.total_paginas:
            self.btn_siguiente.config(state='disabled')
        else:
            self.btn_siguiente.config(state='normal')
    
    def pagina_anterior(self):
        """Va a la página anterior"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.mostrar_pagina_actual()
    
    def pagina_siguiente(self):
        """Va a la página siguiente"""
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.mostrar_pagina_actual()
    
    def iniciar_actualizacion_automatica(self):
        """Inicia la actualización automática cada 10 minutos"""
        self.actualizar_automaticamente()
    
    def actualizar_automaticamente(self):
        """Actualiza los datos automáticamente y programa la próxima actualización"""
        try:
            # Solo actualizar si hay datos cargados y no se está buscando
            if (self.app.programacion is not None and 
                not self.app.programacion.empty and 
                not self.entry_busqueda.get().strip()):
                
                self.cargar_clases_del_dia()
                
        except Exception as e:
            print(f"Error en actualización automática: {str(e)}")

        # Programar la próxima actualización en 30 minutos (1,800,000 ms)
        self.auto_update_job = self.frame_entrega.after(1800000, self.actualizar_automaticamente)

    def detener_actualizacion_automatica(self):
        """Detiene la actualización automática"""
        if self.auto_update_job:
            self.frame_entrega.after_cancel(self.auto_update_job)
            self.auto_update_job = None