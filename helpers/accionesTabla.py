from tkinter import messagebox

class AccionesTabla:
    """
    Componente unificado para manejar acciones de doble clic en tablas
    Proporciona funcionalidad común para confirmar acciones sobre registros
    """
    
    def __init__(self, treeview, callback_accion, callback_recarga=None):
        """
        Args:
            treeview: Widget TreeView
            callback_accion: Función que ejecuta la acción principal (entrega/devolución)
            callback_recarga: Función opcional para recargar datos después de la acción
        """
        self.treeview = treeview
        self.callback_accion = callback_accion
        self.callback_recarga = callback_recarga
        
        # Configurar eventos
        self.ConfigurarEventos()
    
    def ConfigurarEventos(self):
        """Configura los eventos de la tabla"""
        self.treeview.bind('<Double-1>', self.OnDobleClick)
        self.treeview.bind('<Button-1>', self.OnClickSimple)
    
    def OnDobleClick(self, event):
        """Maneja el evento de doble clic"""
        try:
            # Verificar que hay un item seleccionado
            seleccion = self.treeview.selection()
            if not seleccion:
                return
            
            item_seleccionado = seleccion[0]
            valores = self.treeview.item(item_seleccionado, 'values')
            
            if not valores:
                return
            
            # Ejecutar la acción principal
            self._EjecutarAccion(valores)
            
        except IndexError:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro de la tabla.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la acción: {str(e)}")
    
    def OnClickSimple(self, event):
        """Maneja el clic simple para detectar columnas especiales"""
        try:
            # Identificar qué columna se clickeó
            columna = self.treeview.identify_column(event.x)
            item = self.treeview.identify_row(event.y)
            
            # Si es la columna de acción (6) y hay un item seleccionado
            if columna == '#6' and item:  # #6 corresponde a la columna "Acción"
                # Seleccionar el item y simular doble clic
                self.treeview.selection_set(item)
                self.OnDobleClick(event)
                
        except Exception as e:
            print(f"Error en click tabla: {e}")
    
    def _EjecutarAccion(self, valores):
        """
        Ejecuta la acción principal usando el callback
        
        Args:
            valores: Tupla con los valores de la fila seleccionada
        """
        try:
            # Ejecutar callback de acción
            exito = self.callback_accion(valores)
            
            # Si fue exitoso y hay callback de recarga, ejecutarlo
            if exito and self.callback_recarga:
                self.callback_recarga()
                
        except Exception as e:
            print(f"Error ejecutando acción: {e}")
    
    def ActualizarCallbacks(self, callback_accion=None, callback_recarga=None):
        """
        Actualiza los callbacks
        
        Args:
            callback_accion: Nuevo callback de acción (opcional)
            callback_recarga: Nuevo callback de recarga (opcional)
        """
        if callback_accion:
            self.callback_accion = callback_accion
        if callback_recarga:
            self.callback_recarga = callback_recarga


class ConfirmadorAcciones:
    """
    Utilidad para crear diálogos de confirmación estandarizados
    """
    
    @staticmethod
    def ConfirmarEntregaLlave(documento, docente, aula, horario, materia):
        """
        Muestra diálogo de confirmación para entrega de llave
        
        Returns:
            bool: True si el usuario confirma
        """
        return messagebox.askyesno(
            "Confirmar Entrega", 
            f"¿Confirmar entrega de llave para:\n\n"
            f"Docente: {docente}\n"
            f"Documento: {documento}\n"
            f"Aula: {aula}\n"
            f"Horario: {horario}\n"
            f"Materia: {materia}"
        )
    
    @staticmethod
    def ConfirmarDevolucionLlave(documento, docente):
        """
        Muestra diálogo de confirmación para devolución de llave
        
        Returns:
            bool: True si el usuario confirma
        """
        return messagebox.askyesno(
            "Confirmar Devolución",
            f"¿Confirmar devolución de llave?\n\n"
            f"Docente: {docente}\n"
            f"Documento: {documento}\n\n"
            f"Se registrará la fecha y hora de devolución."
        )
    
    @staticmethod
    def MostrarExito(mensaje):
        """Muestra mensaje de éxito"""
        messagebox.showinfo("Éxito", mensaje)
    
    @staticmethod
    def MostrarError(mensaje):
        """Muestra mensaje de error"""
        messagebox.showerror("Error", mensaje)
    
    @staticmethod
    def MostrarAdvertencia(mensaje):
        """Muestra mensaje de advertencia"""
        messagebox.showwarning("Advertencia", mensaje)