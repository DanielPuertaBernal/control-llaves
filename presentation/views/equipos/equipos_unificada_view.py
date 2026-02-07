"""
Vista Unificada de Sistema de Equipos
Incluye gestión, préstamos, devoluciones e historial en pestañas
"""
from tkinter import ttk

from controllers import DocenteController, EquipoController, PréstamoController, DevolucionController
from presentation.views.equipos.equipos_inventario_view import EquiposInventarioView
from presentation.views.equipos.equipos_movimiento_view import EquiposMovimientoView
from presentation.views.equipos.equipos_historial_view import EquiposHistorialView


class EquiposUnificadaView:
    """Vista unificada para todo el sistema de equipos"""

    def __init__(self, parent_frame, equipo_controller: EquipoController,
                 prestamo_controller: PréstamoController, devolucion_controller: DevolucionController,
                 docente_controller: DocenteController = None):
        self.equipo_controller = equipo_controller
        self.prestamo_controller = prestamo_controller
        self.devolucion_controller = devolucion_controller
        self.docente_controller = docente_controller

        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)

        self._crear_interfaz()

        self.cargar_inventario()
        self.cargar_historial()

    def _crear_interfaz(self):
        """Crea la interfaz con pestañas"""
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True)

        self.tab_inventario = ttk.Frame(self.notebook)
        self.tab_movimiento = ttk.Frame(self.notebook)
        self.tab_historial = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_inventario, text="📦 Inventario")
        self.notebook.add(self.tab_movimiento, text="↔️ Movimiento de Equipos")
        self.notebook.add(self.tab_historial, text="📜 Historial")
        
        # Vincular evento de cambio de pestaña para auto-actualización
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

        self.inventario_view = EquiposInventarioView(
            self.tab_inventario,
            self.equipo_controller,
            self.prestamo_controller
        )

        self.movimiento_view = EquiposMovimientoView(
            self.tab_movimiento,
            self.equipo_controller,
            self.prestamo_controller,
            self.devolucion_controller,
            self.docente_controller,
            on_actualizar_historial=self.cargar_historial
        )

        self.historial_view = EquiposHistorialView(
            self.tab_historial,
            self.prestamo_controller,
            self.devolucion_controller
        )

    def cargar_inventario(self):
        """Carga el inventario de equipos"""
        self.inventario_view.cargar_inventario()

    def cargar_historial(self):
        """Carga historial de préstamos y devoluciones"""
        self.historial_view.cargar_historial()

    def _on_tab_changed(self, event=None):
        """Auto-actualiza contenido cuando se cambia de pestaña"""
        try:
            tab_actual = self.notebook.select()
            tab_index = self.notebook.index(tab_actual)
            
            if tab_index == 0:  # Pestaña Inventario
                print("[INVENTARIO] Auto-actualizando vista...")
                self.cargar_inventario()
            elif tab_index == 2:  # Pestaña Historial
                print("[HISTORIAL] Auto-actualizando vista...")
                self.cargar_historial()
        except Exception as e:
            print(f"Error al actualizar pestaña: {e}")

    def detectar_nfc_automático(self, codigo_nfc):
        """Procesa lectura NFC y muestra formulario según estado del docente"""
        if hasattr(self, 'notebook') and hasattr(self, 'tab_movimiento'):
            self.notebook.select(self.tab_movimiento)

        self.movimiento_view.detectar_nfc_automático(codigo_nfc)
