""">
Vista de historial de llaves
Maneja solo la presentación del historial de préstamos
"""
from tkinter import ttk, messagebox
from controllers import HistorialController, LlaveController
from presentation.components import PaginacionComponent, TablaComponent, BuscadorComponent


class HistorialView:
    """Vista para historial de llaves en préstamo"""
    
    def __init__(self, parent_frame, historial_controller: HistorialController, llave_controller: LlaveController):
        self.historial_controller = historial_controller
        self.llave_controller = llave_controller
        
        # Servicios
        self.paginacion_service = PaginacionComponent(items_por_pagina=15)
        
        # Frame principal - ahora recibe el parent directamente
        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)
        
        # Datos
        self.datos_historial = []
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Cargar datos
        self.actualizar_datos()
        
        # Actualización automática cada 30 segundos
        self._iniciar_actualizacion_automatica()
    
    def _crear_interfaz(self):
        """Crea los componentes visuales"""
        # Componente de búsqueda
        self.buscador = BuscadorComponent(
            self.frame,
            callback_busqueda=self._realizar_busqueda,
            label_texto="Buscar:"
        )
        
        # Frame de paginación con botón actualizar
        frame_paginacion = ttk.Frame(self.frame)
        frame_paginacion.pack(fill='x', pady=(0, 15))
        
        # Botón actualizar a la izquierda
        btn_actualizar = ttk.Button(frame_paginacion, text="🔄 Actualizar", command=self.actualizar_datos)
        btn_actualizar.pack(side='left', padx=(0, 20))
        
        # Información de registros
        self.label_info = ttk.Label(frame_paginacion, text="0 registros", font=('Segoe UI', 9))
        self.label_info.pack(side='left')
        
        # Controles de paginación compactos a la derecha
        self.btn_siguiente = ttk.Button(frame_paginacion, text="▶", width=3, command=self._pagina_siguiente)
        self.btn_siguiente.pack(side='right', padx=(5, 0))
        
        self.label_pagina = ttk.Label(frame_paginacion, text="Página 1 de 1", font=('Segoe UI', 9))
        self.label_pagina.pack(side='right', padx=8)
        
        self.btn_anterior = ttk.Button(frame_paginacion, text="◀", width=3, command=self._pagina_anterior)
        self.btn_anterior.pack(side='right', padx=(0, 5))
        
        # Tabla
        frame_tabla = ttk.Frame(self.frame)
        frame_tabla.pack(fill='both', expand=True, pady=(0, 20))
        
        self.tree = ttk.Treeview(frame_tabla)
        TablaComponent.configurar_treeview(self.tree, 'historial')
        
        scrollbar_v = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(frame_tabla, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar_v.pack(side='right', fill='y')
        scrollbar_h.pack(side='bottom', fill='x')
        
        # Evento de doble clic para devolución
        self.tree.bind('<Double-1>', self._on_doble_click)
    
    def actualizar_datos(self):
        """Actualiza los datos del historial mostrando TODAS las llaves en préstamo"""
        # Usar el historial_controller que ya tiene inyectado
        llaves_pendientes = self.historial_controller.obtener_prestamos_activos()
        
        self.datos_historial = llaves_pendientes
        self.paginacion_service.actualizar_datos(llaves_pendientes)
        self._actualizar_vista()
    
    def _realizar_busqueda(self):
        """Filtra los datos según el término de búsqueda"""
        termino = self.buscador.obtener_termino()
        
        if not termino:
            # Sin búsqueda, mostrar todos los datos originales
            self.paginacion_service.actualizar_datos(self.datos_historial)
            self._actualizar_vista()
            return
        
        # Normalizar término de búsqueda
        termino_normalizado = self.buscador.normalizar_texto(termino)
        
        # Filtrar datos con normalización
        datos_filtrados = [
            llave for llave in self.datos_historial
            if (termino_normalizado in self.buscador.normalizar_texto(str(llave.get('documento', ''))) or
                termino_normalizado in self.buscador.normalizar_texto(str(llave.get('docente', ''))) or
                termino_normalizado in self.buscador.normalizar_texto(str(llave.get('aula', ''))))
        ]
        
        # Actualizar paginación con datos filtrados
        self.paginacion_service.actualizar_datos(datos_filtrados)
        self._actualizar_vista()
    
    def _pagina_anterior(self):
        """Va a página anterior"""
        self.paginacion_service.pagina_anterior()
        self._actualizar_vista()
    
    def _pagina_siguiente(self):
        """Va a página siguiente"""
        self.paginacion_service.pagina_siguiente()
        self._actualizar_vista()
    
    def _actualizar_vista(self):
        """Actualiza la vista"""
        datos_pagina, inicio, fin = self.paginacion_service.obtener_pagina_actual()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Llenar tabla con fecha_entrega
        if datos_pagina:
            for llave in datos_pagina:
                valores = (
                    llave.get('documento', ''),
                    llave.get('docente', ''),
                    llave.get('horario', ''),
                    llave.get('aula', ''),
                    llave.get('materia', ''),
                    llave.get('fecha_entrega', ''),
                    llave.get('hora_entrega', '')
                )
                self.tree.insert('', 'end', values=valores)
        
        # Actualizar labels
        info = self.paginacion_service.obtener_info_paginacion()
        self.label_pagina.config(text=f"Página {info['pagina_actual']} de {info['total_paginas']}")
        self.label_info.config(text=f"{info['total_items']} registros")
        
        self.btn_anterior.config(state='normal' if info['tiene_anterior'] else 'disabled')
        self.btn_siguiente.config(state='normal' if info['tiene_siguiente'] else 'disabled')
    
    def _on_doble_click(self, event):
        """Maneja doble clic para devolver llave"""
        try:
            seleccion = self.tree.selection()
            if not seleccion:
                return
            
            valores = self.tree.item(seleccion[0], 'values')
            
            # Confirmar devolución
            if not messagebox.askyesno(
                "Confirmar Devolución",
                f"¿Confirmar devolución de llave?\n\n"
                f"Docente: {valores[1]}\n"
                f"Documento: {valores[0]}"
            ):
                return
            
            # Procesar devolución - usar el llave_controller inyectado
            exito, mensaje = self.llave_controller.procesar_devolucion(valores[0], valores[1])
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.actualizar_datos()
            else:
                messagebox.showwarning("Advertencia", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar devolución: {str(e)}")
    
    def _iniciar_actualizacion_automatica(self):
        """Inicia actualización automática cada 30 segundos"""
        def actualizar():
            if not self.buscador.obtener_termino():
                self.actualizar_datos()
            self.frame.after(30000, actualizar)
        
        self.frame.after(30000, actualizar)
