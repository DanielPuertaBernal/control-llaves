class ConfiguracionTablas:
    """
    Configuración centralizada para las tablas del sistema
    Define columnas, anchos y comportamientos estándar
    """
    
    # Configuración para la tabla de entrega/devolución de llaves
    TABLA_ENTREGA_LLAVES = {
        'columnas': ('Documento', 'Docente', 'Aula', 'Horario', 'Materia'),
        'anchos': [120, 180, 80, 120, 200],
        'alineacion': 'center',
        'altura': 15
    }
    
    # Configuración para la tabla de historial/llaves en préstamo
    TABLA_HISTORIAL_LLAVES = {
        'columnas': ('documento', 'docente', 'horario', 'aula', 'materia', 'fecha_entrega', 'hora_entrega'),
        'nombres_mostrar': ('Documento', 'Docente', 'Horario', 'Aula', 'Materia', 'Fecha Entrega', 'Hora Entrega'),
        'anchos': [120, 180, 150, 80, 180, 120, 120],
        'alineacion': 'center',
        'altura': 15,
        'tag_prestamo': 'prestamo',
        'color_fondo_prestamo': '#FFF3CD',
        'color_texto_prestamo': '#856404'
    }
    
    @classmethod
    def ConfigurarTreeview(cls, treeview, tipo_tabla):
        """
        Configura un Treeview con la configuración especificada
        
        Args:
            treeview: Widget Treeview a configurar
            tipo_tabla (str): Tipo de tabla ('entrega' o 'historial')
        """
        if tipo_tabla == 'entrega':
            config = cls.TABLA_ENTREGA_LLAVES
        elif tipo_tabla == 'historial':
            config = cls.TABLA_HISTORIAL_LLAVES
        else:
            raise ValueError(f"Tipo de tabla no válido: {tipo_tabla}")
        
        # Configurar columnas
        columnas = config['columnas']
        treeview.configure(columns=columnas, show='headings', height=config['altura'])
        
        # Configurar encabezados y anchos
        nombres_mostrar = config.get('nombres_mostrar', columnas)
        anchos = config['anchos']
        alineacion = config['alineacion']
        
        for col, nombre, ancho in zip(columnas, nombres_mostrar, anchos):
            treeview.heading(col, text=nombre, anchor=alineacion)
            treeview.column(col, width=ancho, anchor=alineacion)
    
    @classmethod
    def ConfigurarEstilosTabla(cls, treeview, tipo_tabla):
        """
        Configura los estilos específicos de una tabla
        
        Args:
            treeview: Widget Treeview
            tipo_tabla (str): Tipo de tabla ('entrega' o 'historial')
        """
        if tipo_tabla == 'historial':
            config = cls.TABLA_HISTORIAL_LLAVES
            treeview.tag_configure(
                config['tag_prestamo'], 
                background=config['color_fondo_prestamo'], 
                foreground=config['color_texto_prestamo']
            )
    
    @classmethod
    def ObtenerConfiguracion(cls, tipo_tabla):
        """
        Obtiene la configuración completa para un tipo de tabla
        
        Args:
            tipo_tabla (str): Tipo de tabla ('entrega' o 'historial')
            
        Returns:
            dict: Configuración de la tabla
        """
        if tipo_tabla == 'entrega':
            return cls.TABLA_ENTREGA_LLAVES.copy()
        elif tipo_tabla == 'historial':
            return cls.TABLA_HISTORIAL_LLAVES.copy()
        else:
            raise ValueError(f"Tipo de tabla no válido: {tipo_tabla}")