"""
Vista Unificada de Sistema de Equipos
Incluye gestión, préstamos y devoluciones en pestañas
"""
from tkinter import ttk
from datetime import date, datetime
import pandas as pd

from controllers import DocenteController, EquipoController, PréstamoController, DevolucionController
from presentation.views.equipos.equipos_inventario_view import EquiposInventarioView
from presentation.views.equipos.equipos_movimiento_view import EquiposMovimientoView
from presentation.helpers import ViewHelper


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

    def _crear_interfaz(self):
        """Crea la interfaz con pestañas"""
        frame_top = ttk.Frame(self.frame)
        frame_top.pack(fill='x', pady=(0, 10))

        ttk.Button(
            frame_top,
            text="📥 Exportar Excel",
            command=self._exportar_excel
        ).pack(side='right')

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True)

        self.tab_inventario = ttk.Frame(self.notebook)
        self.tab_movimiento = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_inventario, text="📦 Inventario")
        self.notebook.add(self.tab_movimiento, text="↔️ Movimiento de Equipos")
        
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
            on_actualizar_historial=None
        )

    def cargar_inventario(self):
        """Carga el inventario de equipos"""
        self.inventario_view.cargar_inventario()

    def _on_tab_changed(self, event=None):
        """Auto-actualiza contenido cuando se cambia de pestaña"""
        try:
            tab_actual = self.notebook.select()
            tab_index = self.notebook.index(tab_actual)
            
            if tab_index == 0:  # Pestaña Inventario
                print("[INVENTARIO] Auto-actualizando vista...")
                self.cargar_inventario()
        except Exception as e:
            print(f"Error al actualizar pestaña: {e}")

    def _exportar_excel(self):
        """Exporta inventario y registros de préstamos/devoluciones a Excel (2 hojas)."""
        try:
            # Inventario
            inventario = self.equipo_controller.obtener_inventario()
            inventario_rows = []
            for equipo in inventario:
                eq = equipo.to_dict() if hasattr(equipo, 'to_dict') else equipo
                inventario_rows.append({
                    "codigo_barras": eq.get("codigo_barras", ""),
                    "codigo_inventario": eq.get("codigo_inventario", ""),
                    "nombre": eq.get("nombre", ""),
                    "marca": eq.get("marca", ""),
                    "consecutivo": eq.get("consecutivo", ""),
                    "estado": eq.get("estado", ""),
                    "descripcion": eq.get("descripcion", "")
                })
            df_inventario = pd.DataFrame(inventario_rows)

            # Registro unificado de préstamos y devoluciones
            registros = []
            equipos_procesados = set()  # Para evitar duplicados

            # Obtener todos los préstamos y devoluciones
            prestamos_map = {}  # {prestamo_id: prestamo_data}
            prestamos = self.prestamo_controller.obtener_todos()
            for prestamo in prestamos:
                pr = prestamo.to_dict() if hasattr(prestamo, 'to_dict') else prestamo
                prestamos_map[str(pr.get("_id", ""))] = pr
            
            devoluciones = self.devolucion_controller.obtener_todas()

            devoluciones_map = {}
            for devolucion in devoluciones:
                dev = devolucion.to_dict() if hasattr(devolucion, 'to_dict') else devolucion
                prestamo_id = str(dev.get("prestamo_id", ""))
                for eq_dev in dev.get("equipos_devueltos", []):
                    equipo_id = str(eq_dev.get("equipo_id", ""))
                    devoluciones_map[(prestamo_id, equipo_id)] = {
                        "fecha_devolucion": dev.get("fecha_devolucion", ""),
                        "recibido_por": dev.get("auxiliar_que_recibio", ""),
                        "docente_codigo_nfc": dev.get("docente_codigo_nfc", ""),
                        "docente_nombre": dev.get("docente_nombre", ""),
                        "equipo_nombre": eq_dev.get("equipo_nombre", "")
                    }

            # Primero: procesar todos los préstamos con equipos registrados
            for prestamo_id_str, pr in prestamos_map.items():
                for eq in pr.get("equipos", []):
                    fecha_prestamo = pr.get("fecha_prestamo", "")
                    fecha_prestamo_str = fecha_prestamo.strftime('%d/%m/%Y %H:%M:%S') if isinstance(fecha_prestamo, datetime) else str(fecha_prestamo)

                    equipo_id_str = str(eq.get("equipo_id", ""))

                    devolucion_data = devoluciones_map.get((prestamo_id_str, equipo_id_str))
                    fecha_devolucion_str = ""
                    recibido_por = ""
                    estado = "Entregado"
                    if devolucion_data:
                        fecha_devolucion = devolucion_data.get("fecha_devolucion", "")
                        fecha_devolucion_str = fecha_devolucion.strftime('%d/%m/%Y %H:%M:%S') if isinstance(fecha_devolucion, datetime) else str(fecha_devolucion)
                        recibido_por = devolucion_data.get("recibido_por", "")
                        estado = "Devuelto"

                    registros.append({
                        "prestamo_id": prestamo_id_str,
                        "docente_codigo_nfc": pr.get("docente_codigo_nfc", ""),
                        "docente_nombre": pr.get("docente_nombre", ""),
                        "prestado_por": pr.get("auxiliar_prestamista", ""),
                        "recibido_por": recibido_por,
                        "fecha_prestamo": fecha_prestamo_str,
                        "fecha_devolucion": fecha_devolucion_str,
                        "estado": estado,
                        "equipo_codigo": eq.get("equipo_codigo", ""),
                        "equipo_nombre": eq.get("equipo_nombre", ""),
                        "equipo_marca": eq.get("equipo_marca", ""),
                        "equipo_consecutivo": eq.get("equipo_consecutivo", ""),
                        "equipo_codigo_barras": eq.get("equipo_codigo_barras", "")
                    })
                    equipos_procesados.add((prestamo_id_str, equipo_id_str))

            # Segundo: procesar devoluciones sin equipos en el préstamo
            for (prestamo_id_str, equipo_id_str), dev_data in devoluciones_map.items():
                if (prestamo_id_str, equipo_id_str) in equipos_procesados:
                    continue

                pr = prestamos_map.get(prestamo_id_str, {})

                fecha_devolucion = dev_data.get("fecha_devolucion", "")
                fecha_devolucion_str = fecha_devolucion.strftime('%d/%m/%Y %H:%M:%S') if isinstance(fecha_devolucion, datetime) else str(fecha_devolucion)

                equipo_info = self.equipo_controller.obtener_equipo(equipo_id_str) if equipo_id_str else None
                eq_info = equipo_info.to_dict() if hasattr(equipo_info, 'to_dict') else (equipo_info or {})

                registros.append({
                    "prestamo_id": prestamo_id_str,
                    "docente_codigo_nfc": pr.get("docente_codigo_nfc", "") or dev_data.get("docente_codigo_nfc", ""),
                    "docente_nombre": pr.get("docente_nombre", "") or dev_data.get("docente_nombre", ""),
                    "prestado_por": pr.get("auxiliar_prestamista", ""),
                    "recibido_por": dev_data.get("recibido_por", ""),
                    "fecha_prestamo": "",
                    "fecha_devolucion": fecha_devolucion_str,
                    "estado": "Devuelto",
                    "equipo_codigo": eq_info.get("codigo_inventario", ""),
                    "equipo_nombre": dev_data.get("equipo_nombre", ""),
                    "equipo_marca": eq_info.get("marca", ""),
                    "equipo_consecutivo": eq_info.get("consecutivo", ""),
                    "equipo_codigo_barras": eq_info.get("codigo_barras", "")
                })
                equipos_procesados.add((prestamo_id_str, equipo_id_str))

            df_registros = pd.DataFrame(registros)

            fecha_hoy = date.today().strftime('%Y-%m-%d')
            nombre_archivo = f"Equipos_Prestamos_Devoluciones_{fecha_hoy}.xlsx"

            def exportar_multi(df_placeholder, ruta):
                with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
                    df_inventario.to_excel(writer, sheet_name="Inventario", index=False)
                    df_registros.to_excel(writer, sheet_name="Prestamos_Devoluciones", index=False)

            ViewHelper.exportar_excel_dialogo(
                df_registros if not df_registros.empty else df_inventario,
                exportar_multi,
                nombre_archivo,
                "Guardar Excel de equipos"
            )
        except Exception as e:
            ViewHelper.mostrar_error("Error", f"Error al exportar:\n{str(e)}")

    def detectar_nfc_automático(self, codigo_nfc):
        """Procesa lectura NFC y muestra formulario según estado del docente"""
        if hasattr(self, 'notebook') and hasattr(self, 'tab_movimiento'):
            self.notebook.select(self.tab_movimiento)

        self.movimiento_view.detectar_nfc_automático(codigo_nfc)
