"""
Servicio de Devoluciones - Lógica de negocio para gestión de devoluciones de equipos
"""
from typing import List, Dict
from bson import ObjectId
from datetime import datetime

from domain.devolucion import Devolución
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
    
    def crear_devolucion(
        self,
        prestamo_id: ObjectId,
        docente_codigo_nfc: str,
        docente_nombre: str,
        equipos: List[Dict],
        auxiliar_que_recibio: str = "Auxiliar"
    ) -> Devolución:
        """Registra una devolución: actualiza estado del equipo en el préstamo en lugar de eliminarlo"""
        from datetime import datetime
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

        equipos_devueltos_ids = []
        
        # Actualizar equipos en el préstamo marcándolos como devueltos
        for equipo_data in equipos:
            equipo_id = ValidationHelper.extraer_equipo_id(equipo_data)
            equipos_devueltos_ids.append(equipo_id)
            
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
            
            # Actualizar el estado del equipo en el préstamo a "devuelto"
            for det_prestamo in prestamo.equipos:
                if str(det_prestamo.equipo_id) == str(equipo_id):
                    det_prestamo.estado_equipo = "devuelto"
                    det_prestamo.fecha_devolucion = datetime.now()
                    det_prestamo.auxiliar_que_recibio_devolucion = auxiliar_que_recibio
                    break

        # Verificar si es devolución completa
        equipos_aun_entregados = [
            eq for eq in prestamo.equipos 
            if eq.estado_equipo == "entregado"
        ]
        
        devolucion.es_devolucion_completa = len(equipos_aun_entregados) == 0
        
        # Marcar préstamo como completamente devuelto si NO quedan equipos entregados
        if devolucion.es_devolucion_completa:
            prestamo.estado = "completamente_devuelto"
        else:
            prestamo.estado = "parcialmente_devuelto"

        devolucion = self.devolucion_repo.crear(devolucion)
        self.prestamo_repo.actualizar(prestamo)

        return devolucion

    
