"""Casos de uso para llaves"""
from datetime import date, datetime
from interfaces.llave_repository import LlaveRepository


class LlaveService:
    def __init__(self, repository: LlaveRepository):
        self.repository = repository

    def procesar_entrega(self, info_clase):
        if not self._validar_info_clase(info_clase):
            return False, "Información de clase incompleta"

        exito = self.repository.registrar_entrega(info_clase)
        if exito:
            return True, f"✅ Llave entregada a {info_clase.get('profesor')}"
        return False, "❌ El docente ya tiene una llave prestada"

    def procesar_devolucion(self, nroidenti, nombre_docente=None):
        exito = self.repository.registrar_devolucion(nroidenti)
        if exito:
            docente = nombre_docente if nombre_docente else "el docente"
            return True, f"✅ Llave devuelta por {docente}"
        return False, "❌ No se encontró llave en préstamo para este docente"

    def obtener_llaves_en_prestamo(self):
        return self.repository.obtener_llaves_pendientes()

    def obtener_clases_procesadas_hoy(self):
        fecha_actual = date.today()
        return self.repository.obtener_clases_procesadas_hoy(fecha_actual)

    def obtener_llaves_prestadas_dia(self):
        fecha_actual = date.today()
        return self.repository.obtener_llaves_prestadas_dia(fecha_actual)

    def verificar_tiene_llave(self, nroidenti):
        llaves = self.repository.obtener_llaves_pendientes()
        nroidenti_limpio = str(nroidenti).replace('.0', '')
        for llave in llaves:
            if llave['documento'] == nroidenti_limpio:
                return True
        return False

    def obtener_info_llave(self, nroidenti):
        llaves = self.repository.obtener_llaves_pendientes()
        nroidenti_limpio = str(nroidenti).replace('.0', '')
        for llave in llaves:
            if llave['documento'] == nroidenti_limpio:
                return llave
        return None

    def evaluar_retraso_entrega(self, horario):
        """Evalúa si hay retraso en entrega (> 1 hora después de finalizar clase)."""
        return self.repository.evaluar_retraso_entrega(horario)

    def _validar_info_clase(self, info_clase):
        """Valida que la información de clase tenga campos requeridos"""
        campos_requeridos = ['nroidenti', 'profesor', 'aula']
        return all(campo in info_clase for campo in campos_requeridos)

