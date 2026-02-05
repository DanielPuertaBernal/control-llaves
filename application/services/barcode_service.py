"""
Servicio de Generación de Códigos de Barras
"""
import os
import tempfile
from pathlib import Path
import barcode
from barcode.writer import ImageWriter
from PIL import Image
from typing import Optional


class BarcodeService:
    """Servicio para generar códigos de barras"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def generar_codigo_barras(self, codigo_barras: str) -> Optional[str]:
        """
        Genera una imagen de código de barras simple
        
        Args:
            codigo_barras: El código de barras a generar (ej: INV-001-001)
        
        Returns:
            Ruta de la imagen generada o None si falla
        """
        try:
            # Crear el código de barras (code128)
            codigo_barras_obj = barcode.get('code128', codigo_barras, writer=ImageWriter())
            
            # Guardar en archivo temporal
            archivo_temp = os.path.join(self.temp_dir, f'barcode_{codigo_barras.replace("-", "_")}')
            archivo_generado = codigo_barras_obj.save(archivo_temp, options={'module_height': 15, 'module_width': 0.5})
            
            return archivo_generado
        except Exception as e:
            print(f"Error generando código de barras: {e}")
            return None

