from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import pandas as pd
from datetime import datetime
from helpers.gestion_excel import obtener_historial_completo, obtener_llaves_pendientes

class VistaInformes:
    def __init__(self, notebook, app):
        self.app = app
        self.frame_informes = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame_informes, text="📊 Informes")
        self.crear_vista_informes()

    def crear_vista_informes(self):
        # Título
        titulo_informes = ttk.Label(self.frame_informes, text="INFORMES Y REPORTES", font=('Segoe UI', 16, 'bold'))
        titulo_informes.pack(pady=(0, 20))
        
        # Frame de controles
        frame_controles = ttk.LabelFrame(self.frame_informes, text="GENERAR INFORMES", padding="15")
        frame_controles.pack(fill='x', pady=(0, 15))
        
        # Botones de informes
        btn_pendientes = ttk.Button(frame_controles, text="📋 Llaves Pendientes", 
                                  command=self.generar_informe_llaves_pendientes)
        btn_pendientes.pack(side='left', padx=(0, 10))
        
        btn_todas = ttk.Button(frame_controles, text="📊 Todas las Entregas", 
                             command=self.generar_informe_todas_entregas)
        btn_todas.pack(side='left', padx=(0, 10))
        
        btn_exportar = ttk.Button(frame_controles, text="💾 Exportar Informe", 
                                command=self.exportar_informe)
        btn_exportar.pack(side='right')
        
        # Área de resultados
        frame_resultados = ttk.LabelFrame(self.frame_informes, text="RESULTADOS", padding="15")
        frame_resultados.pack(fill='both', expand=True)
        
        # Treeview para mostrar resultados
        columns_inf = ('Fecha', 'Profesor', 'Documento', 'Aula', 'Estado', 'Hora Entrega', 'Hora Devolución')
        self.tree_informes = ttk.Treeview(frame_resultados, columns=columns_inf, show='headings')
        
        for col in columns_inf:
            self.tree_informes.heading(col, text=col)
            self.tree_informes.column(col, width=100)
        
        scrollbar_inf = ttk.Scrollbar(frame_resultados, orient='vertical', command=self.tree_informes.yview)
        self.tree_informes.configure(yscrollcommand=scrollbar_inf.set)
        
        self.tree_informes.pack(side='left', fill='both', expand=True)
        scrollbar_inf.pack(side='right', fill='y')

    # ============ FUNCIONES VISTA INFORMES ============
    def generar_informe(self):
        """Función base para generar informes"""
        pass
        
    def generar_informe_llaves_pendientes(self):
        """Generar informe de llaves pendientes de devolución"""
        try:
            pendientes = obtener_llaves_pendientes()
            
            # Limpiar tabla anterior
            for item in self.tree_informes.get_children():
                self.tree_informes.delete(item)
            
            if pendientes.empty:
                messagebox.showinfo("Información", "No hay llaves pendientes de devolución")
                return
            
            # Mostrar en la tabla
            for _, fila in pendientes.iterrows():
                self.tree_informes.insert('', 'end', values=(
                    fila.get('fecha_entrega', ''),
                    fila.get('profesor', ''),
                    str(fila.get('nroidenti', '')).replace('.0', ''),
                    fila.get('aula', ''),
                    fila.get('estado', ''),
                    fila.get('hora_entrega', ''),
                    fila.get('hora_devolucion', '')
                ))
            
            messagebox.showinfo("Éxito", f"Se encontraron {len(pendientes)} llaves pendientes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar informe: {str(e)}")
    
    def generar_informe_todas_entregas(self):
        """Generar informe de todas las entregas"""
        try:
            historial = obtener_historial_completo()
            
            # Limpiar tabla anterior
            for item in self.tree_informes.get_children():
                self.tree_informes.delete(item)
            
            if historial.empty:
                messagebox.showinfo("Información", "No hay registros de entregas")
                return
            
            # Mostrar en la tabla
            for _, fila in historial.iterrows():
                self.tree_informes.insert('', 'end', values=(
                    fila.get('fecha_entrega', ''),
                    fila.get('profesor', ''),
                    str(fila.get('nroidenti', '')).replace('.0', ''),
                    fila.get('aula', ''),
                    fila.get('estado', ''),
                    fila.get('hora_entrega', ''),
                    fila.get('hora_devolucion', '')
                ))
            
            messagebox.showinfo("Éxito", f"Se mostraron {len(historial)} registros")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar informe: {str(e)}")
    
    def generar_informe_por_fecha(self):
        """Generar informe por rango de fechas"""
        pass
        
    def generar_informe_por_profesor(self):
        """Generar informe por profesor específico"""
        pass
        
    def generar_informe_por_aula(self):
        """Generar informe por aula específica"""
        pass
        
    def aplicar_filtros_adicionales(self, df):
        """Aplicar filtros adicionales a los datos"""
        return df
        
    def mostrar_resultados_entregas(self, df):
        """Mostrar resultados de entregas en la tabla"""
        # Limpiar tabla anterior
        for item in self.tree_informes.get_children():
            self.tree_informes.delete(item)
        
        # Mostrar datos
        for _, fila in df.iterrows():
            self.tree_informes.insert('', 'end', values=(
                fila.get('fecha_entrega', ''),
                fila.get('profesor', ''),
                str(fila.get('nroidenti', '')).replace('.0', ''),
                fila.get('aula', ''),
                fila.get('estado', ''),
                fila.get('hora_entrega', ''),
                fila.get('hora_devolucion', '')
            ))
    
    def exportar_informe(self):
        """Exportar el informe actual"""
        try:
            # Obtener datos de la tabla
            items = self.tree_informes.get_children()
            if not items:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            # Crear DataFrame con los datos de la tabla
            datos = []
            for item in items:
                valores = self.tree_informes.item(item)['values']
                datos.append(valores)
            
            columns = ['Fecha', 'Profesor', 'Documento', 'Aula', 'Estado', 'Hora Entrega', 'Hora Devolución']
            df = pd.DataFrame(datos, columns=columns)
            
            # Solicitar ubicación del archivo
            archivo_salida = filedialog.asksaveasfilename(
                title="Exportar Informe",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"informe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if archivo_salida:
                df.to_excel(archivo_salida, index=False)
                messagebox.showinfo("Éxito", f"Informe exportado a: {archivo_salida}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar informe: {str(e)}")
    
    def limpiar_filtros_informe(self):
        """Limpiar todos los filtros del informe"""
        # Limpiar tabla
        for item in self.tree_informes.get_children():
            self.tree_informes.delete(item)
    
    def actualizar_estadisticas_generales(self):
        """Actualizar estadísticas generales"""
        pass
