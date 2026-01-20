"""
Vista de entrega y devolución de llaves
Maneja solo la presentación de la programación del día
"""
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from controllers import LlaveController
from services import PaginacionService, TablaService
from views.components import BuscadorComponent


class EntregaView:
    """Vista para entrega y devolución de llaves"""
    
    def __init__(self, parent_frame, programacion_controller):
        self.programacion_controller = programacion_controller
        self.llave_controller = LlaveController()
        
        # Servicios
        self.paginacion_service = PaginacionService(items_por_pagina=15)
        
        # Frame principal - ahora recibe el parent directamente
        self.frame = ttk.Frame(parent_frame, padding="20")
        self.frame.pack(fill='both', expand=True)
        
        # Datos actuales
        self.datos_filtrados = []
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Cargar datos iniciales
        self.cargar_clases_del_dia()
        
        # Actualización automática cada 10 minutos
        self._iniciar_actualizacion_automatica()
    
    def _crear_interfaz(self):
        """Crea los componentes visuales"""
        # Componente de búsqueda
        self.buscador = BuscadorComponent(
            self.frame,
            callback_busqueda=self._realizar_busqueda,
            label_texto="Buscar:"
        )
        
        # Frame de paginación con botón actualizar
        frame_paginacion = ttk.Frame(self.frame)
        frame_paginacion.pack(fill='x', pady=(0, 15))
        
        # Botón actualizar a la izquierda
        btn_actualizar = ttk.Button(frame_paginacion, text="🔄 Actualizar", command=self.cargar_clases_del_dia)
        btn_actualizar.pack(side='left', padx=(0, 20))
        
        # Información de registros
        self.label_info = ttk.Label(frame_paginacion, text="0 registros", font=('Segoe UI', 9))
        self.label_info.pack(side='left')
        
        # Controles de paginación compactos a la derecha
        self.btn_siguiente = ttk.Button(frame_paginacion, text="▶", width=3, command=self._pagina_siguiente)
        self.btn_siguiente.pack(side='right', padx=(5, 0))
        
        self.label_pagina = ttk.Label(frame_paginacion, text="Página 1 de 1", font=('Segoe UI', 9))
        self.label_pagina.pack(side='right', padx=8)
        
        self.btn_anterior = ttk.Button(frame_paginacion, text="◀", width=3, command=self._pagina_anterior)
        self.btn_anterior.pack(side='right', padx=(0, 5))
        
        # Tabla
        frame_tabla = ttk.Frame(self.frame)
        frame_tabla.pack(fill='both', expand=True, pady=(0, 15))
        
        self.tree = ttk.Treeview(frame_tabla)
        TablaService.configurar_treeview(self.tree, 'entrega')
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Evento de doble clic
        self.tree.bind('<Double-1>', self._on_doble_click)
    
    def cargar_clases_del_dia(self):
        """Carga las clases del día desde el controlador"""
        df = self.programacion_controller.obtener_clases_del_dia()

        # Si no hay datos, intentar recargar programación guardada una sola vez
        if df.empty:
            exito, _, _ = self.programacion_controller.cargar_programacion_inicial()
            if exito:
                df = self.programacion_controller.obtener_clases_del_dia()

        if df.empty:
            messagebox.showwarning("Advertencia", "No hay programación cargada o no hay clases para hoy.")
            return

        self.datos_filtrados = df
        self.paginacion_service.actualizar_datos(df)
        self._actualizar_vista()
    
    def _realizar_busqueda(self):
        """Filtra los datos según el término de búsqueda"""
        termino = self.buscador.obtener_termino()
        
        if not termino:
            # Sin búsqueda, mostrar todos los datos originales
            self.paginacion_service.actualizar_datos(self.datos_filtrados)
            self._actualizar_vista()
            return
        
        # Normalizar término de búsqueda
        termino_normalizado = self.buscador.normalizar_texto(termino)
        
        # Filtrar el dataframe con normalización
        df_filtrado = self.datos_filtrados[
            self.datos_filtrados['Docente'].apply(lambda x: termino_normalizado in self.buscador.normalizar_texto(str(x))) |
            self.datos_filtrados['Materia de la Clase'].apply(lambda x: termino_normalizado in self.buscador.normalizar_texto(str(x))) |
            self.datos_filtrados['Aula'].apply(lambda x: termino_normalizado in self.buscador.normalizar_texto(str(x))) |
            self.datos_filtrados['Número de Documento'].apply(lambda x: termino_normalizado in self.buscador.normalizar_texto(str(x))) 
        ]
        
        # Actualizar paginación con datos filtrados
        self.paginacion_service.actualizar_datos(df_filtrado)
        self._actualizar_vista()
    
    def _pagina_anterior(self):
        """Va a página anterior"""
        self.paginacion_service.pagina_anterior()
        self._actualizar_vista()
    
    def _pagina_siguiente(self):
        """Va a página siguiente"""
        self.paginacion_service.pagina_siguiente()
        self._actualizar_vista()
    
    def _actualizar_vista(self):
        """Actualiza toda la vista"""
        # Obtener datos de página actual
        datos_pagina, inicio, fin = self.paginacion_service.obtener_pagina_actual()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Llenar tabla
        if hasattr(datos_pagina, 'empty'):
            # Es un DataFrame de pandas
            if not datos_pagina.empty:
                for _, row in datos_pagina.iterrows():
                    valores = (
                        str(row.get('Número de Documento', '')).replace('.0', ''),
                        row.get('Docente', ''),
                        row.get('Aula', ''),
                        row.get('Horario', ''),
                        row.get('Materia de la Clase', '')
                    )
                    self.tree.insert('', 'end', values=valores)
        elif len(datos_pagina) > 0:
            # Es una lista
            for row in datos_pagina:
                valores = (
                    str(row.get('Número de Documento', '')).replace('.0', ''),
                    row.get('Docente', ''),
                    row.get('Aula', ''),
                    row.get('Horario', ''),
                    row.get('Materia de la Clase', '')
                )
                self.tree.insert('', 'end', values=valores)
        
        # Actualizar labels
        info = self.paginacion_service.obtener_info_paginacion()
        self.label_pagina.config(text=f"Página {info['pagina_actual']} de {info['total_paginas']}")
        self.label_info.config(text=f"{info['total_items']} registros")
        
        # Actualizar botones
        self.btn_anterior.config(state='normal' if info['tiene_anterior'] else 'disabled')
        self.btn_siguiente.config(state='normal' if info['tiene_siguiente'] else 'disabled')
    
    def _on_doble_click(self, event):
        """Maneja doble clic para entregar llave"""
        try:
            seleccion = self.tree.selection()
            if not seleccion:
                return
            
            valores = self.tree.item(seleccion[0], 'values')
            
            # Confirmar entrega
            if not messagebox.askyesno(
                "Confirmar Entrega",
                f"¿Entregar llave para:\n\n"
                f"Docente: {valores[1]}\n"
                f"Aula: {valores[2]}\n"
                f"Horario: {valores[3]}"
            ):
                return
            
            # Obtener facultad
            facultad = self.programacion_controller.obtener_facultad_desde_programacion(
                valores[0], valores[1], valores[2], valores[4]
            )
            
            # Preparar información
            info_clase = {
                'nroidenti': valores[0],
                'profesor': valores[1],
                'aula': valores[2],
                'horario': valores[3],
                'materia': valores[4],
                'facultad': facultad,
                'dia': self._obtener_dia_actual()
            }
            
            # Procesar entrega
            exito, mensaje = self.llave_controller.procesar_entrega(info_clase)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_clases_del_dia()
            else:
                messagebox.showwarning("Advertencia", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar entrega: {str(e)}")
    
    def _obtener_dia_actual(self):
        """Obtiene el día actual en español"""
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        return dias[datetime.now().weekday()]
    
    def _iniciar_actualizacion_automatica(self):
        """Inicia actualización automática cada 10 minutos"""
        def actualizar():
            if not self.buscador.obtener_termino():
                self.cargar_clases_del_dia()
            self.frame.after(600000, actualizar)  # 10 minutos
        
        self.frame.after(600000, actualizar)
