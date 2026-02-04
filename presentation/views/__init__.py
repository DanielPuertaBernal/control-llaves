"""
Vistas del sistema MVC
Capa de presentación visual
"""
from .main_view import MainView
from .entrega_view import EntregaView
from .programacion_view import ProgramacionView
from .historial_view import HistorialView
from .informes_view import InformesView
from .admin_analytics_view import AdminAnalyticsView
from .informes_analytics_view import InformesAnalyticsView

__all__ = ['MainView', 'EntregaView', 'ProgramacionView', 'HistorialView', 'InformesView', 'AdminAnalyticsView', 'InformesAnalyticsView']
