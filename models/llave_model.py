"""
Modelo para la gestión de préstamos de llaves
Maneja toda la lógica de datos relacionada con entregas y devoluciones
"""
from datetime import datetime, date, time, timedelta
import os
from openpyxl import Workbook, load_workbook
import pandas as pd


class LlaveModel:
    """Modelo para gestionar préstamos de llaves"""
    
    def __init__(self):
        self.ruta_data = self._obtener_ruta_data()
        self.ruta_registro = os.path.join(self.ruta_data, 'registrosLlaves.xlsx')
        self._inicializar_registro()
        self._asegurar_formato_registro()
    
    def _obtener_ruta_data(self):
        """Obtiene la ruta del directorio data"""
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_proyecto = os.path.dirname(ruta_actual)
        return os.path.join(ruta_proyecto, "data")
    
    def _inicializar_registro(self):
        """Inicializa el archivo de registro con una sola hoja si no existe"""
        if not os.path.exists(self.ruta_data):
            os.makedirs(self.ruta_data)
        
        if not os.path.exists(self.ruta_registro):
            wb = Workbook()
            ws = wb.active
            ws.title = "Registro de Llaves"
            
            # Headers unificados con todos los campos
            headers = [
                'Número de Documento', 'Docente', 'Día', 'Horario', 'Aula', 'Facultad',
                'Materia de la Clase', 'Fecha de entrega', 'Hora de entrega',
                'Fecha de devolución', 'Hora de devolución',
                'Duración clase (entrega→devolución)',
                'Se reclamó a tiempo',
                'Tiempo de retraso',
                'Retraso en entrega',
                'Tiempo retraso devolución',
                'Estado'
            ]
            
            ws.append(headers)
            wb.save(self.ruta_registro)

    def _asegurar_formato_registro(self):
        """Actualiza el archivo existente para incluir nuevas columnas si faltan."""
        try:
            if not os.path.exists(self.ruta_registro):
                return
            wb = load_workbook(self.ruta_registro)
            ws = wb["Registro de Llaves"]
            headers = [cell.value for cell in ws[1]]
            # Si ya está actualizado, salir
            if len(headers) >= 15:
                wb.close()
                return
            # Transformar headers antiguos (12 columnas) a nuevos (17)
            nuevos_headers = [
                'Número de Documento', 'Docente', 'Día', 'Horario', 'Aula', 'Facultad',
                'Materia de la Clase', 'Fecha de entrega', 'Hora de entrega',
                'Fecha de devolución', 'Hora de devolución',
                'Duración clase (entrega→devolución)',
                'Se reclamó a tiempo',
                'Tiempo de retraso',
                'Retraso en entrega',
                'Tiempo retraso devolución',
                'Estado'
            ]
            ws.delete_rows(1)
            ws.insert_rows(1)
            ws.append(nuevos_headers)
            # Ajustar filas existentes
            filas_originales = list(ws.iter_rows(min_row=2, values_only=True))
            # Limpiar filas originales
            ws.delete_rows(2, ws.max_row)
            for row in filas_originales:
                if len(row) >= 12:
                    estado = row[11]
                    nueva = list(row[:11])  # hasta hora_devolucion
                    nueva += [
                        '',        # duración
                        'No info', # se reclamó a tiempo
                        '',        # tiempo retraso
                        '',        # retraso en entrega
                        '',        # tiempo retraso devolución
                        estado     # estado al final
                    ]
                    ws.append(nueva)
            wb.save(self.ruta_registro)
            wb.close()
        except Exception as e:
            print(f"Error al asegurar formato de registro: {e}")
    
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
            ws = wb["Registro de Llaves"]
            
            nroidenti_limpio = self._limpiar_numero_documento(info_clase['nroidenti'])
            
            # Verificar si ya tiene una llave prestada
            if self._tiene_llave_prestada(ws, nroidenti_limpio):
                wb.close()
                return False
            
            # Crear nuevo registro con columnas de devolución vacías
            ahora = datetime.now()
            se_tiempo, retraso = self._evaluar_reclamo_tiempo(info_clase.get('horario', ''), ahora)

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
                '',  # Fecha de devolución (vacío)
                '',  # Hora de devolución (vacío)
                '',  # Duración clase (vacío hasta devolución)
                se_tiempo,            # Se reclamó a tiempo (Sí/No)
                retraso,              # Tiempo de retraso
                'No',                 # Retraso en entrega (inicialmente No)
                '',                   # Tiempo retraso devolución (vacío hasta devolver)
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
        Registra la devolución de una llave actualizando el registro existente
        
        Args:
            nroidenti: Número de documento del docente
        
        Returns:
            bool: True si se registró exitosamente, False en caso contrario
        """
        try:
            if not os.path.exists(self.ruta_registro):
                return False
            
            wb = load_workbook(self.ruta_registro)
            ws = wb["Registro de Llaves"]
            
            nroidenti_limpio = self._limpiar_numero_documento(nroidenti)
            ahora = datetime.now()
            
            # Buscar y actualizar la fila correspondiente
            for row in ws.iter_rows(min_row=2):
                if (row[0].value and str(row[0].value) == nroidenti_limpio and 
                    row[16].value == 'En Préstamo'):  # Índice 16 es Estado
                    # Actualizar fecha y hora de devolución
                    row[9].value = ahora.strftime('%Y-%m-%d')   # Fecha devolución
                    row[10].value = ahora.strftime('%H:%M:%S')  # Hora devolución
                    # Calcular duración si hay entrega previa
                    duracion = self._calcular_duracion(row[7].value, row[8].value, ahora)
                    row[11].value = duracion
                    # Calcular tiempo retraso devolución si hay retraso
                    horario = row[3].value
                    tiempo_retraso_dev = self._calcular_tiempo_retraso_devolucion(horario, row[7].value, ahora)
                    row[15].value = tiempo_retraso_dev
                    # Actualizar campo "Retraso en entrega" basado en si hay retraso
                    row[14].value = 'Sí' if tiempo_retraso_dev else 'No'
                    row[16].value = 'Devuelta'                  # Estado
                    
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
            ws = wb["Registro de Llaves"]
            
            llaves_pendientes = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and row[16] == 'En Préstamo':  # Índice 16 es Estado
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
                        'estado': row[16]
                    }
                    llaves_pendientes.append(llave_info)
            
            wb.close()
            return llaves_pendientes
            
        except Exception as e:
            print(f"Error al obtener llaves pendientes: {e}")
            return []
    
    def obtener_llaves_prestadas_dia(self, fecha_actual):
        """
        Obtiene las llaves prestadas exclusivamente del día actual
        
        Args:
            fecha_actual (date): Fecha actual para filtrar
        
        Returns:
            list: Lista de diccionarios con información de llaves prestadas del día
        """
        try:
            if not os.path.exists(self.ruta_registro):
                return []
            
            wb = load_workbook(self.ruta_registro)
            ws = wb["Registro de Llaves"]
            
            # Convertir fecha actual a string formato YYYY-MM-DD
            fecha_str = fecha_actual.strftime('%Y-%m-%d')
            
            llaves_del_dia = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and row[16] == 'En Préstamo':  # Índice 16 es Estado
                    # Obtener fecha de entrega de la fila
                    fecha_entrega = row[7]
                    
                    # Convertir a string si es datetime
                    if hasattr(fecha_entrega, 'strftime'):
                        fecha_entrega_str = fecha_entrega.strftime('%Y-%m-%d')
                    else:
                        fecha_entrega_str = str(fecha_entrega)
                    
                    # Filtrar solo registros del día actual
                    if fecha_entrega_str == fecha_str:
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
                            'estado': row[16]
                        }
                        llaves_del_dia.append(llave_info)
            
            wb.close()
            return llaves_del_dia
            
        except Exception as e:
            print(f"Error al obtener llaves prestadas del día: {e}")
            return []
    
    def obtener_clases_procesadas_hoy(self, fecha_actual):
        """
        Obtiene todas las clases que recibieron llaves hoy (En Préstamo o Devueltas).
        Sirve para evitar que una clase vuelva a aparecer en la vista de entrega
        después de ser devuelta el mismo día.
        
        Args:
            fecha_actual (date): Fecha actual para filtrar
        
        Returns:
            list: Lista de diccionarios con documento y horario de clases procesadas
        """
        try:
            if not os.path.exists(self.ruta_registro):
                return []
            
            wb = load_workbook(self.ruta_registro)
            ws = wb["Registro de Llaves"]
            
            # Convertir fecha actual a string formato YYYY-MM-DD
            fecha_str = fecha_actual.strftime('%Y-%m-%d')
            
            clases_procesadas = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row:
                    # Obtener fecha de entrega
                    fecha_entrega = row[7]
                    
                    # Convertir a string si es datetime
                    if hasattr(fecha_entrega, 'strftime'):
                        fecha_entrega_str = fecha_entrega.strftime('%Y-%m-%d')
                    else:
                        fecha_entrega_str = str(fecha_entrega)
                    
                    # Incluir TODAS las entregas de hoy (En Préstamo y Devueltas)
                    if fecha_entrega_str == fecha_str:
                        clase_info = {
                            'documento': self._limpiar_numero_documento(row[0]),
                            'horario': str(row[3]).strip() if row[3] else ''
                        }
                        clases_procesadas.append(clase_info)
            
            wb.close()
            return clases_procesadas
            
        except Exception as e:
            print(f"Error al obtener clases procesadas hoy: {e}")
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
            
            df = pd.read_excel(self.ruta_registro, sheet_name='Registro de Llaves')
            return df
            
        except Exception as e:
            print(f"Error al obtener historial completo: {e}")
            return pd.DataFrame()
    
    def _tiene_llave_prestada(self, ws, nroidenti):
        """Verifica si un docente ya tiene una llave prestada"""
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and str(row[0]) == nroidenti and row[16] == 'En Préstamo':  # Índice 16 es Estado
                return True
        return False

    # ============ Helpers de tiempo ============
    def _evaluar_reclamo_tiempo(self, horario, momento_entrega):
        """Determina si se reclamó a tiempo y el retraso respecto al inicio de clase.
        Retorna (se_reclamo_a_tiempo, tiempo_retraso_str).
        """
        try:
            hora_inicio = self._parse_hora_inicio(horario)
            if hora_inicio is None:
                return 'No', 'N/A'
            inicio_dt = datetime.combine(momento_entrega.date(), hora_inicio)
            if momento_entrega <= inicio_dt:
                return 'Sí', '0'
            else:
                retraso = momento_entrega - inicio_dt
                return 'No', self._formatear_timedelta(retraso)
        except Exception:
            return 'No', 'N/A'

    def _calcular_duracion(self, fecha_entrega, hora_entrega, momento_devolucion):
        """Calcula duración desde entrega hasta devolución."""
        try:
            if not fecha_entrega or not hora_entrega:
                return ''
            if isinstance(fecha_entrega, datetime):
                fecha_entrega_dt = fecha_entrega.date()
            else:
                fecha_entrega_dt = datetime.strptime(str(fecha_entrega), '%Y-%m-%d').date()
            if isinstance(hora_entrega, time):
                hora_entrega_tm = hora_entrega
            else:
                hora_entrega_tm = datetime.strptime(str(hora_entrega), '%H:%M:%S').time()
            entrega_dt = datetime.combine(fecha_entrega_dt, hora_entrega_tm)
            duracion = momento_devolucion - entrega_dt
            if duracion.total_seconds() < 0:
                return ''
            return self._formatear_timedelta(duracion)
        except Exception:
            return ''

    def evaluar_retraso_entrega(self, horario, hora_entrega):
        """Evalúa si hay retraso en entrega (> 1 hora después de finalizar clase).
        Compara la hora actual contra la hora de fin de clase.
        
        Args:
            horario: Horario de la clase (ej: "10:30-11:30" o "10:30 A 11:30")
            hora_entrega: Hora de entrega de la llave (no se usa, solo para compatibilidad)
        
        Returns:
            bool: True si actualmente es > 1 hora después de fin de clase, False en caso contrario
        """
        try:
            if not horario:
                return False
            
            # Parsear hora de fin de clase
            hora_fin = self._parse_hora_fin(horario)
            if hora_fin is None:
                return False
            
            # Obtener hora actual
            ahora = datetime.now()
            
            # Combinar hora de fin con la fecha actual
            fin_clase_dt = datetime.combine(ahora.date(), hora_fin)
            
            # Calcular diferencia entre ahora y fin de clase
            diferencia = ahora - fin_clase_dt
            retraso_minutos = diferencia.total_seconds() / 60
            
            # Si es > 60 minutos (1 hora), hay retraso
            return retraso_minutos > 60
            
        except Exception as e:
            print(f"Error en evaluar_retraso_entrega: {e}")
            return False

    @staticmethod
    def _parse_hora_inicio(horario):
        """Parses 'HH:MM-HH:MM' o 'HH:MM A HH:MM' y retorna time de inicio."""
        if not horario:
            return None
        horario_str = str(horario).strip()
        if '-' in horario_str:
            inicio = horario_str.split('-')[0].strip()
        elif ' A ' in horario_str.upper():
            partes = [p for p in horario_str.replace(' a ', ' A ').split(' A ') if ':' in p]
            inicio = partes[0].strip() if partes else horario_str
        else:
            inicio = horario_str
        try:
            return datetime.strptime(inicio[:5], '%H:%M').time()
        except ValueError:
            return None

    @staticmethod
    def _parse_hora_fin(horario):
        """Parses 'HH:MM-HH:MM' o 'HH:MM A HH:MM' y retorna time de fin."""
        if not horario:
            return None
        horario_str = str(horario).strip()
        if '-' in horario_str:
            partes = horario_str.split('-')
            fin = partes[1].strip() if len(partes) > 1 else horario_str
        elif ' A ' in horario_str.upper():
            partes = [p for p in horario_str.replace(' a ', ' A ').split(' A ') if ':' in p]
            fin = partes[1].strip() if len(partes) > 1 else horario_str
        else:
            fin = horario_str
        try:
            return datetime.strptime(fin[:5], '%H:%M').time()
        except ValueError:
            return None

    def _calcular_tiempo_retraso_devolucion(self, horario, fecha_entrega, momento_devolucion):
        """Calcula cuánto tiempo transcurrió desde fin de clase hasta devolución.
        Solo aplica si hay retraso (> 1 hora después de fin de clase).
        Formato: días, horas, minutos si aplica.
        """
        try:
            if not horario:
                return ''
            
            # Parsear hora de fin de clase
            hora_fin = self._parse_hora_fin(horario)
            if hora_fin is None:
                return ''
            
            # Obtener fecha de entrega
            if isinstance(fecha_entrega, datetime):
                fecha_entrega_dt = fecha_entrega.date()
            else:
                fecha_entrega_dt = datetime.strptime(str(fecha_entrega), '%Y-%m-%d').date()
            
            # Combinar fecha entrega con hora fin de clase
            fin_clase_dt = datetime.combine(fecha_entrega_dt, hora_fin)
            
            # Calcular diferencia
            diferencia = momento_devolucion - fin_clase_dt
            total_minutos = diferencia.total_seconds() / 60
            
            # Si no hay retraso (< 60 min), retornar vacío
            if total_minutos <= 60:
                return ''
            
            # Formatear considerando días, horas y minutos
            dias = int(total_minutos // (24 * 60))
            horas = int((total_minutos % (24 * 60)) // 60)
            minutos = int(total_minutos % 60)
            
            partes = []
            if dias > 0:
                partes.append(f"{dias}d")
            if horas > 0:
                partes.append(f"{horas}h")
            if minutos > 0 or not partes:  # Mostrar minutos si no hay días/horas
                partes.append(f"{minutos}m")
            
            return ' '.join(partes)
            
        except Exception as e:
            print(f"Error calculando retraso devolución: {e}")
            return ''

    @staticmethod
    def _formatear_timedelta(td: timedelta):
        total_seconds = int(td.total_seconds())
        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60
        segundos = total_seconds % 60
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    
    @staticmethod
    def _limpiar_numero_documento(doc):
        """Limpia el número de documento eliminando .0 si existe"""
        doc_str = str(doc)
        return doc_str[:-2] if doc_str.endswith('.0') else doc_str
