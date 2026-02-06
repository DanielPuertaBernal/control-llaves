"""
Vista de Inventario de Equipos
"""
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import os
import shutil

from controllers import EquipoController, PréstamoController
from application.services.barcode_service import BarcodeService


class EquiposInventarioView:
    """Vista para el inventario de equipos"""

    def __init__(self, parent_frame, equipo_controller: EquipoController, prestamo_controller: PréstamoController):
        self.equipo_controller = equipo_controller
        self.prestamo_controller = prestamo_controller

        self.frame = ttk.Frame(parent_frame, padding="15")
        self.frame.pack(fill='both', expand=True)

        self._crear_tab_inventario()

    def _crear_tab_inventario(self):
        """Crea la pestaña de inventario"""
        frame_top = ttk.Frame(self.frame)
        frame_top.pack(fill='x', pady=(0, 10))

        ttk.Label(frame_top, text="Buscar:").pack(side='left')
        self.entrada_busqueda_inv = ttk.Entry(frame_top)
        self.entrada_busqueda_inv.pack(side='left', fill='x', expand=True, padx=(10, 10))
        self.entrada_busqueda_inv.bind('<KeyRelease>', lambda e: self._filtrar_inventario())

        ttk.Button(frame_top, text="🏷️ Imprimir Código", command=self._imprimir_codigo_barras).pack(side='right', padx=5)
        ttk.Button(frame_top, text="➕ Nuevo Equipo", command=self._abrir_formulario_nuevo_equipo).pack(side='right')

        frame_tabla = ttk.Frame(self.frame)
        frame_tabla.pack(fill='both', expand=True)

        self.tree_inventario = ttk.Treeview(
            frame_tabla,
            height=18,
            columns=('codigo', 'nombre', 'marca', 'consecutivo', 'codigo_barras', 'responsable'),
            show='headings'
        )

        self.tree_inventario.heading('codigo', text='Código', anchor='center')
        self.tree_inventario.heading('nombre', text='Nombre', anchor='center')
        self.tree_inventario.heading('marca', text='Marca', anchor='center')
        self.tree_inventario.heading('consecutivo', text='Consecutivo', anchor='center')
        self.tree_inventario.heading('codigo_barras', text='Código Barras', anchor='center')
        self.tree_inventario.heading('responsable', text='Responsable', anchor='center')

        self.tree_inventario.column('codigo', width=80, anchor='center')
        self.tree_inventario.column('nombre', width=120, anchor='center')
        self.tree_inventario.column('marca', width=100, anchor='center')
        self.tree_inventario.column('consecutivo', width=80, anchor='center')
        self.tree_inventario.column('codigo_barras', width=120, anchor='center')
        self.tree_inventario.column('responsable', width=120, anchor='center')

        scrollbar_inv = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_inventario.yview)
        self.tree_inventario.configure(yscrollcommand=scrollbar_inv.set)

        self.tree_inventario.pack(side='left', fill='both', expand=True)
        scrollbar_inv.pack(side='right', fill='y')

        self.tree_inventario.bind('<Double-1>', self._editar_equipo)

    def cargar_inventario(self):
        """Carga el inventario de equipos"""
        try:
            equipos = self.equipo_controller.obtener_inventario()
            prestamos_activos = self.prestamo_controller.obtener_activos() or []
            self.equipos_prestados_ids = set()
            self.equipo_docente_responsable = {}

            for prestamo in prestamos_activos:
                prestamo_dict = prestamo.to_dict() if hasattr(prestamo, 'to_dict') else prestamo
                docente_nombre = prestamo_dict.get('docente_nombre', '')
                for item in prestamo_dict.get('equipos', []):
                    equipo_id = item.get('equipo_id')
                    if equipo_id:
                        self.equipos_prestados_ids.add(str(equipo_id))
                        self.equipo_docente_responsable[str(equipo_id)] = docente_nombre

            self.equipos_dict = {}
            self.equipos_filtrados = []

            for equipo in (equipos or []):
                equipo_dict = equipo.to_dict() if hasattr(equipo, 'to_dict') else equipo
                equipo_id = str(equipo_dict.get('_id', ''))
                self.equipos_dict[equipo_id] = equipo_dict
                self.equipos_filtrados.append(equipo_dict)

            self._actualizar_tabla_inventario()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar inventario: {str(e)}")

    def _filtrar_inventario(self):
        """Filtra el inventario"""
        termino = self.entrada_busqueda_inv.get().lower()

        if not termino:
            self.equipos_filtrados = list(self.equipos_dict.values())
        else:
            self.equipos_filtrados = [
                e for e in self.equipos_dict.values()
                if termino in str(e.get('nombre', '')).lower() or
                   termino in str(e.get('marca', '')).lower() or
                   termino in str(e.get('codigo_inventario', '')).lower() or
                   termino in str(e.get('consecutivo', '')).lower() or
                   termino in str(self.equipo_docente_responsable.get(str(e.get('_id', '')), '')).lower()
            ]

        self._actualizar_tabla_inventario()

    def _actualizar_tabla_inventario(self):
        """Actualiza la tabla de inventario"""
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)

        self.tree_inventario.tag_configure('row_verde', background='#C8E6C9')
        self.tree_inventario.tag_configure('row_amarillo', background='#FFFACD')
        self.tree_inventario.tag_configure('row_rojo', background='#FFB6C1')
        self.tree_inventario.tag_configure('row_gris', background='#E8E8E8')

        for equipo in self.equipos_filtrados:
            codigo = equipo.get('codigo_inventario', '')
            nombre = equipo.get('nombre', '')
            marca = equipo.get('marca', '')
            consecutivo = equipo.get('consecutivo', '')
            codigo_barras = equipo.get('codigo_barras', '')
            estado = equipo.get('estado', 'activo')

            equipo_id = str(equipo.get('_id', ''))

            if estado == 'activo' and hasattr(self, 'equipos_prestados_ids') and equipo_id in self.equipos_prestados_ids:
                estado = 'prestado'

            responsable = ''
            if estado == 'prestado' and equipo_id in self.equipo_docente_responsable:
                responsable = self.equipo_docente_responsable[equipo_id]
            else:
                responsable = 'Disponible'

            if estado == 'dañado':
                tag = 'row_rojo'
            elif estado == 'descartado':
                tag = 'row_gris'
            elif estado == 'prestado':
                tag = 'row_amarillo'
            else:
                tag = 'row_verde'

            self.tree_inventario.insert('', 'end', iid=equipo_id,
                                       values=(codigo, nombre, marca, consecutivo, codigo_barras, responsable),
                                       tags=(tag,))

    def _abrir_formulario_nuevo_equipo(self):
        """Abre formulario para nuevo equipo"""
        ventana = tk.Toplevel(self.frame)
        ventana.title("Nuevo Equipo")
        ventana.geometry("400x400")

        frame = ttk.Frame(ventana, padding="15")
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Código Inventario:").grid(row=0, column=0, sticky='w', pady=5)
        entrada_codigo = ttk.Entry(frame)
        entrada_codigo.grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky='w', pady=5)
        entrada_nombre = ttk.Entry(frame)
        entrada_nombre.grid(row=1, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text="Marca:").grid(row=2, column=0, sticky='w', pady=5)
        entrada_marca = ttk.Entry(frame)
        entrada_marca.grid(row=2, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text="Consecutivo:").grid(row=3, column=0, sticky='w', pady=5)
        entrada_consecutivo = ttk.Entry(frame)
        entrada_consecutivo.grid(row=3, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text="Descripción:").grid(row=4, column=0, sticky='w', pady=5)
        entrada_desc = ttk.Entry(frame)
        entrada_desc.grid(row=4, column=1, sticky='ew', pady=5)

        frame.columnconfigure(1, weight=1)

        def guardar():
            try:
                codigo = entrada_codigo.get().strip()
                nombre = entrada_nombre.get().strip()
                marca = entrada_marca.get().strip()
                consecutivo = entrada_consecutivo.get().strip()
                desc = entrada_desc.get().strip()

                if not all([codigo, nombre, marca, consecutivo]):
                    messagebox.showwarning("Advertencia", "Completa todos los campos obligatorios")
                    return

                equipo = self.equipo_controller.registrar_equipo(
                    nombre, marca, consecutivo, codigo, desc
                )
                messagebox.showinfo("Éxito", f"Equipo {equipo.nombre} #{equipo.consecutivo} registrado")
                ventana.destroy()
                self.cargar_inventario()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        frame_botones = ttk.Frame(ventana)
        frame_botones.pack(fill='x', padx=15, pady=15)

        ttk.Button(frame_botones, text="Guardar", command=guardar).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=ventana.destroy).pack(side='left')

    def _editar_equipo(self, event):
        """Edita un equipo"""
        items = self.tree_inventario.selection()
        if not items:
            return

        equipo_id_str = items[0]
        equipo = self.equipos_dict.get(equipo_id_str, {})

        ventana = tk.Toplevel(self.frame)
        ventana.title("Editar Equipo")
        ventana.geometry("400x400")

        frame = ttk.Frame(ventana, padding="15")
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky='w', pady=5)
        entrada_nombre = ttk.Entry(frame)
        entrada_nombre.insert(0, equipo.get('nombre', ''))
        entrada_nombre.grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text="Marca:").grid(row=1, column=0, sticky='w', pady=5)
        entrada_marca = ttk.Entry(frame)
        entrada_marca.insert(0, equipo.get('marca', ''))
        entrada_marca.grid(row=1, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text="Consecutivo:").grid(row=2, column=0, sticky='w', pady=5)
        entrada_consecutivo = ttk.Entry(frame)
        entrada_consecutivo.insert(0, str(equipo.get('consecutivo', '')))
        entrada_consecutivo.grid(row=2, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text="Descripción:").grid(row=3, column=0, sticky='w', pady=5)
        entrada_desc = ttk.Entry(frame)
        entrada_desc.insert(0, equipo.get('descripcion', ''))
        entrada_desc.grid(row=3, column=1, sticky='ew', pady=5)

        frame.columnconfigure(1, weight=1)

        def guardar():
            try:
                from bson import ObjectId

                nombre = entrada_nombre.get().strip()
                marca = entrada_marca.get().strip()
                consecutivo = entrada_consecutivo.get().strip()
                desc = entrada_desc.get().strip()

                if not consecutivo:
                    messagebox.showwarning("Advertencia", "El consecutivo es obligatorio")
                    return

                equipo_id = ObjectId(equipo_id_str)

                self.equipo_controller.actualizar_equipo(
                    equipo_id,
                    nombre=nombre,
                    marca=marca,
                    consecutivo=consecutivo,
                    descripcion=desc
                )
                messagebox.showinfo("Éxito", "Equipo actualizado")
                ventana.destroy()
                self.cargar_inventario()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        frame_botones = ttk.Frame(ventana)
        frame_botones.pack(fill='x', padx=15, pady=15)

        ttk.Button(frame_botones, text="Guardar", command=guardar).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=ventana.destroy).pack(side='left')

    def _imprimir_codigo_barras(self):
        """Imprime código de barras para el equipo seleccionado"""
        items = self.tree_inventario.selection()
        if not items:
            messagebox.showwarning("Advertencia", "Selecciona un equipo para imprimir su código de barras")
            return

        equipo_id_str = items[0]
        equipo = self.equipos_dict.get(equipo_id_str, {})

        if not equipo:
            messagebox.showerror("Error", "No se encontró el equipo")
            return

        codigo_barras = equipo.get('codigo_barras', '')
        nombre = equipo.get('nombre', 'articulo')
        consecutivo = equipo.get('consecutivo', '0')

        if not codigo_barras:
            messagebox.showerror("Error", "El equipo no tiene código de barras asignado")
            return

        try:
            servicio = BarcodeService()
            ruta_barcode_temp = servicio.generar_codigo_barras(codigo_barras)

            if not ruta_barcode_temp:
                messagebox.showerror("Error", "No se pudo generar el código de barras")
                return

            nombre_archivo = f"{nombre}_{consecutivo}_{codigo_barras.replace('-', '_')}.png"

            archivo_destino = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("Imágenes PNG", "*.png")],
                initialfile=nombre_archivo
            )

            if not archivo_destino:
                try:
                    os.remove(ruta_barcode_temp)
                except:
                    pass
                return

            shutil.copy(ruta_barcode_temp, archivo_destino)

            try:
                os.remove(ruta_barcode_temp)
            except:
                pass

            messagebox.showinfo("Éxito", f"Código de barras guardado en:\n{archivo_destino}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar código de barras: {str(e)}")
