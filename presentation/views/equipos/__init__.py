"""Submódulo de vistas de equipos."""

from .equipos_unificada_view import EquiposUnificadaView
from .equipos_inventario_view import EquiposInventarioView
from .equipos_movimiento_view import EquiposMovimientoView
from .equipos_historial_view import EquiposHistorialView

__all__ = [
    'EquiposUnificadaView',
    'EquiposInventarioView',
    'EquiposMovimientoView',
    'EquiposHistorialView'
]
