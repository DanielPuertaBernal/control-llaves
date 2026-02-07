"""
Servicio de Préstamos - Lógica de negocio para gestión de préstamos de equipos
"""
from typing import List, Optional, Dict, Tuple
from bson import ObjectId
from datetime import datetime, timedelta

from domain.prestamo import Préstamo, DetallePréstamo
from domain.equipo import Equipo
from infrastructure.repositories.prestamo_mongo_repository import PréstamoMongoRepository
from infrastructure.repositories.equipo_mongo_repository import EquipoMongoRepository
from application.helpers import ValidationHelper


class PréstamoService:
    """Casos de uso para gestión de préstamos"""
    
    def __init__(
        self,
        prestamo_repository: PréstamoMongoRepository = None,
        equipo_repository: EquipoMongoRepository = None
    ):
        self.prestamo_repo = prestamo_repository or PréstamoMongoRepository()
        self.equipo_repo = equipo_repository or EquipoMongoRepository()
    
    def crear_prestamo(
        self,
        docente_codigo_nfc: str,
        docente_nombre: str,
        equipos: List,  # Acepta List[Tuple[ObjectId, int]] o List[Dict]
        auxiliar_prestamista: str = "Auxiliar",
        dias_plazo: int = None,
        notas: str = None
    ) -> Préstamo:
        """
        Crea un nuevo préstamo de equipos
        
        Acepta múltiples formatos de entrada para equipos:
        - Lista de tuplas: [(equipo_id, cantidad), ...]
        - Lista de diccionarios: [{"_id": ..., "equipo_id": ..., "id": ...}, ...]
        
        Args:
            docente_codigo_nfc: Código NFC del docente
            docente_nombre: Nombre del docente
            equipos: Lista de equipos (tuplas o diccionarios)
            auxiliar_prestamista: Nombre del auxiliar que hace el préstamo (default: "Auxiliar")
            dias_plazo: Días para devolver (opcional)
            notas: Notas adicionales
            
        Returns:
            Préstamo creado
        """
        
        if not equipos:
            raise ValueError("Debe prestar al menos un equipo")
        
        # Normalizar equipos a lista de dicts
        equipos_normalizados = self._normalizar_equipos(equipos)
        
        # Validar disponibilidad de equipos
        self._validar_equipos_disponibles(equipos_normalizados)
        
        # Crear préstamo
        prestamo = Préstamo(
            docente_codigo_nfc=docente_codigo_nfc,
            docente_nombre=docente_nombre,
            auxiliar_prestamista=auxiliar_prestamista,
            notas=notas
        )
        
        if dias_plazo:
            prestamo.fecha_prevista_devolucion = datetime.now() + timedelta(days=dias_plazo)
        
        # Agregar equipos al préstamo
        for equipo_data in equipos_normalizados:
            equipo_id = equipo_data['equipo_id']
            equipo = self.equipo_repo.obtener_por_id(equipo_id)
            
            prestamo.agregar_equipo(
                equipo_id=equipo_id,
                nombre=equipo.nombre,
                marca=equipo.marca,
                codigo=equipo.codigo_inventario,
                consecutivo=equipo.consecutivo,
                codigo_barras=equipo.codigo_barras
            )
        
        # Guardar préstamo
        return self.prestamo_repo.crear(prestamo)
    
    def _normalizar_equipos(self, equipos: List) -> List[Dict]:
        """
        Convierte múltiples formatos de entrada a formato estándar
        
        Args:
            equipos: Lista de tuplas [(equipo_id, cantidad)] o dicts
            
        Returns:
            Lista de diccionarios [{"equipo_id": ObjectId, "cantidad": int}]
        """
        if not equipos:
            return []
        
        resultado = []
        for item in equipos:
            if isinstance(item, tuple):
                # Formato: (equipo_id, cantidad)
                equipo_id, cantidad = item
                resultado.append({"equipo_id": equipo_id, "cantidad": cantidad})
            elif isinstance(item, dict):
                # Formato: {"_id": ..., "equipo_id": ..., "id": ...}
                equipo_id = ValidationHelper.extraer_equipo_id(item)
                cantidad = item.get('cantidad', 1)
                resultado.append({"equipo_id": equipo_id, "cantidad": cantidad})
            else:
                raise ValueError(f"Formato de equipo no reconocido: {type(item)}")
        
        return resultado
    
    def _validar_equipos_disponibles(self, equipos_normalizados: List[Dict]) -> None:
        """
        Valida que todos los equipos existan y estén disponibles
        
        Args:
            equipos_normalizados: Lista de dicts con equipo_id y cantidad
            
        Raises:
            ValueError: Si algún equipo no existe, no está disponible o cantidad != 1
        """
        for equipo_data in equipos_normalizados:
            equipo_id = equipo_data['equipo_id']
            cantidad = equipo_data.get('cantidad', 1)
            
            equipo = self.equipo_repo.obtener_por_id(equipo_id)
            ValidationHelper.validar_equipo_existe(equipo, equipo_id)
            ValidationHelper.validar_cantidad_individual(cantidad)
            ValidationHelper.validar_equipo_disponible(equipo)
    
    def obtener_prestamos_activos(self) -> List[Préstamo]:
        """Obtiene todos los préstamos activos"""
        return self.prestamo_repo.obtener_activos()
    
    def obtener_historial_docente(self, codigo_nfc: str) -> List[Préstamo]:
        """Obtiene historial de préstamos de un docente"""
        return self.prestamo_repo.obtener_por_docente_nfc(codigo_nfc)
    
    def obtener_prestamos_activos_docente(self, codigo_nfc: str) -> List[Préstamo]:
        """Obtiene préstamos activos de un docente"""
        return self.prestamo_repo.obtener_activos_por_docente(codigo_nfc)
    
    def obtener_prestamo(self, prestamo_id: ObjectId) -> Optional[Préstamo]:
        """Obtiene un préstamo específico"""
        return self.prestamo_repo.obtener_por_id(prestamo_id)
    
    def obtener_todos_prestamos(self) -> List[Préstamo]:
        """Obtiene todos los préstamos (histórico completo)"""
        return self.prestamo_repo.obtener_todos()
    
    def agregar_equipo_prestamo(
        self,
        prestamo_id: ObjectId,
        equipo_id: ObjectId,
        cantidad: int
    ) -> Optional[Préstamo]:
        """Agrega más equipo a un préstamo activo"""
        
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        prestamo = self.prestamo_repo.obtener_por_id(prestamo_id)
        if not prestamo:
            return None
        
        if prestamo.estado not in ["activo", "parcialmente_devuelto"]:
            raise ValueError("Solo se puede agregar equipos a préstamos activos")
        
        equipo = self.equipo_repo.obtener_por_id(equipo_id)
        ValidationHelper.validar_equipo_existe(equipo, equipo_id)
        ValidationHelper.validar_cantidad_individual(cantidad)
        ValidationHelper.validar_equipo_disponible(equipo)
        
        # Agregar equipo
        prestamo.agregar_equipo(
            equipo_id=equipo_id,
            nombre=equipo.nombre,
            marca=equipo.marca,
            codigo=equipo.codigo_inventario,
            consecutivo=equipo.consecutivo,
            codigo_barras=equipo.codigo_barras
        )
        
        # Actualizar préstamo
        self.prestamo_repo.actualizar(prestamo)
        
        return prestamo
    
    def marcar_vencido(self, prestamo_id: ObjectId) -> Optional[Préstamo]:
        """Marca un préstamo como vencido"""
        
        prestamo = self.prestamo_repo.obtener_por_id(prestamo_id)
        if not prestamo:
            return None
        
        if prestamo.estado == "completamente_devuelto":
            raise ValueError("No se puede marcar como vencido un préstamo devuelto")
        
        prestamo.estado = "vencido"
        self.prestamo_repo.actualizar(prestamo)
        
        return prestamo
    
    def verificar_equipo_prestado(self, equipo_id: ObjectId) -> Optional[Tuple[bool, str]]:
        """
        Verifica si un equipo está actualmente en préstamo
        
        Args:
            equipo_id: ID del equipo a verificar
            
        Returns:
            Tupla (está_prestado, nombre_docente) o None si no está prestado
        """
        prestamos_activos = self.prestamo_repo.obtener_activos()
        
        for prestamo in prestamos_activos:
            prestamo_dict = prestamo.to_dict() if hasattr(prestamo, 'to_dict') else prestamo
            equipos = prestamo_dict.get('equipos', [])
            
            for equipo_detalle in equipos:
                equipo_detalle_id = equipo_detalle.get('equipo_id')
                if str(equipo_detalle_id) == str(equipo_id):
                    docente_nombre = prestamo_dict.get('docente_nombre', 'Docente desconocido')
                    return (True, docente_nombre)
        
        return None
