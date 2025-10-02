from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from helpers.gestionExcel import (RegistrarEntrega, LimpiarNumeroDocumento)
from helpers.busquedaTabla import BusquedaTabla
from helpers.paginacionTabla import PaginacionTabla
from helpers.actualizacionAutomatica import ActualizacionAutomatica, UtilTablas
from helpers.accionesTabla import AccionesTabla, ConfirmadorAcciones

class VistaEntregaDevolucion:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_entrega = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_entrega, text="🔑 Devolución de Llaves")
        
        # Instanciar componente de búsqueda reutilizable
        self.buscador = BusquedaTabla()
        
        # Instanciar componente de paginación reutilizable
        self.paginador = PaginacionTabla(items_por_pagina=15)
        
        # Instanciar componente de actualización automática
        self.actualizador = ActualizacionAutomatica(
            frame_parent=self.frame_entrega,
            callback_actualizar=self._ActualizarSiNoHayBusqueda,
            intervalo_ms=600000,  # 10 minutos
            debounce_ms=300       # 300ms de debounce
        )
        
        # Instanciar componente de acciones de tabla
        self.gestor_acciones = None  # Se inicializará después de crear la tabla
        
        self.CrearVistaEntregaDevolucion()
        self.actualizador.IniciarActualizacionAutomatica()

    def CrearVistaEntregaDevolucion(self):
        # Título único que incluye el día
        dia_actual = self._ObtenerDiaActual()
        
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
        
        # Configurar debounce de búsqueda usando el componente
        self.actualizador.ConfigurarDebounce(self.BuscarPorDocumento)
        self.entry_busqueda.bind('<KeyRelease>', self.actualizador.OnCambioBusqueda)
        
        # Frame para paginación (movido arriba de la tabla)
        frame_paginacion = ttk.Frame(self.frame_entrega)
        frame_paginacion.pack(fill='x', pady=(15, 10))
        
        # Crear widgets de paginación usando el componente
        self.paginador.CrearWidgetsPaginacion(frame_paginacion)
        
        # Configurar callback para mostrar datos
        self.paginador.ConfigurarCallback(self.MostrarDatosEnTabla)
        
        # Botón actualizar al lado del paginador
        btn_actualizar = ttk.Button(frame_paginacion, text="🔄 Refrescar", 
                                   command=self.actualizador.ForzarActualizacion)
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
        # self.tree_clases.bind('<Double-1>', self.ConfirmarEntregaLlave)
        
        # También configurar evento de clic simple en la columna de Acción
        # self.tree_clases.bind('<Button-1>', self.OnClickTabla)
        
        # Configurar gestor de acciones de tabla
        self.gestor_acciones = AccionesTabla(
            treeview=self.tree_clases,
            callback_accion=self._ProcesarEntregaLlave,
            callback_recarga=self._RecargarDespuesDeAccion
        )

        # Label de información de actualización automática
        self.label_auto_update = ttk.Label(self.frame_entrega, 
                                          text="⏰ Actualización automática cada 10 minutos | Cache 10 segundos", 
                                          font=('Segoe UI', 9), 
                                          foreground='gray')
        self.label_auto_update.pack(pady=(15, 0))

        # NO cargar datos iniciales aquí - se cargará después de que la programación esté disponible

    # ============ FUNCIONES PRINCIPALES ============
    
    def _ObtenerDiaActual(self):
        """Obtiene el día actual en español"""
        dia_numero = datetime.now().weekday()  # 0=Monday, 6=Sunday
        dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        return dias_espanol[dia_numero]
    
    def _ActualizarSiNoHayBusqueda(self):
        """Callback para actualización automática - solo actualiza si no hay búsqueda activa"""
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
            dia_actual = self._ObtenerDiaActual()
            self.label_dia.config(text=f"CLASES DEL DÍA: {dia_actual}")
            
            # Aplicar filtros adicionales
            self.datos_filtrados = self.buscador.OrdenarPorHorario(self.datos_filtrados)
            self.datos_filtrados = self.buscador.EliminarClasesPasadas(self.datos_filtrados)
            self.datos_filtrados = self.buscador.FiltrarDocentesSinLlaves(self.datos_filtrados)
            
            # Actualizar paginación con nuevos datos
            self.paginador.ActualizarDatos(self.datos_filtrados)
            
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
            
            # Actualizar paginación con nuevos datos
            self.paginador.ActualizarDatos(self.datos_filtrados)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def MostrarDatosEnTabla(self, datos_pagina, inicio, fin):
        """
        Callback para mostrar datos en la tabla (usado por el componente de paginación)
        
        Args:
            datos_pagina: DataFrame con los datos de la página actual
            inicio: Índice de inicio
            fin: Índice de fin
        """
        # Limpiar tabla usando utilidad
        UtilTablas.LimpiarTabla(self.tree_clases)
        
        # Validar datos vacíos usando utilidad
        if UtilTablas.ValidarDatosVacios(datos_pagina):
            return
        
        try:
            # Insertar datos en la tabla
            for _, fila in datos_pagina.iterrows():
                # Usar utilidades para extraer valores de forma segura
                documento = UtilTablas.ExtraerValorSeguro(fila, 'Número de Documento')
                documento_limpio = LimpiarNumeroDocumento(documento)
                
                docente = UtilTablas.ExtraerValorSeguro(fila, 'Docente')
                aula = UtilTablas.ExtraerValorSeguro(fila, 'Aula')
                horario = UtilTablas.ExtraerValorSeguro(fila, 'Horario')
                materia = UtilTablas.ExtraerValorSeguro(fila, 'Materia de la Clase')
                
                self.tree_clases.insert('', 'end', values=(
                    documento_limpio,
                    docente,
                    aula,
                    horario,
                    materia,
                    "🔑 Entregar"
                ))
        except Exception as e:
            print(f"Error al mostrar datos en tabla: {e}")
            # En caso de error, simplemente no mostrar datos
    
    # ============ CALLBACKS PARA ACCIONES DE TABLA ============
    
    def _ProcesarEntregaLlave(self, valores):
        """
        Procesa la entrega de llave (callback para AccionesTabla)
        
        Args:
            valores: Tupla con los valores de la fila seleccionada
            
        Returns:
            bool: True si la acción fue exitosa
        """
        try:
            # Extraer información del registro seleccionado
            documento = valores[0]
            docente = valores[1]
            aula = valores[2]
            horario = valores[3]
            materia = valores[4]
            
            # Confirmar la acción con el usuario
            if ConfirmadorAcciones.ConfirmarEntregaLlave(documento, docente, aula, horario, materia):
                # Obtener el día actual
                dia_actual = self._ObtenerDiaActual()
                
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
                    return True  # Éxito
                else:
                    ConfirmadorAcciones.MostrarError(
                        "No se pudo registrar la entrega de la llave.\n"
                        "Es posible que el docente ya tenga una llave entregada."
                    )
                    return False
            
            return False  # Usuario canceló
            
        except Exception as e:
            ConfirmadorAcciones.MostrarError(f"Error al confirmar entrega: {str(e)}")
            return False
    
    def _RecargarDespuesDeAccion(self):
        """Recarga los datos después de una acción exitosa"""
        try:
            # Invalidar cache
            self.buscador.InvalidarCache()
            
            # Recargar datos según el estado de búsqueda
            busqueda_texto = self.entry_busqueda.get().strip()
            if busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio...":
                self.BuscarPorDocumento()
            else:
                self.CargarClasesDelDia()
            
            # Actualizar vista historial si existe
            if hasattr(self.app, 'vista_historial') and hasattr(self.app.vista_historial, 'CargarHistorial'):
                try:
                    self.app.vista_historial.CargarHistorial()
                except Exception:
                    pass  # Error silencioso
                    
        except Exception as e:
            print(f"Error recargando después de acción: {e}")
    
    def OnClickTabla(self, event):
        """MÉTODO LEGACY - mantenido por compatibilidad, usar gestor_acciones"""
        # Este método ahora es manejado por AccionesTabla
        pass

    def ConfirmarEntregaLlave(self, event):
        """MÉTODO LEGACY - mantenido por compatibilidad, usar gestor_acciones"""
        # Este método ahora es manejado por AccionesTabla y _ProcesarEntregaLlave
        pass