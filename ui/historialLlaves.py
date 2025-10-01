from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from helpers.gestionExcel import (ObtenerLlavesPendientes, RegistrarDevolucion, 
                                 LimpiarNumeroDocumento)
from helpers.busquedaTabla import BusquedaTabla
from helpers.paginacionTabla import PaginacionTabla
import pandas as pd

class VistaHistorialLlaves:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_historial = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_historial, text="📋 Llaves en Préstamo")
        
        # Variables para datos
        self.datos_historial = []
        self.datos_filtrados = []
        
        # Variable para el temporizador de actualización automática
        self.auto_update_job = None
        
        # Instanciar componente de búsqueda reutilizable
        self.buscador = BusquedaTabla()
        
        # Instanciar componente de paginación reutilizable
        self.paginador = PaginacionTabla(items_por_pagina=20)
        
        self.CrearVistaHistorial()
        self.CargarHistorial()
        self.IniciarActualizacionAutomatica()

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
        self.entry_busqueda.bind('<KeyRelease>', self.OnBusquedaChanged)
        
        # Botón actualizar
        btn_actualizar = ttk.Button(frame_controles, text="🔄 Actualizar", 
                                   command=self.CargarHistorial)
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

        # Crear Treeview (incluyendo columna de horario)
        columnas = ('documento', 'docente', 'horario', 'aula', 'materia', 'fecha_entrega', 'hora_entrega')
        self.tree_historial = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)
        
        # Configurar encabezados (centrados)
        self.tree_historial.heading('documento', text='Documento', anchor='center')
        self.tree_historial.heading('docente', text='Docente', anchor='center')
        self.tree_historial.heading('horario', text='Horario', anchor='center')
        self.tree_historial.heading('aula', text='Aula', anchor='center')
        self.tree_historial.heading('materia', text='Materia', anchor='center')
        self.tree_historial.heading('fecha_entrega', text='Fecha Entrega', anchor='center')
        self.tree_historial.heading('hora_entrega', text='Hora Entrega', anchor='center')
        
        # Configurar anchos de columna y centrar contenido
        self.tree_historial.column('documento', width=120, anchor='center')
        self.tree_historial.column('docente', width=200, anchor='center')
        self.tree_historial.column('horario', width=150, anchor='center')
        self.tree_historial.column('aula', width=80, anchor='center')
        self.tree_historial.column('materia', width=180, anchor='center')
        self.tree_historial.column('fecha_entrega', width=120, anchor='center')
        self.tree_historial.column('hora_entrega', width=120, anchor='center')
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_historial.yview)
        scrollbar_h = ttk.Scrollbar(frame_tabla, orient='horizontal', command=self.tree_historial.xview)
        self.tree_historial.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Posicionar tabla y scrollbars
        self.tree_historial.pack(side='left', fill='both', expand=True)
        scrollbar_v.pack(side='right', fill='y')
        scrollbar_h.pack(side='bottom', fill='x')
        
        # Evento doble clic para devolver llave
        self.tree_historial.bind('<Double-1>', self.ConfirmarDevolucion)

    def CargarHistorial(self):
        """Carga los datos del historial - SOLO llaves en préstamo"""
        try:
            # Obtener solo las llaves que están en préstamo (sin fecha de devolución)
            self.datos_historial = ObtenerLlavesPendientes()
            
            self.AplicarFiltros()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")
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
    
    def MostrarDatosEnTabla(self, datos_pagina, inicio, fin):
        """
        Callback para mostrar datos en la tabla (usado por el componente de paginación)
        
        Args:
            datos_pagina: Lista con los datos de la página actual
            inicio: Índice de inicio
            fin: Índice de fin
        """
        # Limpiar tabla
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)
        
        if not datos_pagina:
            return
        
        # Mostrar datos de la página actual
        for registro in datos_pagina:
            documento = registro.get('Número de Documento', '')
            docente = registro.get('Docente', '')
            horario = registro.get('Horario', '')
            aula = registro.get('Aula', '')
            materia = registro.get('Materia de la Clase', '')
            fecha_entrega = registro.get('Fecha de entrega', '')
            hora_entrega = registro.get('Hora de entrega', '')
            
            # Insertar con fondo de color para destacar que están en préstamo
            item_id = self.tree_historial.insert('', 'end', 
                values=(documento, docente, horario, aula, materia, fecha_entrega, hora_entrega),
                tags=('prestamo',))
        
        # Configurar el color de fondo para items en préstamo
        self.tree_historial.tag_configure('prestamo', background='#FFF3CD', foreground='#856404')

    def OnBusquedaChanged(self, event):
        """Maneja el evento de cambio en el campo de búsqueda"""
        # Cancelar búsqueda anterior si existe
        if hasattr(self, 'search_job') and self.search_job:
            self.frame_historial.after_cancel(self.search_job)
        
        # Programar nueva búsqueda con retraso
        self.search_job = self.frame_historial.after(300, self.AplicarFiltros)

    def ConfirmarDevolucion(self, event):
        """Confirma la devolución de una llave"""
        try:
            # Obtener el item seleccionado
            item_seleccionado = self.tree_historial.selection()[0]
            valores = self.tree_historial.item(item_seleccionado, 'values')
            
            if not valores:
                return
            
            documento = valores[0]
            docente = valores[1]
            
            # Confirmar acción
            resultado = messagebox.askyesno(
                "Confirmar Devolución",
                f"¿Confirmar devolución de llave?\n\n"
                f"Docente: {docente}\n"
                f"Documento: {documento}\n\n"
                f"Se registrará la fecha y hora de devolución."
            )
            
            if resultado:
                # Registrar devolución
                if RegistrarDevolucion(documento):
                    
                    # Recargar historial (el registro desaparecerá porque ya no está "Entregado")
                    self.CargarHistorial()
                    
                    # *** ACTUALIZAR VISTA ENTREGA AUTOMÁTICAMENTE ***
                    if hasattr(self.app, 'vista_entrega') and hasattr(self.app.vista_entrega, 'CargarClasesDelDia'):
                        try:
                            # Invalidar cache de la vista de entrega usando el componente
                            self.app.vista_entrega.buscador.InvalidarCache()
                            # Recargar datos de la vista de entrega
                            busqueda_texto = self.app.vista_entrega.entry_busqueda.get().strip()
                            if busqueda_texto and busqueda_texto != "Ejemplo: 12345678 o A101 o Laboratorio...":
                                self.app.vista_entrega.BuscarPorDocumento()
                            else:
                                self.app.vista_entrega.CargarClasesDelDia()
                        except Exception:
                            pass  # Error silencioso si no se puede actualizar la vista de entrega
                else:
                    messagebox.showerror("Error", "No se pudo registrar la devolución.")
        
        except IndexError:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro de la tabla.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar devolución: {str(e)}")

    def IniciarActualizacionAutomatica(self):
        """Inicia actualización automática cada 30 segundos"""
        self.ActualizarAutomaticamente()

    def ActualizarAutomaticamente(self):
        """Actualiza datos automáticamente"""
        try:
            # Solo actualizar si no hay filtros de búsqueda activos
            if not self.entry_busqueda.get().strip():
                self.CargarHistorial()
        except Exception:
            pass  # Error silencioso
        finally:
            # Programar próxima actualización
            self.auto_update_job = self.frame_historial.after(30000, self.ActualizarAutomaticamente)

    def DetenerActualizacionAutomatica(self):
        """Detiene la actualización automática"""
        if self.auto_update_job:
            self.frame_historial.after_cancel(self.auto_update_job)
            self.auto_update_job = None