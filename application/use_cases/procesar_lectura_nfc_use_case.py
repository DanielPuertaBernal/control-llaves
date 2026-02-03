"""
Caso de uso: Procesar lectura NFC
Maneja la lógica de procesamiento de carnets y validación de tiempos
"""
from application.services.docente_service import DocenteService
from application.services.llave_service import LlaveService
from application.services.programacion_service import ProgramacionService
from infrastructure.repositories.docente_mongo_repository import DocenteMongoRepository
from infrastructure.repositories.llave_mongo_repository import LlaveMongoRepository
from infrastructure.repositories.programacion_mongo_repository import ProgramacionMongoRepository
from datetime import datetime, date


class ProcesarLecturaNFCUseCase:
    """Caso de uso para procesar lecturas NFC y automatizar entregas/devoluciones"""
    
    def __init__(self):
        """Inicializa los servicios necesarios"""
        self.docente_service = DocenteService(DocenteMongoRepository())
        self.llave_service = LlaveService(LlaveMongoRepository())
        # ProgramacionService necesita llave_service
        self.programacion_service = ProgramacionService(
            ProgramacionMongoRepository(),
            self.llave_service
        )
    
    def ejecutar(self, id_carnet):
        """
        Procesa la lectura de un carnet NFC/RFID
        Realiza entrega o devolución automática según corresponda
        
        Args:
            id_carnet (str): ID del carnet leído
        
        Returns:
            dict: {
                'exito': bool,
                'accion': 'entrega'|'devolucion'|'advertencia'|'error',
                'mensaje': str,
                'datos_docente': dict (opcional),
                'datos_clase': dict (opcional),
                'hora_devolucion': str (opcional),
                'requiere_confirmacion': bool,
                'tiempo_faltante': str (opcional),
                'callback_confirmar': function (opcional)
            }
        """
        try:
            # 1. Buscar docente por ID de carnet
            docente = self.docente_service.buscar_docente_por_carnet(id_carnet)
            
            if not docente:
                return {
                    'exito': False,
                    'accion': 'error',
                    'mensaje': f'❌ Carnet no registrado: {id_carnet}\nPor favor, cargue la información de docentes primero.'
                }
            
            numero_documento = docente['Numero de documento']
            
            # 2. Verificar si ya tiene llave prestada (caso devolución)
            if self._verificar_tiene_llave(numero_documento):
                return self._procesar_devolucion(docente, numero_documento)
            
            # 3. Caso entrega: buscar clase del docente para hoy
            clase = self._buscar_clase_docente_hoy(numero_documento)
            
            if not clase:
                return {
                    'exito': False,
                    'accion': 'error',
                    'mensaje': f'❌ {docente["Nombre"]} no tiene clases programadas hoy'
                }
            
            # 4. Validar tiempo restante para la clase
            return self._validar_y_procesar_entrega(docente, clase)
        
        except Exception as e:
            return {
                'exito': False,
                'accion': 'error',
                'mensaje': f'❌ Error al procesar carnet: {str(e)}'
            }
    
    def _verificar_tiene_llave(self, numero_documento):
        """Verifica si un docente tiene llave prestada"""
        llaves_prestadas = self.llave_service.obtener_llaves_en_prestamo()
        numero_limpio = str(numero_documento).replace('.0', '').strip()
        return any(
            str(llave.get('documento', '')).replace('.0', '').strip() == numero_limpio
            for llave in llaves_prestadas
        )
    
    def _procesar_devolucion(self, docente, numero_documento):
        """Procesa la devolución de una llave"""
        hora_devolucion = datetime.now().strftime('%H:%M:%S')
        exito, mensaje = self.llave_service.procesar_devolucion(
            numero_documento, 
            docente['Nombre']
        )
        
        if exito:
            return {
                'exito': True,
                'accion': 'devolucion',
                'mensaje': mensaje,
                'datos_docente': docente,
                'hora_devolucion': hora_devolucion,
                'requiere_confirmacion': False
            }
        else:
            return {
                'exito': False,
                'accion': 'error',
                'mensaje': mensaje
            }
    
    def _validar_y_procesar_entrega(self, docente, clase):
        """Valida el tiempo y procesa la entrega según corresponda"""
        validacion = self._validar_tiempo_clase(clase)
        
        if validacion['permitir_inmediato']:
            # Entrega automática (falta 30 min o menos, o ya inició)
            exito, mensaje = self.llave_service.procesar_entrega(clase)
            
            if exito:
                return {
                    'exito': True,
                    'accion': 'entrega',
                    'mensaje': mensaje,
                    'datos_docente': docente,
                    'datos_clase': {
                        'Materia': clase.get('materia', 'N/A'),
                        'Aula': clase.get('aula', 'N/A'),
                        'Horario': clase.get('horario', 'N/A')
                    },
                    'requiere_confirmacion': False
                }
            else:
                return {
                    'exito': False,
                    'accion': 'error',
                    'mensaje': mensaje
                }
        else:
            # Requiere confirmación (falta más de 30 min)
            return {
                'exito': False,
                'accion': 'advertencia',
                'mensaje': f'La clase de {docente["Nombre"]} aún no está cerca.\n¿Desea entregar la llave de todas formas?',
                'datos_docente': docente,
                'datos_clase': {
                    'Materia': clase.get('materia', 'N/A'),
                    'Aula': clase.get('aula', 'N/A'),
                    'Horario': clase.get('horario', 'N/A')
                },
                'requiere_confirmacion': True,
                'tiempo_faltante': validacion['tiempo_faltante_str'],
                'callback_confirmar': lambda: self._confirmar_entrega_adelantada(clase)
            }
    
    def _buscar_clase_docente_hoy(self, numero_documento):
        """Busca la próxima clase del docente para hoy"""
        try:
            # Obtener clases del día usando el servicio de programación
            df_clases = self.programacion_service.obtener_clases_del_dia()
            
            if df_clases is None or df_clases.empty:
                return None
            
            # Filtrar por documento del docente
            documento_limpio = str(numero_documento).replace('.0', '').strip()
            df_docente = df_clases[
                df_clases['Número de Documento'].astype(str).str.replace('.0', '').str.strip() == documento_limpio
            ]
            
            if df_docente.empty:
                return None
            
            # Filtrar clases ya procesadas hoy
            clases_procesadas = self.llave_service.obtener_clases_procesadas_hoy()
            clases_procesadas_keys = {
                (str(c['documento']).replace('.0', '').strip(), c.get('horario', ''))
                for c in clases_procesadas
            }
            
            # Filtrar clases no procesadas
            df_pendientes = df_docente[
                ~df_docente.apply(
                    lambda row: (
                        str(row['Número de Documento']).replace('.0', '').strip(),
                        str(row.get('Horario', ''))
                    ) in clases_procesadas_keys,
                    axis=1
                )
            ]
            
            if df_pendientes.empty:
                return None
            
            # Retornar primera clase pendiente convertida a formato interno
            clase = df_pendientes.iloc[0]
            return {
                'nroidenti': clase.get('Número de Documento'),
                'profesor': clase.get('Docente'),
                'aula': clase.get('Aula'),
                'materia': clase.get('Materia de la Clase'),
                'horario': clase.get('Horario'),
                'dia': clase.get('Día')
            }
        
        except Exception as e:
            print(f"Error al buscar clase: {e}")
            return None
    
    def _validar_tiempo_clase(self, clase):
        """
        Valida si está en el tiempo apropiado para entregar la llave
        Threshold: 30 minutos antes de la clase o durante la clase
        
        Returns:
            dict: {
                'permitir_inmediato': bool,
                'minutos_faltantes': int,
                'tiempo_faltante_str': str
            }
        """
        try:
            hora_actual = datetime.now().time()
            
            # Parsear hora de inicio de la clase desde columna 'Horario'
            horario = clase.get('horario', '') or clase.get('Horario', '')
            
            if not horario:
                return {
                    'permitir_inmediato': True,
                    'minutos_faltantes': 0,
                    'tiempo_faltante_str': 'N/A'
                }
            
            # El formato puede ser "HH:MM-HH:MM" o "HH:MM A HH:MM", extraer solo la hora de inicio
            horario_str = str(horario).strip()
            
            # Separar por delimitador
            if '-' in horario_str:
                hora_inicio_str = horario_str.split('-')[0].strip()
            elif ' A ' in horario_str.upper():
                # Manejar "HH:MM A HH:MM"
                partes = [p for p in horario_str.split() if ':' in p]
                hora_inicio_str = partes[0].strip() if partes else horario_str
            else:
                hora_inicio_str = horario_str
            
            # Limpiar espacios y caracteres especiales
            hora_inicio_str = hora_inicio_str.strip()
            # Extraer solo HH:MM
            if len(hora_inicio_str) > 5:
                hora_inicio_str = hora_inicio_str[:5]
            
            # Convertir a objeto time
            try:
                hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            except ValueError:
                # Si falla el parsing, permitir entrega por defecto
                return {
                    'permitir_inmediato': True,
                    'minutos_faltantes': 0,
                    'tiempo_faltante_str': 'N/A (formato inválido)'
                }
            
            # Calcular diferencia en minutos
            ahora = datetime.combine(date.today(), hora_actual)
            inicio_clase = datetime.combine(date.today(), hora_inicio)
            diferencia = inicio_clase - ahora
            minutos_faltantes = int(diferencia.total_seconds() / 60)
            
            # Formatear tiempo faltante
            if minutos_faltantes < 0:
                tiempo_str = "La clase ya inició"
            elif minutos_faltantes < 60:
                tiempo_str = f"{minutos_faltantes} minutos"
            else:
                horas = minutos_faltantes // 60
                minutos = minutos_faltantes % 60
                tiempo_str = f"{horas}h {minutos}min"
            
            # Permitir si falta 30 min o menos, o ya inició
            permitir = minutos_faltantes <= 30
            
            return {
                'permitir_inmediato': permitir,
                'minutos_faltantes': minutos_faltantes,
                'tiempo_faltante_str': tiempo_str
            }
        
        except Exception as e:
            print(f"Error al validar tiempo: {e}")
            # En caso de error, permitir entrega
            return {
                'permitir_inmediato': True,
                'minutos_faltantes': 0,
                'tiempo_faltante_str': 'N/A'
            }
    
    def _confirmar_entrega_adelantada(self, clase):
        """Callback para confirmar entrega adelantada"""
        return self.llave_service.procesar_entrega(clase)
