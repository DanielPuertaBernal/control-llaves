"""
Modelo para la gestión de préstamos de llaves
Maneja toda la lógica de datos relacionada con entregas y devoluciones
"""
from datetime import datetime
import os
from openpyxl import Workbook, load_workbook
import pandas as pd


class LlaveModel:
    """Modelo para gestionar préstamos de llaves"""
    
    def __init__(self):
        self.ruta_data = self._obtener_ruta_data()
        self.ruta_registro = os.path.join(self.ruta_data, 'registrosLlaves.xlsx')
        self._inicializar_registro()
    
    def _obtener_ruta_data(self):
        """Obtiene la ruta del directorio data"""
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_proyecto = os.path.dirname(ruta_actual)
        return os.path.join(ruta_proyecto, "data")
    
    def _inicializar_registro(self):
        """Inicializa el archivo de registro si no existe"""
        if not os.path.exists(self.ruta_data):
            os.makedirs(self.ruta_data)
        
        if not os.path.exists(self.ruta_registro):
            wb = Workbook()
            ws_prestamo = wb.active
            ws_prestamo.title = "Llaves en Prestamo"
            ws_entregadas = wb.create_sheet("Llaves Entregadas")
            
            headers = [
                'Número de Documento', 'Docente', 'Día', 'Horario', 'Aula', 'Facultad', 
                'Materia de la Clase', 'Fecha de entrega', 'Hora de entrega', 
                'Fecha de devolución', 'Hora de devolución', 'Estado'
            ]
            
            ws_prestamo.append(headers)
            ws_entregadas.append(headers)
            wb.save(self.ruta_registro)
    
    def registrar_entrega(self, info_clase):
        """
        Registra la entrega de una llave
        
        Args:
            info_clase (dict): Información de la clase con llaves:
                - nroidenti: Número de documento
                - profesor: Nombre del docente
                - dia: Día de la semana
                - horario: Horario de la clase
                - aula: Salón
                - facultad: Facultad
                - materia: Materia de la clase
        
        Returns:
            bool: True si se registró exitosamente, False si ya tiene una llave prestada
        """
        try:
            wb = load_workbook(self.ruta_registro)
            ws = wb["Llaves en Prestamo"]
            
            nroidenti_limpio = self._limpiar_numero_documento(info_clase['nroidenti'])
            
            # Verificar si ya tiene una llave prestada
            if self._tiene_llave_prestada(ws, nroidenti_limpio):
                wb.close()
                return False
            
            # Crear nuevo registro
            ahora = datetime.now()
            nuevo_registro = [
                nroidenti_limpio,
                info_clase.get('profesor', ''),
                info_clase.get('dia', ''),
                info_clase.get('horario', ''),
                info_clase.get('aula', ''),
                info_clase.get('facultad', 'No especificada'),
                info_clase.get('materia', ''),
                ahora.strftime('%Y-%m-%d'),
                ahora.strftime('%H:%M:%S'),
                '',
                '',
                'En Préstamo'
            ]
            
            ws.append(nuevo_registro)
            wb.save(self.ruta_registro)
            wb.close()
            return True
            
        except Exception as e:
            print(f"Error en registrar_entrega: {e}")
            return False
    
    def registrar_devolucion(self, nroidenti):
        """
        Registra la devolución de una llave
        
        Args:
            nroidenti: Número de documento del docente
        
        Returns:
            bool: True si se registró exitosamente, False en caso contrario
        """
        try:
            if not os.path.exists(self.ruta_registro):
                return False
            
            wb = load_workbook(self.ruta_registro)
            ws_prestamo = wb["Llaves en Prestamo"]
            ws_entregadas = wb["Llaves Entregadas"]
            
            nroidenti_limpio = self._limpiar_numero_documento(nroidenti)
            fila_encontrada = None
            registro_data = None
            
            # Buscar la llave en préstamo
            for row_idx, row in enumerate(ws_prestamo.iter_rows(min_row=2, values_only=False), start=2):
                if (row and str(row[0].value) == nroidenti_limpio and 
                    row[11].value == 'En Préstamo'):
                    fila_encontrada = row_idx
                    registro_data = [cell.value for cell in row]
                    break
            
            if fila_encontrada:
                ahora = datetime.now()
                
                # Actualizar registro con datos de devolución
                registro_data[9] = ahora.strftime('%Y-%m-%d')  # Fecha devolución
                registro_data[10] = ahora.strftime('%H:%M:%S')  # Hora devolución
                registro_data[11] = 'Devuelta'  # Estado
                
                # Agregar a hoja de llaves entregadas
                ws_entregadas.append(registro_data)
                
                # Eliminar de hoja de préstamos
                ws_prestamo.delete_rows(fila_encontrada, 1)
                
                wb.save(self.ruta_registro)
                wb.close()
                return True
            
            wb.close()
            return False
            
        except Exception as e:
            print(f"Error en registrar_devolucion: {e}")
            return False
    
    def obtener_llaves_pendientes(self):
        """
        Obtiene todas las llaves actualmente en préstamo
        
        Returns:
            list: Lista de diccionarios con información de llaves en préstamo
        """
        try:
            if not os.path.exists(self.ruta_registro):
                return []
            
            wb = load_workbook(self.ruta_registro)
            ws = wb["Llaves en Prestamo"]
            
            llaves_pendientes = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and row[11] == 'En Préstamo':
                    llave_info = {
                        'documento': self._limpiar_numero_documento(row[0]),
                        'docente': row[1],
                        'dia': row[2],
                        'horario': row[3],
                        'aula': row[4],
                        'facultad': row[5],
                        'materia': row[6],
                        'fecha_entrega': row[7],
                        'hora_entrega': row[8],
                        'estado': row[11]
                    }
                    llaves_pendientes.append(llave_info)
            
            wb.close()
            return llaves_pendientes
            
        except Exception as e:
            print(f"Error al obtener llaves pendientes: {e}")
            return []
    
    def obtener_historial_completo(self):
        """
        Obtiene el historial completo de préstamos (activos y devueltos)
        
        Returns:
            pd.DataFrame: DataFrame con el historial completo
        """
        try:
            if not os.path.exists(self.ruta_registro):
                return pd.DataFrame()
            
            df_prestamo = pd.read_excel(self.ruta_registro, sheet_name='Llaves en Prestamo')
            df_entregadas = pd.read_excel(self.ruta_registro, sheet_name='Llaves Entregadas')
            
            # Combinar ambos DataFrames
            df_completo = pd.concat([df_prestamo, df_entregadas], ignore_index=True)
            return df_completo
            
        except Exception as e:
            print(f"Error al obtener historial completo: {e}")
            return pd.DataFrame()
    
    def _tiene_llave_prestada(self, ws, nroidenti):
        """Verifica si un docente ya tiene una llave prestada"""
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and str(row[0]) == nroidenti and row[11] == 'En Préstamo':
                return True
        return False
    
    @staticmethod
    def _limpiar_numero_documento(doc):
        """Limpia el número de documento eliminando .0 si existe"""
        doc_str = str(doc)
        return doc_str[:-2] if doc_str.endswith('.0') else doc_str
