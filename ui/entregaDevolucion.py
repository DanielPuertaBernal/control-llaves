from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from datetime import datetime
import locale
from openpyxl import Workbook
from helpers.gestionExcel import (RegistrarEntrega, RegistrarDevolucion, 
                                 ObtenerLlavesPendientes, LimpiarNumeroDocumento, 
                                 ObtenerHistorialCompleto, VerificarLlaveEntregada)
from helpers.limpiezaProgramacion import LimpiarProgramacion

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
        
        # Variables para optimización de rendimiento
        self.search_job = None  # Para debounce en búsqueda
        self.cache_docentes_con_llaves = set()  # Cache de documentos con llaves entregadas
        self.cache_timestamp = None  # Timestamp del cache para invalidación
        self.cache_valid_duration = 10  # Cache válido por 10 segundos (reducido para mayor consistencia)
        
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
        
        ttk.Label(frame_busqueda, text="Buscar por Número de Documento o Salón:").pack(anchor='w', pady=(0, 5))
        
        self.entry_busqueda = ttk.Entry(frame_busqueda, font=('Segoe UI', 11))
        self.entry_busqueda.pack(fill='x')
        self.entry_busqueda.bind('<KeyRelease>', self.on_search_keyrelease)  # Cambiar a función de debounce
        
        # Frame para paginación (movido arriba de la tabla)
        frame_paginacion = ttk.Frame(self.frame_entrega)
        frame_paginacion.pack(fill='x', pady=(15, 10))
        
        self.btn_anterior = ttk.Button(frame_paginacion, text="◀ Anterior", 
                                      command=self.pagina_anterior, state='disabled')
        self.btn_anterior.pack(side='left')
        
        self.label_pagina = ttk.Label(frame_paginacion, text="Página 1 de 1")
        self.label_pagina.pack(side='left', padx=(20, 20))
        
        self.btn_siguiente = ttk.Button(frame_paginacion, text="Siguiente ▶", 
                                       command=self.pagina_siguiente, state='disabled')
        self.btn_siguiente.pack(side='left')
        
        # Información adicional
        self.label_info = ttk.Label(frame_paginacion, text="0 registros encontrados")
        self.label_info.pack(side='right', padx=(0, 5))
        
        # Botón actualizar al lado del paginador
        btn_actualizar = ttk.Button(frame_paginacion, text="🔄 Refrescar", 
                                   command=self.forzar_actualizacion)
        btn_actualizar.pack(side='right')
        
        # Frame para la tabla principal
        frame_tabla = ttk.Frame(self.frame_entrega)
        frame_tabla.pack(fill='both', expand=True, pady=(0, 15))

        # Configurar tabla con las columnas requeridas incluyendo el botón de confirmación
        columnas = ('Documento', 'Docente', 'Aula', 'Horario', 'Materia', 'Acción')
        self.tree_clases = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)
        
        # Configurar encabezados y anchos de columnas
        anchos = [120, 180, 80, 120, 200, 100]
        for col, ancho in zip(columnas, anchos):
            self.tree_clases.heading(col, text=col, anchor='center')  # Centrar encabezados
            self.tree_clases.column(col, width=ancho, anchor='center')  # Centrar contenido

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_clases.yview)
        self.tree_clases.configure(yscrollcommand=scrollbar.set)
        self.tree_clases.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Configurar evento de doble clic para confirmar entrega
        self.tree_clases.bind('<Double-1>', self.confirmar_entrega_llave)
        
        # También configurar evento de clic simple en la columna de Acción
        self.tree_clases.bind('<Button-1>', self.on_click_tabla)

        # Label de información de actualización automática
        self.label_auto_update = ttk.Label(self.frame_entrega, 
                                          text="⏰ Actualización automática cada 10 minutos | Cache 10 segundos", 
                                          font=('Segoe UI', 9), 
                                          foreground='gray')
        self.label_auto_update.pack(pady=(15, 0))

        # NO cargar datos iniciales aquí - se cargará después de que la programación esté disponible

    # ============ FUNCIONES PRINCIPALES ============
    
    def forzar_actualizacion(self):
        """Fuerza la actualización invalidando completamente el cache"""
        # Invalidar cache completamente
        self.cache_timestamp = None
        self.cache_docentes_con_llaves = set()
        
        # Recargar según el estado de búsqueda
        busqueda_texto = self.entry_busqueda.get().strip()
        if busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio...":
            self.buscar_por_documento()
        else:
            self.cargar_clases_del_dia()
    
    def cargar_clases_del_dia(self):
        """Carga y muestra las clases del día actual desde programacionLimpiaActual.xlsx"""
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
    
    def normalizar_busqueda_salon(self, texto):
        """Normaliza el texto para búsqueda de salones eliminando guiones y espacios"""
        if not texto:
            return ""
        # Convertir a minúsculas, eliminar guiones, espacios y otros caracteres especiales
        return texto.lower().replace('-', '').replace('_', '').replace(' ', '').strip()
    
    def buscar_por_documento(self, event=None):
        """Busca clases por número de documento del docente o por nombre del salón/aula"""
        termino = self.entry_busqueda.get().strip()
        
        # Ignorar el texto del placeholder
        if not termino or termino == "Ejemplo: 12345678 o A101 o Laboratorio...":
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
            
            # Verificar que existen las columnas necesarias
            columnas_requeridas = ['Número de Documento', 'Aula']
            columnas_faltantes = [col for col in columnas_requeridas if col not in datos_del_dia.columns]
            if columnas_faltantes:
                messagebox.showerror("Error", f"No se encontraron las columnas: {', '.join(columnas_faltantes)}")
                return
            
            # Limpiar números de documento y crear máscaras de búsqueda
            datos_del_dia['nroidenti_limpio'] = datos_del_dia['Número de Documento'].astype(str).apply(LimpiarNumeroDocumento)
            
            # Buscar por número de documento
            mascara_documento = datos_del_dia['nroidenti_limpio'].str.contains(termino, na=False, case=False)
            
            # Buscar por aula/salón con normalización mejorada
            termino_normalizado = self.normalizar_busqueda_salon(termino)
            
            # Crear columna temporal con aulas normalizadas para comparación
            datos_del_dia['aula_normalizada'] = datos_del_dia['Aula'].astype(str).apply(self.normalizar_busqueda_salon)
            
            # Buscar tanto en el aula original (para búsquedas exactas) como en la normalizada (para búsquedas flexibles)
            mascara_aula_exacta = datos_del_dia['Aula'].astype(str).str.contains(termino, na=False, case=False)
            mascara_aula_normalizada = datos_del_dia['aula_normalizada'].str.contains(termino_normalizado, na=False, case=False)
            mascara_aula = mascara_aula_exacta | mascara_aula_normalizada
            
            # Combinar ambas búsquedas con OR (cualquiera de las dos condiciones)
            mascara_combinada = mascara_documento | mascara_aula
            
            # Aplicar filtro combinado
            self.datos_filtrados = datos_del_dia[mascara_combinada].copy()
            
            # Limpiar columna temporal
            if 'aula_normalizada' in self.datos_filtrados.columns:
                self.datos_filtrados = self.datos_filtrados.drop('aula_normalizada', axis=1)
            
            # Ordenar por horario
            if 'Horario' in self.datos_filtrados.columns:
                self.datos_filtrados = self.datos_filtrados.sort_values(by='Horario')
            
            # *** IMPORTANTE: Aplicar filtros adicionales después de la búsqueda ***
            self.eliminar_clases_pasadas()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def eliminar_clases_pasadas(self):
        """Elimina de la tabla las clases que ya terminaron y las que ya tienen llaves entregadas."""
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
            
            # Filtrar clases cuyos docentes ya tienen llaves entregadas (OPTIMIZADO)
            if not self.datos_filtrados.empty and 'Número de Documento' in self.datos_filtrados.columns:
                # Actualizar cache de docentes con llaves entregadas
                self.actualizar_cache_docentes()
                
                # Usar vectorización para filtrar más eficientemente
                def docente_sin_llave(documento):
                    documento_limpio = LimpiarNumeroDocumento(str(documento))
                    return documento_limpio not in self.cache_docentes_con_llaves
                
                # Aplicar filtro vectorizado (mucho más rápido que un loop)
                mascara_sin_llaves = self.datos_filtrados['Número de Documento'].apply(docente_sin_llave)
                self.datos_filtrados = self.datos_filtrados[mascara_sin_llaves]
            
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
            documento_limpio = LimpiarNumeroDocumento(documento)
            
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
                materia,
                "🔑 Entregar"
            ))
        
        self.actualizar_info_pagina()
        self.actualizar_botones_navegacion()
    
    def actualizar_info_pagina(self):
        """Actualiza la información de paginación"""
        total_items = len(self.datos_filtrados)
        self.label_pagina.config(text=f"Página {self.pagina_actual} de {self.total_paginas}")
        self.label_info.config(text=f"{total_items} registros encontrados")
    
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
            busqueda_texto = self.entry_busqueda.get().strip()
            esta_buscando = busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio..."
            
            if (self.app.programacion is not None and 
                not self.app.programacion.empty and 
                not esta_buscando):
                
                # Invalidar cache antes de actualización automática
                self.cache_timestamp = None
                
                self.cargar_clases_del_dia()
                
        except Exception as e:
            print(f"Error en actualización automática: {str(e)}")

        # Programar la próxima actualización en 10 minutos (600,000 ms) - cambiado de 30 a 10 minutos
        self.auto_update_job = self.frame_entrega.after(600000, self.actualizar_automaticamente)

    def detener_actualizacion_automatica(self):
        """Detiene la actualización automática"""
        if self.auto_update_job:
            self.frame_entrega.after_cancel(self.auto_update_job)
            self.auto_update_job = None

    def on_entry_focus_in(self, event):
        """Maneja cuando el campo de búsqueda recibe el foco"""
        if self.entry_busqueda.get() == "Ejemplo: 12345678 o A101 o Laboratorio...":
            self.entry_busqueda.delete(0, tk.END)
            self.entry_busqueda.config(foreground='black')

    def on_entry_focus_out(self, event):
        """Maneja cuando el campo de búsqueda pierde el foco"""
        if not self.entry_busqueda.get():
            self.entry_busqueda.insert(0, "Ejemplo: 12345678 o A101 o Laboratorio...")
            self.entry_busqueda.config(foreground='gray')

    def on_search_keyrelease(self, event):
        """Implementa debounce para la búsqueda - retrasa la búsqueda hasta que el usuario pare de escribir"""
        # Cancelar búsqueda anterior si existe
        if self.search_job is not None:
            self.frame_entrega.after_cancel(self.search_job)
        
        # Programar nueva búsqueda después de 300ms de inactividad
        self.search_job = self.frame_entrega.after(300, self.buscar_por_documento)

    def actualizar_cache_docentes(self):
        """Actualiza el cache de docentes que tienen llaves entregadas"""
        try:
            ahora = datetime.now()
            
            # Verificar si el cache necesita actualización
            if (self.cache_timestamp is None or 
                (ahora - self.cache_timestamp).total_seconds() > self.cache_valid_duration):
                
                # Obtener lista de docentes con llaves pendientes (más eficiente que verificar uno por uno)
                llaves_pendientes = ObtenerLlavesPendientes()
                
                # Crear set con los documentos que tienen llaves entregadas
                self.cache_docentes_con_llaves = {
                    LimpiarNumeroDocumento(str(registro.get('Número de Documento', ''))) 
                    for registro in llaves_pendientes
                }
                
                # Actualizar timestamp del cache
                self.cache_timestamp = ahora
                
        except Exception as e:
            print(f"Error al actualizar cache de docentes: {e}")
            # En caso de error, limpiar cache para evitar datos incorrectos
            self.cache_docentes_con_llaves = set()

    def on_click_tabla(self, event):
        """Maneja el clic en la tabla para detectar clic en la columna de Acción"""
        try:
            # Identificar qué columna se clickeó
            columna = self.tree_clases.identify_column(event.x)
            item = self.tree_clases.identify_row(event.y)
            
            # Si es la columna 6 (Acción) y hay un item seleccionado
            if columna == '#6' and item:  # #6 corresponde a la columna "Acción"
                # Simular el evento de doble clic
                self.tree_clases.selection_set(item)
                self.confirmar_entrega_llave(event)
        except Exception as e:
            print(f"Error en click tabla: {e}")

    def confirmar_entrega_llave(self, event):
        """Confirma la entrega de llave al docente cuando se hace doble clic"""
        try:
            # Obtener el item seleccionado
            item_seleccionado = self.tree_clases.selection()[0]
            valores = self.tree_clases.item(item_seleccionado, 'values')
            
            if not valores:
                return
            
            # Extraer información del registro seleccionado
            documento = valores[0]
            docente = valores[1]
            aula = valores[2]
            horario = valores[3]
            materia = valores[4]
            
            # Obtener el día actual
            dia_numero = datetime.now().weekday()
            dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            dia_actual = dias_espanol[dia_numero]
            
            # Confirmar la acción con el usuario
            resultado = messagebox.askyesno(
                "Confirmar Entrega", 
                f"¿Confirmar entrega de llave para:\n\n"
                f"Docente: {docente}\n"
                f"Documento: {documento}\n"
                f"Aula: {aula}\n"
                f"Horario: {horario}\n"
                f"Materia: {materia}"
            )
            
            if resultado:
                # Preparar información para el registro
                info_clase = {
                    'nroidenti': documento,
                    'profesor': docente,
                    'dia': dia_actual,
                    'horario': horario,
                    'aula': aula,
                    'materia': materia
                }
                
                # Registrar la entrega
                if RegistrarEntrega(info_clase):
                    # *** INVALIDAR CACHE después de entrega exitosa ***
                    self.cache_timestamp = None  # Forzar actualización del cache en próxima consulta
                    
                    # *** NO eliminar individualmente - recargar datos completos para consistencia ***
                    # self.tree_clases.delete(item_seleccionado)  # COMENTADO: causa problemas
                    
                    # Recargar los datos completamente para mantener la consistencia
                    busqueda_texto = self.entry_busqueda.get().strip()
                    if busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio...":
                        self.buscar_por_documento()
                    else:
                        self.cargar_clases_del_dia()
                    
                    # *** ACTUALIZAR VISTA HISTORIAL AUTOMÁTICAMENTE ***
                    if hasattr(self.app, 'vista_historial') and hasattr(self.app.vista_historial, 'cargar_historial'):
                        try:
                            self.app.vista_historial.cargar_historial()
                        except Exception:
                            pass  # Error silencioso si no se puede actualizar el historial
                else:
                    messagebox.showerror("Error", "No se pudo registrar la entrega de la llave.\nEs posible que el docente ya tenga una llave entregada.")
        
        except IndexError:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro de la tabla primero.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al confirmar entrega: {str(e)}")