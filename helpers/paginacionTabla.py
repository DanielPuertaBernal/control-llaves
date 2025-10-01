from tkinter import ttk
import tkinter as tk

class PaginacionTabla:
    """
    Componente de paginación reutilizable para tablas de datos
    Maneja la lógica de paginación y los controles de navegación
    """
    
    def __init__(self, items_por_pagina=20):
        """
        Inicializa el componente de paginación
        
        Args:
            items_por_pagina (int): Número de elementos por página
        """
        self.pagina_actual = 1
        self.items_por_pagina = items_por_pagina
        self.total_paginas = 1
        self.total_items = 0
        self.datos_completos = []
        
        # Referencias a los widgets de UI (se asignan después)
        self.btn_anterior = None
        self.btn_siguiente = None
        self.label_pagina = None
        self.label_info = None
        
        # Callback para actualizar la vista (se asigna por la vista que lo usa)
        self.callback_mostrar_datos = None
    
    def ConfigurarWidgets(self, btn_anterior, btn_siguiente, label_pagina, label_info):
        """
        Configura las referencias a los widgets de UI
        
        Args:
            btn_anterior: Botón para página anterior
            btn_siguiente: Botón para página siguiente
            label_pagina: Label que muestra información de página
            label_info: Label que muestra información general
        """
        self.btn_anterior = btn_anterior
        self.btn_siguiente = btn_siguiente
        self.label_pagina = label_pagina
        self.label_info = label_info
        
        # Configurar eventos de los botones
        if self.btn_anterior:
            self.btn_anterior.configure(command=self.PaginaAnterior)
        if self.btn_siguiente:
            self.btn_siguiente.configure(command=self.PaginaSiguiente)
    
    def ConfigurarCallback(self, callback_funcion):
        """
        Configura la función callback que se llama cuando se necesita mostrar datos
        
        Args:
            callback_funcion: Función que recibe (datos_pagina, inicio, fin) y actualiza la vista
        """
        self.callback_mostrar_datos = callback_funcion
    
    def ActualizarDatos(self, datos_completos):
        """
        Actualiza los datos completos y recalcula la paginación
        
        Args:
            datos_completos: Lista o DataFrame con todos los datos
        """
        self.datos_completos = datos_completos
        
        # Manejo seguro del conteo de elementos
        try:
            if datos_completos is None:
                self.total_items = 0
            elif hasattr(datos_completos, '__len__'):
                self.total_items = len(datos_completos)
            else:
                self.total_items = 0
        except Exception:
            self.total_items = 0
        
        # Mantener página actual si es válida, sino ir a la primera
        self.CalcularPaginacion()
        self.ActualizarVista()
    
    def CalcularPaginacion(self):
        """Calcula el número total de páginas"""
        if self.total_items == 0:
            self.total_paginas = 1
            self.pagina_actual = 1
        else:
            self.total_paginas = max(1, (self.total_items + self.items_por_pagina - 1) // self.items_por_pagina)
            
            # Asegurar que la página actual esté dentro del rango válido
            if self.pagina_actual > self.total_paginas:
                self.pagina_actual = self.total_paginas
            elif self.pagina_actual < 1:
                self.pagina_actual = 1
    
    def ObtenerDatosPaginaActual(self):
        """
        Obtiene los datos de la página actual
        
        Returns:
            tuple: (datos_pagina, inicio, fin) donde inicio y fin son los índices
        """
        # Verificación más robusta de datos vacíos
        if (self.datos_completos is None or 
            self.total_items == 0 or 
            (hasattr(self.datos_completos, '__len__') and len(self.datos_completos) == 0)):
            return [], 0, 0
        
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = min(inicio + self.items_por_pagina, self.total_items)
        
        try:
            # Manejar tanto listas como DataFrames de forma más segura
            if hasattr(self.datos_completos, 'iloc'):
                # Es un DataFrame de pandas
                datos_pagina = self.datos_completos.iloc[inicio:fin]
            else:
                # Es una lista
                datos_pagina = self.datos_completos[inicio:fin]
        except Exception as e:
            print(f"Error al obtener datos de página: {e}")
            return [], 0, 0
        
        return datos_pagina, inicio, fin
    
    def ActualizarVista(self):
        """Actualiza toda la vista de paginación"""
        self.ActualizarInfoPagina()
        self.ActualizarBotonesNavegacion()
        self.MostrarDatosPagina()
    
    def ActualizarInfoPagina(self):
        """Actualiza las etiquetas de información de paginación"""
        if self.label_pagina:
            self.label_pagina.config(text=f"Página {self.pagina_actual} de {self.total_paginas}")
        
        if self.label_info:
            self.label_info.config(text=f"{self.total_items} registros encontrados")
    
    def ActualizarBotonesNavegacion(self):
        """Actualiza el estado de los botones de navegación"""
        if self.btn_anterior:
            if self.pagina_actual <= 1:
                self.btn_anterior.config(state='disabled')
            else:
                self.btn_anterior.config(state='normal')
        
        if self.btn_siguiente:
            if self.pagina_actual >= self.total_paginas:
                self.btn_siguiente.config(state='disabled')
            else:
                self.btn_siguiente.config(state='normal')
    
    def MostrarDatosPagina(self):
        """Llama al callback para mostrar los datos de la página actual"""
        if self.callback_mostrar_datos:
            datos_pagina, inicio, fin = self.ObtenerDatosPaginaActual()
            self.callback_mostrar_datos(datos_pagina, inicio, fin)
    
    def PaginaAnterior(self):
        """Navega a la página anterior"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.ActualizarVista()
    
    def PaginaSiguiente(self):
        """Navega a la página siguiente"""
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.ActualizarVista()
    
    def IrAPagina(self, numero_pagina):
        """
        Navega a una página específica
        
        Args:
            numero_pagina (int): Número de página a la que navegar
        """
        if 1 <= numero_pagina <= self.total_paginas:
            self.pagina_actual = numero_pagina
            self.ActualizarVista()
    
    def ReiniciarPaginacion(self):
        """Reinicia la paginación a la primera página"""
        self.pagina_actual = 1
        self.ActualizarVista()
    
    def CambiarItemsPorPagina(self, nuevos_items_por_pagina):
        """
        Cambia el número de elementos por página
        
        Args:
            nuevos_items_por_pagina (int): Nuevo número de elementos por página
        """
        if nuevos_items_por_pagina > 0:
            # Calcular en qué elemento estamos actualmente
            elemento_actual = (self.pagina_actual - 1) * self.items_por_pagina
            
            # Actualizar items por página
            self.items_por_pagina = nuevos_items_por_pagina
            
            # Calcular nueva página para mantener posición aproximada
            self.pagina_actual = max(1, (elemento_actual // self.items_por_pagina) + 1)
            
            # Recalcular paginación
            self.CalcularPaginacion()
            self.ActualizarVista()
    
    def ObtenerEstadoPaginacion(self):
        """
        Obtiene el estado actual de la paginación
        
        Returns:
            dict: Diccionario con información del estado actual
        """
        return {
            'pagina_actual': self.pagina_actual,
            'total_paginas': self.total_paginas,
            'items_por_pagina': self.items_por_pagina,
            'total_items': self.total_items,
            'tiene_anterior': self.pagina_actual > 1,
            'tiene_siguiente': self.pagina_actual < self.total_paginas
        }
    
    def CrearWidgetsPaginacion(self, frame_padre):
        """
        Crea los widgets de paginación en un frame padre
        
        Args:
            frame_padre: Frame donde crear los widgets
            
        Returns:
            tuple: (btn_anterior, btn_siguiente, label_pagina, label_info)
        """
        # Crear botón anterior
        btn_anterior = ttk.Button(frame_padre, text="◀ Anterior", state='disabled')
        btn_anterior.pack(side='left')
        
        # Crear label de página
        label_pagina = ttk.Label(frame_padre, text="Página 1 de 1")
        label_pagina.pack(side='left', padx=(20, 20))
        
        # Crear botón siguiente
        btn_siguiente = ttk.Button(frame_padre, text="Siguiente ▶", state='disabled')
        btn_siguiente.pack(side='left')
        
        # Crear label de información
        label_info = ttk.Label(frame_padre, text="0 registros encontrados")
        label_info.pack(side='right')
        
        # Configurar widgets automáticamente
        self.ConfigurarWidgets(btn_anterior, btn_siguiente, label_pagina, label_info)
        
        return btn_anterior, btn_siguiente, label_pagina, label_info