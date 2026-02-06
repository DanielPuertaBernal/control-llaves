"""
Servicio de Devoluciones - Lógica de negocio para gestión de devoluciones de equipos
"""
from typing import List, Optional, Dict, Tuple
from bson import ObjectId
from datetime import datetime

from domain.devolucion import Devolución, DetalleDevolucion
from domain.prestamo import Préstamo
from infrastructure.repositories.devolucion_mongo_repository import DevolucionMongoRepository
from infrastructure.repositories.prestamo_mongo_repository import PréstamoMongoRepository
from infrastructure.repositories.equipo_mongo_repository import EquipoMongoRepository
from application.helpers import ValidationHelper


class DevolucionService:
    """Casos de uso para gestión de devoluciones"""
    
    def __init__(
        self,
        devolucion_repository: DevolucionMongoRepository = None,
        prestamo_repository: PréstamoMongoRepository = None,
        equipo_repository: EquipoMongoRepository = None
    ):
        self.devolucion_repo = devolucion_repository or DevolucionMongoRepository()
        self.prestamo_repo = prestamo_repository or PréstamoMongoRepository()
        self.equipo_repo = equipo_repository or EquipoMongoRepository()
    
    def registrar_devolucion(
        self,
        prestamo_id: ObjectId,
        auxiliar_que_recibio: str,
        equipos_devueltos: List[Tuple[ObjectId, int, str]],  # [(equipo_id, cantidad, estado), ...]
        notas: str = None
    ) -> Tuple[Devolución, Préstamo]:
        """
        Registra la devolución de equipos
        
        Args:
            prestamo_id: ID del préstamo original
            auxiliar_que_recibio: Nombre del auxiliar que recibe
            equipos_devueltos: Lista de tuplas (equipo_id, cantidad, estado)
            notas: Notas adicionales
            
        Returns:
            Tupla (devolución creada, préstamo actualizado)
        """
        
        prestamo = self.prestamo_repo.obtener_por_id(prestamo_id)
        ValidationHelper.validar_prestamo_existe(prestamo, prestamo_id)
        ValidationHelper.validar_prestamo_no_devuelto(prestamo)
        ValidationHelper.validar_lista_no_vacia(equipos_devueltos, "Debe devolver al menos un equipo")
        
        # Crear devolución
        devolucion = Devolución(
            prestamo_id=prestamo_id,
            docente_codigo_nfc=prestamo.docente_codigo_nfc,
            docente_nombre=prestamo.docente_nombre,
            auxiliar_que_recibio=auxiliar_que_recibio,
            notas=notas
        )
        
        # Variables para validar devolucion completa
        total_items_prestados = prestamo.obtener_total_items()
        total_items_devueltos = 0
        
        # Procesar equipos devueltos
        for equipo_id, cantidad, estado in equipos_devueltos:
            equipo = self.equipo_repo.obtener_por_id(equipo_id)
            ValidationHelper.validar_equipo_existe(equipo, equipo_id)
            
            devolucion.agregar_equipo_devuelto(
                equipo_id=equipo_id,
                nombre=equipo.nombre,
                cantidad=cantidad,
                estado=estado
            )
            
            total_items_devueltos += cantidad
            
            # Inventario individual: no se ajusta cantidad, solo se registra devolución
        
        # Determinar si es devolucion completa
        devolucion.es_devolucion_completa = total_items_devueltos >= total_items_prestados
        
        # Actualizar estado del préstamo
        if devolucion.es_devolucion_completa:
            prestamo.estado = "completamente_devuelto"
        else:
            prestamo.estado = "parcialmente_devuelto"
        
        # Guardar devolución y actualizar préstamo
        devolucion = self.devolucion_repo.crear(devolucion)
        self.prestamo_repo.actualizar(prestamo)
        
        return devolucion, prestamo

    def crear_devolucion(
        self,
        prestamo_id: ObjectId,
        docente_codigo_nfc: str,
        docente_nombre: str,
        equipos: List[Dict],
        auxiliar_que_recibio: str = "Auxiliar"
    ) -> Devolución:
        """Registra una devolución completa de equipos individuales"""
        prestamo_id = ValidationHelper.normalizar_object_id(prestamo_id)

        prestamo = self.prestamo_repo.obtener_por_id(prestamo_id)
        ValidationHelper.validar_prestamo_existe(prestamo, prestamo_id)
        ValidationHelper.validar_prestamo_no_devuelto(prestamo)

        devolucion = Devolución(
            prestamo_id=prestamo_id,
            docente_codigo_nfc=docente_codigo_nfc,
            docente_nombre=docente_nombre,
            auxiliar_que_recibio=auxiliar_que_recibio
        )

        if not equipos:
            equipos = prestamo.to_dict().get('equipos', [])

        for equipo_data in equipos:
            equipo_id = ValidationHelper.extraer_equipo_id(equipo_data)

            equipo = self.equipo_repo.obtener_por_id(equipo_id) if equipo_id else None
            nombre = None
            if equipo:
                nombre = equipo.nombre
            else:
                nombre = equipo_data.get('nombre') or equipo_data.get('equipo_nombre', '')

            devolucion.agregar_equipo_devuelto(
                equipo_id=equipo_id,
                nombre=nombre,
                cantidad=1,
                estado="bueno"
            )

        devolucion.es_devolucion_completa = True
        prestamo.estado = "completamente_devuelto"

        devolucion = self.devolucion_repo.crear(devolucion)
        self.prestamo_repo.actualizar(prestamo)

        return devolucion
    
    def obtener_devoluciones_prestamo(self, prestamo_id: ObjectId) -> List[Devolución]:
        """Obtiene todas las devoluciones de un préstamo"""
        return self.devolucion_repo.obtener_por_prestamo(prestamo_id)
    
    def obtener_historial_docente(self, codigo_nfc: str) -> List[Devolución]:
        """Obtiene historial de devoluciones de un docente"""
        return self.devolucion_repo.obtener_por_docente_nfc(codigo_nfc)
    
    def obtener_todas_devoluciones(self) -> List[Devolución]:
        """Obtiene todas las devoluciones"""
        return self.devolucion_repo.obtener_todos()
    
    def obtener_devolucion(self, devolucion_id: ObjectId) -> Optional[Devolución]:
        """Obtiene una devolución específica"""
        return self.devolucion_repo.obtener_por_id(devolucion_id)
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de devoluciones"""
        
        todas = self.devolucion_repo.obtener_todas()
        
        total_devoluciones = len(todas)
        devoluciones_completas = len([d for d in todas if d.es_devolucion_completa])
        devoluciones_parciales = total_devoluciones - devoluciones_completas
        
        total_items_devueltos = sum(d.obtener_total_items_devueltos() for d in todas)
        items_extraviados = sum(
            sum(item.cantidad_devuelta for item in d.equipos_devueltos if item.estado_equipo == "extraviado")
            for d in todas
        )
        
        return {
            'total_devoluciones': total_devoluciones,
            'devoluciones_completas': devoluciones_completas,
            'devoluciones_parciales': devoluciones_parciales,
            'total_items_devueltos': total_items_devueltos,
            'items_extraviados': items_extraviados,
            'porcentaje_completitud': round(
                (devoluciones_completas / total_devoluciones * 100) if total_devoluciones > 0 else 0, 2
            )
        }
