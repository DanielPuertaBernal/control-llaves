"""
Servicio de paginación de datos
Maneja la lógica de paginación de forma reutilizable
"""
import pandas as pd


class PaginacionService:
    """Servicio para paginación de datos"""
    
    def __init__(self, items_por_pagina=15):
        self.items_por_pagina = items_por_pagina
        self.pagina_actual = 1
        self.total_paginas = 1
        self.total_items = 0
        self.datos_completos = []
    
    def actualizar_datos(self, datos):
        """
        Actualiza los datos y recalcula paginación
        
        Args:
            datos: Lista o DataFrame con los datos
        """
        self.datos_completos = datos
        
        # Calcular total de items
        try:
            if datos is None:
                self.total_items = 0
            elif isinstance(datos, pd.DataFrame):
                self.total_items = len(datos)
            elif hasattr(datos, '__len__'):
                self.total_items = len(datos)
            else:
                self.total_items = 0
        except:
            self.total_items = 0
        
        self._calcular_paginacion()
    
    def obtener_pagina_actual(self):
        """
        Obtiene los datos de la página actual
        
        Returns:
            tuple: (datos_pagina, inicio, fin)
        """
        if self.total_items == 0:
            return [], 0, 0
        
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = min(inicio + self.items_por_pagina, self.total_items)
        
        try:
            if isinstance(self.datos_completos, pd.DataFrame):
                datos_pagina = self.datos_completos.iloc[inicio:fin]
            else:
                datos_pagina = self.datos_completos[inicio:fin]
            return datos_pagina, inicio, fin
        except Exception as e:
            print(f"Error al obtener página: {e}")
            return [], 0, 0
    
    def pagina_siguiente(self):
        """Avanza a la siguiente página"""
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
    
    def pagina_anterior(self):
        """Retrocede a la página anterior"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
    
    def ir_a_pagina(self, numero_pagina):
        """Va a una página específica"""
        if 1 <= numero_pagina <= self.total_paginas:
            self.pagina_actual = numero_pagina
    
    def _calcular_paginacion(self):
        """Calcula el número total de páginas"""
        if self.total_items == 0:
            self.total_paginas = 1
            self.pagina_actual = 1
        else:
            self.total_paginas = max(1, (self.total_items + self.items_por_pagina - 1) // self.items_por_pagina)
            if self.pagina_actual > self.total_paginas:
                self.pagina_actual = self.total_paginas
    
    def obtener_info_paginacion(self):
        """
        Obtiene información de paginación
        
        Returns:
            dict: Información de paginación
        """
        return {
            'pagina_actual': self.pagina_actual,
            'total_paginas': self.total_paginas,
            'total_items': self.total_items,
            'items_por_pagina': self.items_por_pagina,
            'tiene_anterior': self.pagina_actual > 1,
            'tiene_siguiente': self.pagina_actual < self.total_paginas
        }
