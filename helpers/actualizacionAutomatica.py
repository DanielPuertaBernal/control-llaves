class ActualizacionAutomatica:
    """
    Componente para manejar actualización automática y debounce de búsqueda
    Unifica patrones comunes entre diferentes vistas
    """
    
    def __init__(self, frame_parent, callback_actualizar, intervalo_ms=30000, debounce_ms=300):
        """
        Args:
            frame_parent: Frame padre para programar tareas
            callback_actualizar: Función a llamar para actualizar datos
            intervalo_ms: Intervalo de actualización automática en ms
            debounce_ms: Tiempo de espera para debounce en ms
        """
        self.frame_parent = frame_parent
        self.callback_actualizar = callback_actualizar
        self.intervalo_ms = intervalo_ms
        self.debounce_ms = debounce_ms
        
        # Jobs de temporizadores
        self.auto_update_job = None
        self.search_job = None
        
        # Estado
        self.activo = False
    
    # ============ ACTUALIZACIÓN AUTOMÁTICA ============
    
    def IniciarActualizacionAutomatica(self):
        """Inicia la actualización automática"""
        if not self.activo:
            self.activo = True
            self.ActualizarAutomaticamente()
    
    def ActualizarAutomaticamente(self):
        """Actualiza los datos automáticamente y programa la próxima actualización"""
        if not self.activo:
            return
            
        try:
            # Llamar al callback de actualización
            self.callback_actualizar()
            
        except Exception as e:
            print(f"Error en actualización automática: {str(e)}")
        
        # Programar la próxima actualización
        if self.activo:
            self.auto_update_job = self.frame_parent.after(
                self.intervalo_ms, 
                self.ActualizarAutomaticamente
            )
    
    def DetenerActualizacionAutomatica(self):
        """Detiene la actualización automática"""
        self.activo = False
        if self.auto_update_job:
            self.frame_parent.after_cancel(self.auto_update_job)
            self.auto_update_job = None
    
    def ForzarActualizacion(self):
        """Fuerza una actualización inmediata"""
        try:
            self.callback_actualizar()
        except Exception as e:
            print(f"Error en actualización forzada: {str(e)}")
    
    # ============ DEBOUNCE DE BÚSQUEDA ============
    
    def ConfigurarDebounce(self, callback_busqueda):
        """
        Configura el callback para búsqueda con debounce
        
        Args:
            callback_busqueda: Función a llamar para realizar búsqueda
        """
        self.callback_busqueda = callback_busqueda
    
    def OnCambioBusqueda(self, event=None):
        """
        Maneja el cambio en campo de búsqueda con debounce
        Usar este método en el evento KeyRelease del campo de búsqueda
        """
        # Cancelar búsqueda anterior si existe
        if self.search_job is not None:
            self.frame_parent.after_cancel(self.search_job)
        
        # Programar nueva búsqueda después del tiempo de debounce
        if hasattr(self, 'callback_busqueda'):
            self.search_job = self.frame_parent.after(
                self.debounce_ms, 
                self.callback_busqueda
            )
    
    def CancelarBusqueda(self):
        """Cancela la búsqueda pendiente"""
        if self.search_job is not None:
            self.frame_parent.after_cancel(self.search_job)
            self.search_job = None
    
    # ============ UTILIDADES ============
    
    def CambiarIntervalo(self, nuevo_intervalo_ms):
        """
        Cambia el intervalo de actualización automática
        
        Args:
            nuevo_intervalo_ms: Nuevo intervalo en milisegundos
        """
        self.intervalo_ms = nuevo_intervalo_ms
        
        # Si está activo, reiniciar con nuevo intervalo
        if self.activo:
            self.DetenerActualizacionAutomatica()
            self.IniciarActualizacionAutomatica()
    
    def CambiarDebounce(self, nuevo_debounce_ms):
        """
        Cambia el tiempo de debounce
        
        Args:
            nuevo_debounce_ms: Nuevo tiempo de debounce en milisegundos
        """
        self.debounce_ms = nuevo_debounce_ms
    
    def EstaActivo(self):
        """Retorna si la actualización automática está activa"""
        return self.activo
    
    def ObtenerEstado(self):
        """
        Retorna información del estado actual
        
        Returns:
            dict: Estado del componente
        """
        return {
            'activo': self.activo,
            'intervalo_ms': self.intervalo_ms,
            'debounce_ms': self.debounce_ms,
            'tiene_job_actualizacion': self.auto_update_job is not None,
            'tiene_job_busqueda': self.search_job is not None
        }


class UtilTablas:
    """
    Utilidades comunes para manejo de datos en tablas
    Unifica patrones de validación y manipulación de datos
    """
    
    @staticmethod
    def ValidarDatosVacios(datos):
        """
        Valida si los datos están vacíos usando múltiples métodos
        
        Args:
            datos: Datos a validar (DataFrame, lista, etc.)
            
        Returns:
            bool: True si están vacíos
        """
        if datos is None:
            return True
        
        # Para DataFrames de pandas
        if hasattr(datos, 'empty'):
            return datos.empty
        
        # Para listas y otros iterables
        if hasattr(datos, '__len__'):
            return len(datos) == 0
        
        return False
    
    @staticmethod
    def LimpiarTabla(treeview):
        """
        Limpia todos los elementos de un TreeView
        
        Args:
            treeview: Widget TreeView a limpiar
        """
        for item in treeview.get_children():
            treeview.delete(item)
    
    @staticmethod
    def ExtraerValorSeguro(fila, columna, valor_defecto='N/A'):
        """
        Extrae un valor de forma segura de una fila de datos
        
        Args:
            fila: Fila de datos (dict, Series, etc.)
            columna: Nombre de la columna
            valor_defecto: Valor por defecto si no existe
            
        Returns:
            str: Valor extraído como string
        """
        try:
            valor = fila.get(columna, valor_defecto)
            return str(valor) if valor is not None else valor_defecto
        except Exception:
            return valor_defecto
    
    @staticmethod
    def ConfigurarColorFila(treeview, item_id, tag, color_fondo, color_texto=None):
        """
        Configura el color de una fila en TreeView
        
        Args:
            treeview: Widget TreeView
            item_id: ID del item
            tag: Tag para aplicar
            color_fondo: Color de fondo
            color_texto: Color de texto (opcional)
        """
        try:
            # Configurar tag si no existe
            if color_texto:
                treeview.tag_configure(tag, background=color_fondo, foreground=color_texto)
            else:
                treeview.tag_configure(tag, background=color_fondo)
            
            # Aplicar tag al item
            treeview.set(item_id, tag)
        except Exception as e:
            print(f"Error configurando color de fila: {e}")
    
    @staticmethod
    def ObtenerTextoEstado(es_busqueda_activa, total_registros, texto_busqueda=""):
        """
        Genera texto de estado para mostrar información de la tabla
        
        Args:
            es_busqueda_activa: Si hay búsqueda activa
            total_registros: Total de registros
            texto_busqueda: Texto de búsqueda actual
            
        Returns:
            str: Texto de estado
        """
        if es_busqueda_activa and texto_busqueda:
            return f"Mostrando {total_registros} resultado(s) para '{texto_busqueda}'"
        else:
            return f"Total: {total_registros} registro(s)"