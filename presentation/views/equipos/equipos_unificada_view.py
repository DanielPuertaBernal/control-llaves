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
                equipo_id = eq.get("_id")
                
                # Verificar si está en préstamo
                estado_prestamo = "Disponible"
                prestado_a = ""
                resultado = self.prestamo_controller.service.verificar_equipo_prestado(equipo_id)
                if resultado:
                    estado_prestamo = "En Préstamo"
                    prestado_a = resultado[1]
                
                inventario_rows.append({
                    "codigo_barras": eq.get("codigo_barras", ""),
                    "codigo_inventario": eq.get("codigo_inventario", ""),
                    "nombre": eq.get("nombre", ""),
                    "marca": eq.get("marca", ""),
                    "consecutivo": eq.get("consecutivo", ""),
                    "estado": estado_prestamo,
                    "prestado_a": prestado_a,
                    "descripcion": eq.get("descripcion", "")
                })
            df_inventario = pd.DataFrame(inventario_rows)

            # Registro unificado: solo usar tabla de Préstamos
            registros = []

            prestamos = self.prestamo_controller.obtener_todos()
            for prestamo in prestamos:
                pr = prestamo.to_dict() if hasattr(prestamo, 'to_dict') else prestamo
                prestamo_id_str = str(pr.get("_id", ""))
                
                for eq in pr.get("equipos", []):
                    fecha_prestamo = pr.get("fecha_prestamo", "")
                    fecha_prestamo_str = fecha_prestamo.strftime('%d/%m/%Y %H:%M:%S') if isinstance(fecha_prestamo, datetime) else str(fecha_prestamo)
                    
                    fecha_devolucion_str = ""
                    recibido_por = ""
                    estado = "Entregado"
                    
                    # Si el equipo tiene fecha de devolución, es que fue devuelto
                    fecha_dev = eq.get("fecha_devolucion")
                    estado_equipo = eq.get("estado_equipo", "entregado")
                    if fecha_dev and estado_equipo == "devuelto":
                        fecha_devolucion_str = fecha_dev.strftime('%d/%m/%Y %H:%M:%S') if isinstance(fecha_dev, datetime) else str(fecha_dev)
                        recibido_por = eq.get("auxiliar_que_recibio_devolucion", "")
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
