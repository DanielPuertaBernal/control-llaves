"""
Modelo para la gestión de préstamos de llaves
Maneja toda la lógica de datos relacionada con entregas y devoluciones
"""
from datetime import datetime, date, time, timedelta
import pandas as pd
from services.mongo_client import MongoClientProvider


class LlaveModel:
    """Modelo para gestionar préstamos de llaves"""
    
    def __init__(self):
        self.collection = MongoClientProvider.get_collection("registros_llaves")
        self._asegurar_indices()

    def _asegurar_indices(self):
        try:
            self.collection.create_index("Número de Documento")
            self.collection.create_index("Estado")
            self.collection.create_index("Fecha de entrega")
        except Exception:
            pass
    
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
            nroidenti_limpio = self._limpiar_numero_documento(info_clase['nroidenti'])
            
            # Verificar si ya tiene una llave prestada
            if self.collection.find_one({"Número de Documento": nroidenti_limpio, "Estado": "En Préstamo"}):
                return False
            
            # Crear nuevo registro con columnas de devolución vacías
            ahora = datetime.now()
            se_tiempo, retraso = self._evaluar_reclamo_tiempo(info_clase.get('horario', ''), ahora)

            nuevo_registro = {
                'Número de Documento': nroidenti_limpio,
                'Docente': info_clase.get('profesor', ''),
                'Día': info_clase.get('dia', ''),
                'Horario': info_clase.get('horario', ''),
                'Aula': info_clase.get('aula', ''),
                'Facultad': info_clase.get('facultad', 'No especificada'),
                'Materia de la Clase': info_clase.get('materia', ''),
                'Fecha de entrega': ahora.strftime('%Y-%m-%d'),
                'Hora de entrega': ahora.strftime('%H:%M:%S'),
                'Fecha de devolución': '',
                'Hora de devolución': '',
                'Duración clase (entrega→devolución)': '',
                'Se reclamó a tiempo': se_tiempo,
                'Tiempo de retraso': retraso,
                'Retraso en entrega': 'No',
                'Tiempo retraso devolución': '',
                'Estado': 'En Préstamo'
            }

            self.collection.insert_one(nuevo_registro)
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
            nroidenti_limpio = self._limpiar_numero_documento(nroidenti)
            ahora = datetime.now()
            registro = self.collection.find_one({
                "Número de Documento": nroidenti_limpio,
                "Estado": "En Préstamo"
            })

            if not registro:
                return False

            duracion = self._calcular_duracion(
                registro.get('Fecha de entrega'),
                registro.get('Hora de entrega'),
                ahora
            )
            horario = registro.get('Horario')
            tiempo_retraso_dev = self._calcular_tiempo_retraso_devolucion(
                horario,
                registro.get('Fecha de entrega'),
                ahora
            )

            self.collection.update_one(
                {"_id": registro["_id"]},
                {"$set": {
                    "Fecha de devolución": ahora.strftime('%Y-%m-%d'),
                    "Hora de devolución": ahora.strftime('%H:%M:%S'),
                    "Duración clase (entrega→devolución)": duracion,
                    "Tiempo retraso devolución": tiempo_retraso_dev,
                    "Retraso en entrega": 'Sí' if tiempo_retraso_dev else 'No',
                    "Estado": "Devuelta"
                }}
            )

            return True
            
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
            llaves_pendientes = []
            for registro in self.collection.find({"Estado": "En Préstamo"}, {"_id": 0}):
                llave_info = {
                    'documento': self._limpiar_numero_documento(registro.get('Número de Documento')),
                    'docente': registro.get('Docente'),
                    'dia': registro.get('Día'),
                    'horario': registro.get('Horario'),
                    'aula': registro.get('Aula'),
                    'facultad': registro.get('Facultad'),
                    'materia': registro.get('Materia de la Clase'),
                    'fecha_entrega': registro.get('Fecha de entrega'),
                    'hora_entrega': registro.get('Hora de entrega'),
                    'estado': registro.get('Estado')
                }
                llaves_pendientes.append(llave_info)
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
            # Convertir fecha actual a string formato YYYY-MM-DD
            fecha_str = fecha_actual.strftime('%Y-%m-%d')
            llaves_del_dia = []
            for registro in self.collection.find({"Estado": "En Préstamo", "Fecha de entrega": fecha_str}, {"_id": 0}):
                llave_info = {
                    'documento': self._limpiar_numero_documento(registro.get('Número de Documento')),
                    'docente': registro.get('Docente'),
                    'dia': registro.get('Día'),
                    'horario': registro.get('Horario'),
                    'aula': registro.get('Aula'),
                    'facultad': registro.get('Facultad'),
                    'materia': registro.get('Materia de la Clase'),
                    'fecha_entrega': registro.get('Fecha de entrega'),
                    'hora_entrega': registro.get('Hora de entrega'),
                    'estado': registro.get('Estado')
                }
                llaves_del_dia.append(llave_info)
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
            # Convertir fecha actual a string formato YYYY-MM-DD
            fecha_str = fecha_actual.strftime('%Y-%m-%d')
            clases_procesadas = []
            for registro in self.collection.find({"Fecha de entrega": fecha_str}, {"_id": 0, "Número de Documento": 1, "Horario": 1}):
                clase_info = {
                    'documento': self._limpiar_numero_documento(registro.get('Número de Documento')),
                    'horario': str(registro.get('Horario', '')).strip()
                }
                clases_procesadas.append(clase_info)
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
            registros = list(self.collection.find({}, {"_id": 0}))
            return pd.DataFrame(registros)
            
        except Exception as e:
            print(f"Error al obtener historial completo: {e}")
            return pd.DataFrame()
    
    def _tiene_llave_prestada(self, ws, nroidenti):
        """Verifica si un docente ya tiene una llave prestada"""
        return self.collection.find_one({"Número de Documento": nroidenti, "Estado": "En Préstamo"}) is not None

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
