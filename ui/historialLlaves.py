from tkinter import ttk
from helpers.gestionExcel import (ObtenerLlavesPendientes, RegistrarDevolucion)
from helpers.busquedaTabla import BusquedaTabla
from helpers.paginacionTabla import PaginacionTabla
from helpers.actualizacionAutomatica import ActualizacionAutomatica, UtilTablas
from helpers.accionesTabla import AccionesTabla, ConfirmadorAcciones
from helpers.configuracionTablas import ConfiguracionTablas
import pandas as pd

class VistaHistorialLlaves:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_historial = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_historial, text="📋 Llaves en Préstamo")
        
        # Variables para datos
        self.datos_historial = []
        self.datos_filtrados = []
        
        # Instanciar componente de búsqueda reutilizable
        self.buscador = BusquedaTabla()
        
        # Instanciar componente de paginación reutilizable
        self.paginador = PaginacionTabla(items_por_pagina=20)
        
        # Instanciar componente de actualización automática
        self.actualizador = ActualizacionAutomatica(
            frame_parent=self.frame_historial,
            callback_actualizar=self._ActualizarSiNoHayBusqueda,
            intervalo_ms=30000,  # 30 segundos
            debounce_ms=300      # 300ms de debounce
        )
        
        # Instanciar componente de acciones de tabla
        self.gestor_acciones = None  # Se inicializará después de crear la tabla
        
        self.CrearVistaHistorial()
        self.CargarHistorial()
        self.actualizador.IniciarActualizacionAutomatica()

    def CrearVistaHistorial(self):
        # Título
        titulo = ttk.Label(self.frame_historial, 
                          text="LLAVES ACTUALMENTE EN PRÉSTAMO", 
                          font=('Segoe UI', 16, 'bold'))
        titulo.pack(pady=(0, 20))

        # Frame para búsqueda y botones
        frame_controles = ttk.Frame(self.frame_historial)
        frame_controles.pack(fill='x', pady=(0, 20))
        
        # Campo de búsqueda
        ttk.Label(frame_controles, text="Buscar:").pack(side='left', padx=(0, 5))
        self.entry_busqueda = ttk.Entry(frame_controles, width=40)
        self.entry_busqueda.pack(side='left', padx=(0, 10))
        
        # Configurar debounce de búsqueda usando el componente
        self.actualizador.ConfigurarDebounce(self.AplicarFiltros)
        self.entry_busqueda.bind('<KeyRelease>', self.actualizador.OnCambioBusqueda)
        
        # Botón actualizar
        btn_actualizar = ttk.Button(frame_controles, text="🔄 Actualizar", 
                                   command=self.actualizador.ForzarActualizacion)
        btn_actualizar.pack(side='left')

        # Frame para paginación (movido arriba de la tabla)
        frame_paginacion = ttk.Frame(self.frame_historial)
        frame_paginacion.pack(fill='x', pady=(0, 10))
        
        # Crear widgets de paginación usando el componente
        self.paginador.CrearWidgetsPaginacion(frame_paginacion)
        
        # Configurar callback para mostrar datos
        self.paginador.ConfigurarCallback(self.MostrarDatosEnTabla)

        # Frame para la tabla
        frame_tabla = ttk.Frame(self.frame_historial)
        frame_tabla.pack(fill='both', expand=True, pady=(0, 20))

        # Crear Treeview usando configuración centralizada
        self.tree_historial = ttk.Treeview(frame_tabla)
        ConfiguracionTablas.ConfigurarTreeview(self.tree_historial, 'historial')
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_historial.yview)
        scrollbar_h = ttk.Scrollbar(frame_tabla, orient='horizontal', command=self.tree_historial.xview)
        self.tree_historial.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Posicionar tabla y scrollbars
        self.tree_historial.pack(side='left', fill='both', expand=True)
        scrollbar_v.pack(side='right', fill='y')
        scrollbar_h.pack(side='bottom', fill='x')
        
        # Evento doble clic para devolver llave
        # self.tree_historial.bind('<Double-1>', self.ConfirmarDevolucion)
        
        # Configurar gestor de acciones de tabla
        self.gestor_acciones = AccionesTabla(
            treeview=self.tree_historial,
            callback_accion=self._ProcesarDevolucionLlave,
            callback_recarga=self._RecargarDespuesDeAccion
        )

    def CargarHistorial(self):
        """Carga los datos del historial - SOLO llaves en préstamo"""
        try:
            # Obtener solo las llaves que están en préstamo (sin fecha de devolución)
            self.datos_historial = ObtenerLlavesPendientes()
            
            self.AplicarFiltros()
            
        except Exception as e:
            ConfirmadorAcciones.MostrarError(f"Error al cargar historial: {str(e)}")
            self.datos_historial = []
            self.datos_filtrados = []
            self.paginador.ActualizarDatos([])

    def AplicarFiltros(self):
        """Aplica filtros de búsqueda usando el componente de búsqueda"""
        termino = self.entry_busqueda.get().strip()
        
        if not termino:
            self.datos_filtrados = self.datos_historial.copy()
        else:
            # Convertir lista de diccionarios a DataFrame para usar el componente de búsqueda
            if self.datos_historial:
                df_historial = pd.DataFrame(self.datos_historial)
                
                # Usar el componente de búsqueda para filtrar
                df_filtrado = self.buscador.BuscarEnDataFrame(df_historial, termino)
                
                # Convertir de vuelta a lista de diccionarios
                self.datos_filtrados = df_filtrado.to_dict('records')
            else:
                self.datos_filtrados = []
        
        # Actualizar paginación con nuevos datos
        self.paginador.ActualizarDatos(self.datos_filtrados)

    def _ActualizarSiNoHayBusqueda(self):
        """Callback para actualización automática - solo actualiza si no hay búsqueda activa"""
        try:
            # Solo actualizar si no hay filtros de búsqueda activos
            if not self.entry_busqueda.get().strip():
                self.CargarHistorial()
        except Exception:
            pass  # Error silencioso
    
    def MostrarDatosEnTabla(self, datos_pagina, inicio, fin):
        """
        Callback para mostrar datos en la tabla (usado por el componente de paginación)
        
        Args:
            datos_pagina: Lista con los datos de la página actual
            inicio: Índice de inicio
            fin: Índice de fin
        """
        # Limpiar tabla usando utilidad
        UtilTablas.LimpiarTabla(self.tree_historial)
        
        # Validar datos vacíos usando utilidad
        if UtilTablas.ValidarDatosVacios(datos_pagina):
            return
        
        # Mostrar datos de la página actual
        for registro in datos_pagina:
            documento = UtilTablas.ExtraerValorSeguro(registro, 'Número de Documento')
            docente = UtilTablas.ExtraerValorSeguro(registro, 'Docente')
            horario = UtilTablas.ExtraerValorSeguro(registro, 'Horario')
            aula = UtilTablas.ExtraerValorSeguro(registro, 'Aula')
            materia = UtilTablas.ExtraerValorSeguro(registro, 'Materia de la Clase')
            fecha_entrega = UtilTablas.ExtraerValorSeguro(registro, 'Fecha de entrega')
            hora_entrega = UtilTablas.ExtraerValorSeguro(registro, 'Hora de entrega')
            
            # Insertar con fondo de color para destacar que están en préstamo
            item_id = self.tree_historial.insert('', 'end', 
                values=(documento, docente, horario, aula, materia, fecha_entrega, hora_entrega),
                tags=('prestamo',))
        
        # Configurar estilos usando configuración centralizada
        ConfiguracionTablas.ConfigurarEstilosTabla(self.tree_historial, 'historial')

    # ============ CALLBACKS PARA ACCIONES DE TABLA ============
    
    def _ProcesarDevolucionLlave(self, valores):
        """
        Procesa la devolución de llave (callback para AccionesTabla)
        
        Args:
            valores: Tupla con los valores de la fila seleccionada
            
        Returns:
            bool: True si la acción fue exitosa
        """
        try:
            documento = valores[0]
            docente = valores[1]
            
            # Confirmar la acción con el usuario
            if ConfirmadorAcciones.ConfirmarDevolucionLlave(documento, docente):
                # Registrar devolución
                if RegistrarDevolucion(documento):
                    return True  # Éxito
                else:
                    ConfirmadorAcciones.MostrarError("No se pudo registrar la devolución.")
                    return False
            
            return False  # Usuario canceló
            
        except Exception as e:
            ConfirmadorAcciones.MostrarError(f"Error al procesar devolución: {str(e)}")
            return False
    
    def _RecargarDespuesDeAccion(self):
        """Recarga los datos después de una acción exitosa"""
        try:
            # Recargar historial (el registro desaparecerá porque ya no está "Entregado")
            self.CargarHistorial()
            
            # Actualizar vista entrega si existe
            if hasattr(self.app, 'vista_entrega') and hasattr(self.app.vista_entrega, 'CargarClasesDelDia'):
                try:
                    # Invalidar cache de la vista de entrega
                    self.app.vista_entrega.buscador.InvalidarCache()
                    # Recargar datos de la vista de entrega
                    busqueda_texto = self.app.vista_entrega.entry_busqueda.get().strip()
                    if busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio...":
                        self.app.vista_entrega.BuscarPorDocumento()
                    else:
                        self.app.vista_entrega.CargarClasesDelDia()
                except Exception:
                    pass  # Error silencioso
                    
        except Exception as e:
            print(f"Error recargando después de acción: {e}")