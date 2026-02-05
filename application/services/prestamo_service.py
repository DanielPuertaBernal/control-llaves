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
        auxiliar_prestamista: str,
        equipos_a_prestar: List[Tuple[ObjectId, int]],  # [(equipo_id, cantidad), ...]
        dias_plazo: int = None,
        notas: str = None
    ) -> Préstamo:
        """
        Crea un nuevo préstamo de equipos
        
        Args:
            docente_codigo_nfc: Código NFC del docente
            docente_nombre: Nombre del docente
            auxiliar_prestamista: Nombre del auxiliar que hace el préstamo
            equipos_a_prestar: Lista de tuplas (equipo_id, cantidad)
            dias_plazo: Días para devolver (opcional)
            notas: Notas adicionales
            
        Returns:
            Préstamo creado
        """
        
        if not equipos_a_prestar:
            raise ValueError("Debe prestar al menos un equipo")
        
        # Validar disponibilidad de equipos
        for equipo_id, cantidad in equipos_a_prestar:
            equipo = self.equipo_repo.obtener_por_id(equipo_id)
            if not equipo:
                raise ValueError(f"Equipo con ID {equipo_id} no existe")

            if cantidad != 1:
                raise ValueError("El modelo actual usa equipos individuales (cantidad=1)")

            if not equipo.está_disponible():
                raise ValueError(f"Equipo no disponible: {equipo.nombre}")
        
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
        for equipo_id, cantidad in equipos_a_prestar:
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

    def crear_prestamo_simple(
        self,
        docente_codigo_nfc: str,
        docente_nombre: str,
        equipos: List[Dict],
        auxiliar_prestamista: str = "Auxiliar"
    ) -> Préstamo:
        """Crea un préstamo simple con equipos individuales"""
        if not equipos:
            raise ValueError("Debe prestar al menos un equipo")

        prestamo = Préstamo(
            docente_codigo_nfc=docente_codigo_nfc,
            docente_nombre=docente_nombre,
            auxiliar_prestamista=auxiliar_prestamista
        )

        for equipo_data in equipos:
            equipo_id = equipo_data.get('_id') or equipo_data.get('equipo_id') or equipo_data.get('id')
            if isinstance(equipo_id, str):
                equipo_id = ObjectId(equipo_id)

            equipo = self.equipo_repo.obtener_por_id(equipo_id) if equipo_id else None
            if not equipo:
                raise ValueError("Equipo no encontrado para préstamo")

            if not equipo.está_disponible():
                raise ValueError(f"Equipo no disponible: {equipo.nombre}")

            prestamo.agregar_equipo(
                equipo_id=equipo_id,
                nombre=equipo.nombre,
                marca=equipo.marca,
                codigo=equipo.codigo_inventario,
                consecutivo=equipo.consecutivo,
                codigo_barras=equipo.codigo_barras
            )

        return self.prestamo_repo.crear(prestamo)
    
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
        if not equipo:
            raise ValueError(f"Equipo con ID {equipo_id} no existe")
        
        if cantidad != 1:
            raise ValueError("El modelo actual usa equipos individuales (cantidad=1)")

        if not equipo.está_disponible():
            raise ValueError(f"Equipo no disponible: {equipo.nombre}")
        
        # Agregar equipo
        prestamo.agregar_equipo(
            equipo_id=equipo_id,
            nombre=equipo.nombre,
            marca=equipo.marca,
            codigo=equipo.codigo_inventario,
            cantidad=1
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
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de préstamos"""
        
        todos = self.prestamo_repo.obtener_todos()
        activos = self.prestamo_repo.obtener_activos()
        
        total_prestamos = len(todos)
        total_activos = len(activos)
        total_devueltos = len([p for p in todos if p.estado == "completamente_devuelto"])
        total_items_prestados = sum(p.obtener_total_items() for p in todos)
        
        return {
            'total_prestamos': total_prestamos,
            'total_activos': total_activos,
            'total_devueltos': total_devueltos,
            'total_items_prestados': total_items_prestados,
            'promedio_items_por_prestamo': round(total_items_prestados / total_prestamos if total_prestamos > 0 else 0, 2)
        }
