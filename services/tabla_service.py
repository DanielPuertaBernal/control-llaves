"""
Servicio de configuración de tablas
Define columnas y estilos estándar para tablas
"""


class TablaService:
    """Servicio de configuración de tablas"""
    
    # Configuraciones de tablas
    TABLA_ENTREGA = {
        'columnas': ('Documento', 'Docente', 'Aula', 'Horario', 'Materia'),
        'anchos': [120, 180, 80, 120, 200],
        'alineacion': 'center',
        'altura': 15
    }
    
    TABLA_HISTORIAL = {
        'columnas': ('documento', 'docente', 'horario', 'aula', 'materia', 'hora_entrega'),
        'nombres': ('Documento', 'Docente', 'Horario', 'Aula', 'Materia', 'Hora Entrega'),
        'anchos': [120, 200, 150, 100, 220, 120],
        'alineacion': 'center',
        'altura': 15
    }
    
    @classmethod
    def configurar_treeview(cls, treeview, tipo):
        """
        Configura un Treeview con la configuración especificada
        
        Args:
            treeview: Widget Treeview
            tipo (str): 'entrega' o 'historial'
        """
        config = cls.TABLA_ENTREGA if tipo == 'entrega' else cls.TABLA_HISTORIAL
        
        columnas = config['columnas']
        treeview.configure(columns=columnas, show='headings', height=config['altura'])
        
        nombres = config.get('nombres', columnas)
        anchos = config['anchos']
        alineacion = config['alineacion']
        
        for col, nombre, ancho in zip(columnas, nombres, anchos):
            treeview.heading(col, text=nombre, anchor=alineacion)
            treeview.column(col, width=ancho, anchor=alineacion)
    
    @classmethod
    def obtener_configuracion(cls, tipo):
        """Obtiene configuración de tabla"""
        return cls.TABLA_ENTREGA.copy() if tipo == 'entrega' else cls.TABLA_HISTORIAL.copy()
