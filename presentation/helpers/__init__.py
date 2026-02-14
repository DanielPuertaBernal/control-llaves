"""Helpers para operaciones comunes en las vistas"""

from tkinter import filedialog, messagebox
from typing import Optional, Callable, Any
import pandas as pd


class ViewHelper:
    """Centraliza operaciones comunes de UI para eliminar código duplicado en las vistas"""
    
    @staticmethod
    def mostrar_exito(titulo: str, mensaje: str) -> None:
        """Muestra un mensaje de éxito"""
        messagebox.showinfo(titulo, mensaje)
    
    @staticmethod
    def mostrar_error(titulo: str, mensaje: str) -> None:
        """Muestra un mensaje de error"""
        messagebox.showerror(titulo, mensaje)
    
    @staticmethod
    def mostrar_advertencia(titulo: str, mensaje: str) -> None:
        """Muestra un mensaje de advertencia"""
        messagebox.showwarning(titulo, mensaje)
    
    @staticmethod
    def exportar_excel_dialogo(
        dataframe: pd.DataFrame,
        callback_exportar: Callable[[pd.DataFrame, str], None],
        nombre_archivo: str = "export.xlsx",
        titulo: str = "Guardar archivo Excel"
    ) -> bool:
        """
        Muestra diálogo para exportar DataFrame a Excel y ejecuta la exportación.
        
        Args:
            dataframe: DataFrame a exportar
            callback_exportar: Función que recibe (df, ruta) para hacer la exportación
            nombre_archivo: Nombre por defecto del archivo
            titulo: Título del diálogo
            
        Returns:
            True si se exportó exitosamente, False en caso contrario
        """
        if dataframe is None or dataframe.empty:
            ViewHelper.mostrar_advertencia("Sin datos", "No hay datos para exportar")
            return False
        
        ruta_guardado = filedialog.asksaveasfilename(
            title=titulo,
            defaultextension=".xlsx",
            filetypes=[
                ("Archivo Excel", "*.xlsx"),
                ("Todos los archivos", "*.*")
            ],
            initialfile=nombre_archivo
        )
        
        if not ruta_guardado:
            return False
        
        try:
            callback_exportar(dataframe, ruta_guardado)
            ViewHelper.mostrar_exito("Éxito", f"Archivo exportado en:\n{ruta_guardado}")
            return True
        except Exception as e:
            ViewHelper.mostrar_error("Error", f"Error al exportar:\n{str(e)}")
            return False
    
    @staticmethod
    def exportar_excel_simple(
        dataframe: pd.DataFrame,
        nombre_archivo: str = "export.xlsx",
        titulo: str = "Guardar archivo Excel"
    ) -> bool:
        """
        Exporta DataFrame a Excel directamente sin callback personalizado.
        
        Args:
            dataframe: DataFrame a exportar
            nombre_archivo: Nombre por defecto del archivo
            titulo: Título del diálogo
            
        Returns:
            True si se exportó exitosamente, False en caso contrario
        """
        def exportar_default(df: pd.DataFrame, ruta: str) -> None:
            df.to_excel(ruta, index=False, engine='openpyxl')
        
        return ViewHelper.exportar_excel_dialogo(
            dataframe, 
            exportar_default, 
            nombre_archivo, 
            titulo
        )
