"""
Factory para crear widgets de fecha
Maneja la creación de DateEntry o Entry según disponibilidad de tkcalendar
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

try:
    from tkcalendar import DateEntry
    CALENDARIO_DISPONIBLE = True
except ImportError:
    CALENDARIO_DISPONIBLE = False


class DateWidgetFactory:
    """Factory para crear widgets de selección de fecha"""
    
    @staticmethod
    def crear_selector_fecha(
        parent,
        fecha_inicial: datetime = None,
        width: int = 18,
        **kwargs
    ):
        """
        Crea un widget de selección de fecha (DateEntry o Entry según disponibilidad)
        
        Args:
            parent: Widget padre
            fecha_inicial: Fecha inicial a mostrar (default: hoy)
            width: Ancho del widget
            **kwargs: Argumentos adicionales para el widget
            
        Returns:
            Widget de fecha (DateEntry o Entry)
        """
        if fecha_inicial is None:
            fecha_inicial = datetime.now()
        
        if CALENDARIO_DISPONIBLE:
            return DateEntry(
                parent,
                width=width,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd',
                **kwargs
            )
        else:
            # Fallback a Entry simple
            entry = ttk.Entry(parent, width=width, **kwargs)
            entry.insert(0, fecha_inicial.strftime('%Y-%m-%d'))
            return entry
    
    @staticmethod
    def obtener_fecha(widget) -> str:
        """
        Obtiene la fecha del widget en formato YYYY-MM-DD
        
        Args:
            widget: Widget de fecha (DateEntry o Entry)
            
        Returns:
            String con fecha en formato YYYY-MM-DD
        """
        if CALENDARIO_DISPONIBLE and hasattr(widget, 'get_date'):
            try:
                fecha = widget.get_date()
                if hasattr(fecha, 'strftime'):
                    return fecha.strftime('%Y-%m-%d')
                return str(fecha)
            except Exception:
                return widget.get().strip()
        else:
            return widget.get().strip()
    
    @staticmethod
    def establecer_fecha(widget, fecha: datetime):
        """
        Establece la fecha en el widget
        
        Args:
            widget: Widget de fecha (DateEntry o Entry)
            fecha: Objeto datetime a establecer
        """
        if CALENDARIO_DISPONIBLE and hasattr(widget, 'set_date'):
            try:
                widget.set_date(fecha)
            except Exception:
                widget.delete(0, 'end')
                widget.insert(0, fecha.strftime('%Y-%m-%d'))
        else:
            widget.delete(0, 'end')
            widget.insert(0, fecha.strftime('%Y-%m-%d'))
    
    @staticmethod
    def esta_disponible_calendario() -> bool:
        """
        Verifica si tkcalendar está disponible
        
        Returns:
            True si DateEntry está disponible, False si no
        """
        return CALENDARIO_DISPONIBLE
