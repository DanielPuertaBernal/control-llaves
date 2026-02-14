"""
Vistas del sistema MVC
Capa de presentación visual
"""
from .main_view import MainView
from .auth.login_view import LoginView
from .llaves.entrega_view import EntregaView
from .llaves.historial_view import HistorialView
from .programacion.programacion_view import ProgramacionView
from .informes.informes_view import InformesView
from .informes.admin_analytics_view import AdminAnalyticsView
from .informes.informes_llaves_admin_view import InformesLlavesAdminView
from .usuarios.usuarios_view import UsuariosView
from .nfc.nfc_view import NFCView
from .equipos.equipos_unificada_view import EquiposUnificadaView

__all__ = [
    'MainView', 'LoginView', 'EntregaView', 'HistorialView', 'ProgramacionView',
    'InformesView', 'AdminAnalyticsView', 'InformesLlavesAdminView', 'UsuariosView',
    'NFCView', 'EquiposUnificadaView'
]
