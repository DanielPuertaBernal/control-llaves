"""
Validadores de Dominio - Reglas de negocio
Centraliza lógica de validación específica del negocio
"""
from datetime import datetime, date


class ValidadorLlave:
    """Valida reglas de negocio para llaves"""
    
    @staticmethod
    def validar_informacion_clase(info_clase: dict) -> tuple[bool, str]:
        """Valida que la información de clase tenga campos requeridos"""
        campos_requeridos = ['nroidenti', 'profesor', 'aula']
        campos_faltantes = [c for c in campos_requeridos if c not in info_clase or not info_clase[c]]
        
        if campos_faltantes:
            return False, f"Campos faltantes: {', '.join(campos_faltantes)}"
        return True, "Válido"
    
    @staticmethod
    def validar_tiempo_para_entrega(horario: str) -> tuple[bool, int, str]:
        """
        Valida si es tiempo apropiado para entregar llave.
        Retorna: (permitir_inmediato, minutos_faltantes, tiempo_faltante_str)
        """
        try:
            hora_actual = datetime.now().time()
            
            # Parsear hora de inicio
            horario_str = str(horario).strip()
            if '-' in horario_str:
                hora_inicio_str = horario_str.split('-')[0].strip()
            elif ' A ' in horario_str.upper():
                partes = [p for p in horario_str.split() if ':' in p]
                hora_inicio_str = partes[0].strip() if partes else horario_str
            else:
                hora_inicio_str = horario_str
            
            hora_inicio_str = hora_inicio_str.strip()
            if len(hora_inicio_str) > 5:
                hora_inicio_str = hora_inicio_str[:5]
            
            try:
                hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            except ValueError:
                return True, 0, "N/A (formato inválido)"
            
            # Calcular diferencia
            ahora = datetime.combine(date.today(), hora_actual)
            inicio_clase = datetime.combine(date.today(), hora_inicio)
            diferencia = inicio_clase - ahora
            minutos_faltantes = int(diferencia.total_seconds() / 60)
            
            # Formatear tiempo
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
            
            return permitir, minutos_faltantes, tiempo_str
            
        except Exception:
            return True, 0, "N/A"


class ValidadorDocente:
    """Valida reglas de negocio para docentes"""
    
    @staticmethod
    def validar_documento_unico(numero_documento: str, docentes_existentes: list) -> bool:
        """Valida que un documento no esté duplicado"""
        return numero_documento not in [d['Numero de documento'] for d in docentes_existentes]
    @staticmethod
    def validar_documento(numero_documento: str) -> tuple[bool, str]:
        """Valida que el documento sea válido"""
        if not numero_documento or not str(numero_documento).strip():
            return False, "El número de documento no puede estar vacío"
        
        # Limpiar y validar
        doc_limpio = str(numero_documento).replace('.0', '').strip()
        if not doc_limpio.isdigit():
            return False, "El documento debe contener solo números"
        
        return True, "Válido"
    
    @staticmethod
    def validar_nombre(nombre: str) -> tuple[bool, str]:
        """Valida que el nombre sea válido"""
        if not nombre or not str(nombre).strip():
            return False, "El nombre no puede estar vacío"
        return True, "Válido"


class ValidadorClase:
    """Valida reglas de negocio para clases"""
    
    @staticmethod
    def validar_clase(numero_documento: str, docente: str, 
                     dia: str, horario: str, aula: str) -> tuple[bool, str]:
        """Valida que la clase tenga datos válidos"""
        if not numero_documento or not docente or not dia or not horario or not aula:
            return False, "Faltan campos en la clase"
        return True, "Válido"
    
    @staticmethod
    def es_dia_valido(dia: str) -> bool:
        """Verifica que el día sea válido"""
        dias_validos = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        return dia.upper() in dias_validos
