from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from datetime import datetime
import locale
from openpyxl import Workbook
from helpers.gestionExcel import (RegistrarEntrega, RegistrarDevolucion, 
                                 ObtenerLlavesPendientes, LimpiarNumeroDocumento, 
                                 ObtenerHistorialCompleto, VerificarLlaveEntregada)
from helpers.limpiezaProgramacion import LimpiarProgramacion
from helpers.busquedaTabla import BusquedaTabla

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
        
        # Variables para optimización de rendimiento - ELIMINAR cache local, usar componente
        self.search_job = None  # Para debounce en búsqueda
        
        # Instanciar componente de búsqueda reutilizable
        self.buscador = BusquedaTabla()
        
        self.CrearVistaEntregaDevolucion()
        self.IniciarActualizacionAutomatica()

    def CrearVistaEntregaDevolucion(self):
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
        self.entry_busqueda.bind('<KeyRelease>', self.OnSearchKeyrelease)  # Cambiar a función de debounce
        
        # Frame para paginación (movido arriba de la tabla)
        frame_paginacion = ttk.Frame(self.frame_entrega)
        frame_paginacion.pack(fill='x', pady=(15, 10))
        
        self.btn_anterior = ttk.Button(frame_paginacion, text="◀ Anterior", 
                                      command=self.PaginaAnterior, state='disabled')
        self.btn_anterior.pack(side='left')
        
        self.label_pagina = ttk.Label(frame_paginacion, text="Página 1 de 1")
        self.label_pagina.pack(side='left', padx=(20, 20))
        
        self.btn_siguiente = ttk.Button(frame_paginacion, text="Siguiente ▶", 
                                       command=self.PaginaSiguiente, state='disabled')
        self.btn_siguiente.pack(side='left')
        
        # Información adicional
        self.label_info = ttk.Label(frame_paginacion, text="0 registros encontrados")
        self.label_info.pack(side='right', padx=(0, 5))
        
        # Botón actualizar al lado del paginador
        btn_actualizar = ttk.Button(frame_paginacion, text="🔄 Refrescar", 
                                   command=self.ForzarActualizacion)
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
        self.tree_clases.bind('<Double-1>', self.ConfirmarEntregaLlave)
        
        # También configurar evento de clic simple en la columna de Acción
        self.tree_clases.bind('<Button-1>', self.OnClickTabla)

        # Label de información de actualización automática
        self.label_auto_update = ttk.Label(self.frame_entrega, 
                                          text="⏰ Actualización automática cada 10 minutos | Cache 10 segundos", 
                                          font=('Segoe UI', 9), 
                                          foreground='gray')
        self.label_auto_update.pack(pady=(15, 0))

        # NO cargar datos iniciales aquí - se cargará después de que la programación esté disponible

    # ============ FUNCIONES PRINCIPALES ============
    
    def ForzarActualizacion(self):
        """Fuerza la actualización invalidando completamente el cache"""
        # Invalidar cache del componente de búsqueda
        self.buscador.InvalidarCache()
        
        # Recargar según el estado de búsqueda
        busqueda_texto = self.entry_busqueda.get().strip()
        if busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio...":
            self.BuscarPorDocumento()
        else:
            self.CargarClasesDelDia()
    
    def CargarClasesDelDia(self):
        """Carga y muestra las clases del día actual desde programacionLimpiaActual.xlsx"""
        if self.app.programacion is None or self.app.programacion.empty:
            messagebox.showwarning("Advertencia", 
                                 "No hay programación cargada. Por favor, cargue la programación primero.")
            return

        try:
            # Usar el componente de búsqueda para filtrar por día actual
            df = self.app.programacion
            self.datos_filtrados = self.buscador.FiltrarPorDiaActual(df)
            
            # Actualizar label del día
            dia_numero = datetime.now().weekday()
            dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            dia_actual = dias_espanol[dia_numero]
            self.label_dia.config(text=f"CLASES DEL DÍA: {dia_actual}")
            
            # Aplicar filtros adicionales
            self.datos_filtrados = self.buscador.OrdenarPorHorario(self.datos_filtrados)
            self.datos_filtrados = self.buscador.EliminarClasesPasadas(self.datos_filtrados)
            self.datos_filtrados = self.buscador.FiltrarDocentesSinLlaves(self.datos_filtrados)
            
            # Reiniciar paginación y mostrar datos
            self.pagina_actual = 1
            self.CalcularPaginacion()
            self.MostrarPaginaActual()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar las clases del día: {str(e)}")
    
    def BuscarPorDocumento(self, event=None):
        """Busca clases por número de documento del docente o por nombre del salón/aula"""
        termino = self.entry_busqueda.get().strip()
        
        # Ignorar el texto del placeholder
        if not termino or termino == "Ejemplo: 12345678 o A101 o Laboratorio...":
            # Si no hay término, mostrar todas las clases del día
            self.CargarClasesDelDia()
            return
        
        if self.app.programacion is None or self.app.programacion.empty:
            messagebox.showwarning("Advertencia", 
                                 "No hay programación cargada. Por favor, cargue la programación primero.")
            return
        
        try:
            # Usar el componente de búsqueda para filtrar por día actual
            df = self.app.programacion
            datos_del_dia = self.buscador.FiltrarPorDiaActual(df)
            
            # Usar el componente de búsqueda para buscar por término
            self.datos_filtrados = self.buscador.BuscarEnDataFrame(datos_del_dia, termino)
            
            # Aplicar filtros adicionales
            self.datos_filtrados = self.buscador.OrdenarPorHorario(self.datos_filtrados)
            self.datos_filtrados = self.buscador.EliminarClasesPasadas(self.datos_filtrados)
            self.datos_filtrados = self.buscador.FiltrarDocentesSinLlaves(self.datos_filtrados)
            
            # Reiniciar paginación y mostrar datos
            self.pagina_actual = 1
            self.CalcularPaginacion()
            self.MostrarPaginaActual()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def CalcularPaginacion(self):
        """Calcula el número total de páginas"""
        total_items = len(self.datos_filtrados)
        self.total_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        
        # Asegurar que la página actual esté dentro del rango
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas
    
    def MostrarPaginaActual(self):
        """Muestra los datos de la página actual en la tabla"""
        # Limpiar tabla
        for item in self.tree_clases.get_children():
            self.tree_clases.delete(item)
        
        if self.datos_filtrados.empty:
            self.ActualizarInfoPagina()
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
        
        self.ActualizarInfoPagina()
        self.ActualizarBotonesNavegacion()
    
    def ActualizarInfoPagina(self):
        """Actualiza la información de paginación"""
        total_items = len(self.datos_filtrados)
        self.label_pagina.config(text=f"Página {self.pagina_actual} de {self.total_paginas}")
        self.label_info.config(text=f"{total_items} registros encontrados")
    
    def ActualizarBotonesNavegacion(self):
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
    
    def PaginaAnterior(self):
        """Va a la página anterior"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.MostrarPaginaActual()
    
    def PaginaSiguiente(self):
        """Va a la página siguiente"""
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.MostrarPaginaActual()
    
    def IniciarActualizacionAutomatica(self):
        """Inicia la actualización automática cada 10 minutos"""
        self.ActualizarAutomaticamente()
    
    def ActualizarAutomaticamente(self):
        """Actualiza los datos automáticamente y programa la próxima actualización"""
        try:
            # Solo actualizar si hay datos cargados y no se está buscando
            busqueda_texto = self.entry_busqueda.get().strip()
            esta_buscando = busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio..."
            
            if (self.app.programacion is not None and 
                not self.app.programacion.empty and 
                not esta_buscando):
                
                # Invalidar cache antes de actualización automática
                self.buscador.InvalidarCache()
                
                self.CargarClasesDelDia()
                
        except Exception as e:
            print(f"Error en actualización automática: {str(e)}")

        # Programar la próxima actualización en 10 minutos (600,000 ms) - cambiado de 30 a 10 minutos
        self.auto_update_job = self.frame_entrega.after(600000, self.ActualizarAutomaticamente)

    def DetenerActualizacionAutomatica(self):
        """Detiene la actualización automática"""
        if self.auto_update_job:
            self.frame_entrega.after_cancel(self.auto_update_job)
            self.auto_update_job = None

    def OnEntryFocusIn(self, event):
        """Maneja cuando el campo de búsqueda recibe el foco"""
        if self.entry_busqueda.get() == "Ejemplo: 12345678 o A101 o Laboratorio...":
            self.entry_busqueda.delete(0, tk.END)
            self.entry_busqueda.config(foreground='black')

    def OnEntryFocusOut(self, event):
        """Maneja cuando el campo de búsqueda pierde el foco"""
        if not self.entry_busqueda.get():
            self.entry_busqueda.insert(0, "Ejemplo: 12345678 o A101 o Laboratorio...")
            self.entry_busqueda.config(foreground='gray')

    def OnSearchKeyrelease(self, event):
        """Implementa debounce para la búsqueda - retrasa la búsqueda hasta que el usuario pare de escribir"""
        # Cancelar búsqueda anterior si existe
        if self.search_job is not None:
            self.frame_entrega.after_cancel(self.search_job)
        
        # Programar nueva búsqueda después de 300ms de inactividad
        self.search_job = self.frame_entrega.after(300, self.BuscarPorDocumento)

    def OnClickTabla(self, event):
        """Maneja el clic en la tabla para detectar clic en la columna de Acción"""
        try:
            # Identificar qué columna se clickeó
            columna = self.tree_clases.identify_column(event.x)
            item = self.tree_clases.identify_row(event.y)
            
            # Si es la columna 6 (Acción) y hay un item seleccionado
            if columna == '#6' and item:  # #6 corresponde a la columna "Acción"
                # Simular el evento de doble clic
                self.tree_clases.selection_set(item)
                self.ConfirmarEntregaLlave(event)
        except Exception as e:
            print(f"Error en click tabla: {e}")

    def ConfirmarEntregaLlave(self, event):
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
                    self.buscador.InvalidarCache()  # Usar el componente de búsqueda
                    
                    # Recargar los datos completamente para mantener la consistencia
                    busqueda_texto = self.entry_busqueda.get().strip()
                    if busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio...":
                        self.BuscarPorDocumento()
                    else:
                        self.CargarClasesDelDia()
                    
                    # *** ACTUALIZAR VISTA HISTORIAL AUTOMÁTICAMENTE ***
                    if hasattr(self.app, 'vista_historial') and hasattr(self.app.vista_historial, 'cargar_historial'):
                        try:
                            self.app.vista_historial.CargarHistorial()
                        except Exception:
                            pass  # Error silencioso si no se puede actualizar el historial
                else:
                    messagebox.showerror("Error", "No se pudo registrar la entrega de la llave.\nEs posible que el docente ya tenga una llave entregada.")
        
        except IndexError:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro de la tabla primero.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al confirmar entrega: {str(e)}")