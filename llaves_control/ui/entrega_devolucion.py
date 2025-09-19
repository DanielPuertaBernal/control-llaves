from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from datetime import datetime
from openpyxl import Workbook
from helpers.gestion_excel import (registrar_entrega, registrar_devolucion, 
                                 obtener_llaves_pendientes, limpiar_numero_documento, 
                                 obtener_historial_completo, verificar_llave_entregada)
from helpers.limpieza_programacion import limpiar_programacion

class VistaEntregaDevolucion:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_entrega = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_entrega, text="🔑 Entrega y Devolución")
        self.crear_vista_entrega_devolucion()

    def crear_vista_entrega_devolucion(self):
        # Título de la vista
        titulo_entrega = ttk.Label(self.frame_entrega, text="GESTIÓN DE LLAVES", font=('Segoe UI', 16, 'bold'))
        titulo_entrega.pack(pady=(0, 20))

        main_container = ttk.Frame(self.frame_entrega)
        main_container.pack(fill='both', expand=True)

        # Columna izquierda - Entrega de llaves
        frame_izq = ttk.LabelFrame(main_container, text="ENTREGA DE LLAVES", padding="15")
        frame_izq.pack(side='left', fill='both', expand=True, padx=(0, 10))

        ttk.Label(frame_izq, text="Buscar Profesor:").pack(anchor='w', pady=(0, 5))
        frame_busqueda = ttk.Frame(frame_izq)
        frame_busqueda.pack(fill='x', pady=(0, 15))
        self.entry_busqueda = ttk.Entry(frame_busqueda, font=('Segoe UI', 11))
        self.entry_busqueda.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_profesor)
        btn_buscar = ttk.Button(frame_busqueda, text="🔍 Buscar", command=self.buscar_profesor, width=10)
        btn_buscar.pack(side='right')

        ttk.Label(frame_izq, text="Seleccione Profesor:").pack(anchor='w', pady=(0, 5))
        list_frame = ttk.Frame(frame_izq)
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        columns = ('Profesor', 'Documento', 'Materia', 'Aula', 'Día', 'Horario')
        self.tree_profesores = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        for col, ancho in zip(columns, [120, 90, 100, 60, 70, 90]):
            self.tree_profesores.heading(col, text=col)
            self.tree_profesores.column(col, width=ancho)
        scrollbar_prof = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_profesores.yview)
        self.tree_profesores.configure(yscrollcommand=scrollbar_prof.set)
        self.tree_profesores.pack(side='left', fill='both', expand=True)
        scrollbar_prof.pack(side='right', fill='y')
        self.info_label = ttk.Label(frame_izq, text="Escriba nombre o número de documento para buscar", foreground="gray")
        self.info_label.pack(pady=(0, 10))
        btn_entregar = ttk.Button(frame_izq, text="🔑 ENTREGAR LLAVE", command=self.entregar_llave_seleccionada, style="Accent.TButton")
        btn_entregar.pack(pady=10, fill='x')
        frame_export = ttk.Frame(frame_izq)
        frame_export.pack(fill='x', pady=(0, 10))
        btn_export_registro = ttk.Button(frame_export, text="📊 Exportar Registro", command=self.exportar_registro_entregas, width=20)
        btn_export_registro.pack(side='left', padx=(0, 5))
        btn_export_prog = ttk.Button(frame_export, text="📄 Exportar Programación", command=self.exportar_programacion_limpia, width=20)
        btn_export_prog.pack(side='right', padx=(5, 0))

        # Columna derecha - Devolución de llaves
        frame_der = ttk.LabelFrame(main_container, text="DEVOLUCIÓN DE LLAVES", padding="15")
        frame_der.pack(side='right', fill='both', expand=True, padx=(10, 0))
        ttk.Label(frame_der, text="Llaves Prestadas Actualmente:").pack(anchor='w', pady=(0, 5))
        list_prestadas_frame = ttk.Frame(frame_der)
        list_prestadas_frame.pack(fill='both', expand=True, pady=(0, 15))
        columns_prestadas = ('Profesor', 'Documento', 'Aula', 'Fecha', 'Hora')
        self.tree_prestadas = ttk.Treeview(list_prestadas_frame, columns=columns_prestadas, show='headings', height=10)
        for col, ancho in zip(columns_prestadas, [120, 90, 60, 80, 70]):
            self.tree_prestadas.heading(col, text=col)
            self.tree_prestadas.column(col, width=ancho)
        scrollbar_prest = ttk.Scrollbar(list_prestadas_frame, orient='vertical', command=self.tree_prestadas.yview)
        self.tree_prestadas.configure(yscrollcommand=scrollbar_prest.set)
        self.tree_prestadas.pack(side='left', fill='both', expand=True)
        scrollbar_prest.pack(side='right', fill='y')
        btn_frame = ttk.Frame(frame_der)
        btn_frame.pack(fill='x', pady=10)
        btn_devolver = ttk.Button(btn_frame, text="↩️ DEVOLVER LLAVE", command=self.devolver_llave_seleccionada, style="Accent.TButton")
        btn_devolver.pack(side='left', fill='x', expand=True, padx=(0, 5))
        btn_actualizar = ttk.Button(btn_frame, text="🔄 ACTUALIZAR", command=self.actualizar_llaves_prestadas, width=12)
        btn_actualizar.pack(side='right')

    # ============ FUNCIONES VISTA ENTREGA/DEVOLUCIÓN ============
    def buscar_profesor(self, event=None):
        """Busca profesores en la programación cargada"""
        if not self.app.programacion or len(self.app.programacion) == 0:
            self.info_label.config(text="⚠️ Primero cargue la programación en la pestaña Programación")
            return
        
        termino = self.entry_busqueda.get().strip().upper()
        
        # Limpiar lista anterior
        for item in self.tree_profesores.get_children():
            self.tree_profesores.delete(item)
        
        if len(termino) < 2:
            self.info_label.config(text="Escriba al menos 2 caracteres para buscar")
            return
        
        # Realizar búsqueda
        resultados = []
        df = self.app.programacion
        
        # Buscar por nombre de profesor
        mask_nombre = df['profesor'].str.contains(termino, na=False, case=False)
        
        # Buscar por número de documento (limpiar primero)
        df_temp = df.copy()
        df_temp['nroidenti_limpio'] = df_temp['nroidenti'].apply(limpiar_numero_documento)
        mask_documento = df_temp['nroidenti_limpio'].str.contains(termino, na=False, case=False)
        
        # Combinar resultados
        mask_final = mask_nombre | mask_documento
        resultados = df[mask_final]
        
        if resultados.empty:
            self.info_label.config(text=f"No se encontraron resultados para '{termino}'")
        else:
            self.info_label.config(text=f"Encontrados {len(resultados)} profesores")
            
            # Mostrar resultados en el Treeview
            for _, fila in resultados.iterrows():
                documento_limpio = limpiar_numero_documento(fila['nroidenti'])
                dia_clase = fila.get('dia', 'N/A')
                self.tree_profesores.insert('', 'end', values=(
                    fila['profesor'],
                    documento_limpio,
                    fila.get('materia', 'N/A'),
                    fila.get('aula', 'N/A'),
                    dia_clase,
                    fila.get('horario', 'N/A')
                ))

    def entregar_llave_seleccionada(self):
        """Entrega la llave del profesor seleccionado"""
        seleccion = self.tree_profesores.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un profesor")
            return
        
        item = self.tree_profesores.item(seleccion[0])
        valores = item['values']
        
        # Verificar si ya tiene llave entregada
        documento = valores[1]
        if verificar_llave_entregada(documento):
            messagebox.showwarning("Advertencia", 
                                 f"El profesor {valores[0]} ya tiene una llave entregada")
            return
        
        # Preparar información para el registro
        info_clase = {
            'nroidenti': documento,
            'profesor': valores[0],
            'materia': valores[2],
            'aula': valores[3],
            'dia': valores[4],
            'horario': valores[5],
            'nro_estudiantes': 0  # Se puede agregar si está en la programación
        }
        
        # Registrar entrega
        if registrar_entrega(info_clase):
            messagebox.showinfo("Éxito", 
                              f"Llave entregada exitosamente al profesor {valores[0]}\nAula: {valores[3]}")
            self.actualizar_llaves_prestadas()
        else:
            messagebox.showerror("Error", "No se pudo registrar la entrega")

    def devolver_llave_seleccionada(self):
        """Devuelve la llave del profesor seleccionado"""
        seleccion = self.tree_prestadas.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione una llave para devolver")
            return
        
        item = self.tree_prestadas.item(seleccion[0])
        valores = item['values']
        documento = valores[1]
        profesor = valores[0]
        
        # Confirmar devolución
        if messagebox.askyesno("Confirmar devolución", 
                             f"¿Confirma la devolución de la llave del profesor {profesor}?"):
            if registrar_devolucion(documento):
                messagebox.showinfo("Éxito", f"Llave devuelta exitosamente por {profesor}")
                self.actualizar_llaves_prestadas()
            else:
                messagebox.showerror("Error", "No se pudo registrar la devolución")

    def actualizar_llaves_prestadas(self):
        """Actualiza la lista de llaves prestadas"""
        # Limpiar lista anterior
        for item in self.tree_prestadas.get_children():
            self.tree_prestadas.delete(item)
        
        # Obtener llaves pendientes
        prestadas = obtener_llaves_pendientes()
        
        if prestadas:  # Si hay elementos en la lista
            for fila in prestadas:
                documento_limpio = limpiar_numero_documento(fila['nroidenti'])
                self.tree_prestadas.insert('', 'end', values=(
                    fila['profesor'],
                    documento_limpio,
                    fila['aula'],
                    fila['fecha_entrega'],
                    fila['hora_entrega']
                ))

    # ============ FUNCIONES DE EXPORTACIÓN ============
    def exportar_registro_entregas(self):
        """Exporta el historial completo de entregas"""
        try:
            # Obtener historial
            historial = obtener_historial_completo()
            
            if not historial:
                messagebox.showwarning("Advertencia", "No hay registros para exportar")
                return
            
            # Solicitar ubicación del archivo
            archivo_salida = filedialog.asksaveasfilename(
                title="Guardar Registro de Entregas",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"registro_entregas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if archivo_salida:
                # Crear workbook con openpyxl
                wb = Workbook()
                
                # Hoja de datos
                ws_datos = wb.active
                ws_datos.title = "Registro_Entregas"
                
                # Agregar encabezados
                if historial:
                    headers = list(historial[0].keys())
                    ws_datos.append(headers)
                    
                    # Agregar datos
                    for registro in historial:
                        row_data = [registro.get(header, '') for header in headers]
                        ws_datos.append(row_data)
                
                wb.save(archivo_salida)
                wb.close()
                
                messagebox.showinfo("Éxito", f"Registro exportado exitosamente a:\n{archivo_salida}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar registro: {str(e)}")

    def exportar_programacion_limpia(self):
        """Exporta la programación actualmente cargada y limpia"""
        if not self.app.programacion or len(self.app.programacion) == 0:
            messagebox.showwarning("Advertencia", "No hay programación cargada para exportar")
            return
        
        try:
            archivo_salida = filedialog.asksaveasfilename(
                title="Guardar Programación Limpia",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"programacion_limpia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if archivo_salida:
                programacion_limpia = limpiar_programacion(self.app.programacion)
                
                # Crear workbook
                wb = Workbook()
                ws_datos = wb.active
                ws_datos.title = "Programacion_Limpia"
                
                # Agregar datos de la programación
                if len(programacion_limpia) > 0:
                    # Convertir DataFrame a lista de listas para openpyxl
                    headers = list(programacion_limpia.columns)
                    ws_datos.append(headers)
                    
                    for _, row in programacion_limpia.iterrows():
                        ws_datos.append(row.tolist())
                
                wb.save(archivo_salida)
                wb.close()
                
                messagebox.showinfo("Éxito", f"Programación exportada exitosamente a:\n{archivo_salida}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar programación: {str(e)}")
