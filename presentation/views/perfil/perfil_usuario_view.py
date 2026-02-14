"""
Vista de Perfil de Usuario
Permite al usuario cambiar sus datos y contraseña
Interfaz intuitiva y segura con validaciones en cada paso
"""
import tkinter as tk
from tkinter import ttk, messagebox
from domain.usuario import Usuario
from application.auth.auth_manager import AuthManager
from presentation.helpers import ViewHelper


class PerfilUsuarioView:
    """Vista para configuración de perfil personal del usuario"""

    def __init__(self, parent_frame, usuario_actual: Usuario, auth_service, callback_actualizar_nombre=None):
        self.usuario_actual = usuario_actual
        self.auth_service = auth_service
        self.callback_actualizar_nombre = callback_actualizar_nombre
        
        self.frame = ttk.Frame(parent_frame, padding="25")
        self.frame.pack(fill='both', expand=True)
        
        self._crear_interfaz()

    def _crear_interfaz(self):
        """Crea interfaz intuitiva con tabs para cada sección"""
        
        # Header con usuario actual
        self._crear_header()
        
        # Notebook (tabs)
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill='both', expand=True, pady=(15, 0))
        
        # Tab 1: Información Personal
        tab_personal = ttk.Frame(notebook, padding="20")
        notebook.add(tab_personal, text="👤 Información Personal")
        self._crear_tab_personal(tab_personal)
        
        # Tab 2: Cambiar Contraseña
        tab_password = ttk.Frame(notebook, padding="20")
        notebook.add(tab_password, text="🔐 Contraseña")
        self._crear_tab_contraseña(tab_password)

    def _crear_header(self):
        """Header con información del usuario actual"""
        header = ttk.Frame(self.frame)
        header.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            header,
            text="Mi Perfil",
            font=('Segoe UI', 18, 'bold')
        ).pack(anchor='w')
        
        info_text = f"Rol: {self.usuario_actual.rol.value.replace('_', ' ').title()}"
        ttk.Label(
            header,
            text=info_text,
            font=('Segoe UI', 10)
        ).pack(anchor='w', pady=(5, 0))

    def _crear_tab_personal(self, parent):
        """Tab para editar información personal"""
        
        # Instrucciones
        ttk.Label(
            parent,
            text="Actualiza tus datos personales",
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        # Frame principal con grid
        content = ttk.Frame(parent)
        content.pack(fill='both', expand=True)
        
        # Campo: Usuario (nombre de usuario único)
        ttk.Label(content, text="Nombre de Usuario:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=8)
        self.entry_usuario = ttk.Entry(content, width=40, font=('Segoe UI', 10))
        self.entry_usuario.insert(0, self.usuario_actual.usuario)
        self.entry_usuario.grid(row=0, column=1, sticky='ew', padx=10)
        ttk.Label(content, text="(único en el sistema)", font=('Segoe UI', 8), foreground='gray').grid(row=0, column=2, sticky='w')
        
        # Campo: Nombre completo
        ttk.Label(content, text="Nombre Completo:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=8)
        self.entry_nombre = ttk.Entry(content, width=40, font=('Segoe UI', 10))
        self.entry_nombre.insert(0, self.usuario_actual.nombre)
        self.entry_nombre.grid(row=1, column=1, sticky='ew', padx=10)
        
        # Campo: Email
        ttk.Label(content, text="Email:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=8)
        self.entry_email = ttk.Entry(content, width=40, font=('Segoe UI', 10))
        self.entry_email.insert(0, self.usuario_actual.email)
        self.entry_email.grid(row=2, column=1, sticky='ew', padx=10)
        ttk.Label(content, text="(ejemplo@correo.com)", font=('Segoe UI', 8), foreground='gray').grid(row=2, column=2, sticky='w')
        
        # Campo: Teléfono
        ttk.Label(content, text="Teléfono/Contacto:", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=8)
        self.entry_telefono = ttk.Entry(content, width=40, font=('Segoe UI', 10))
        self.entry_telefono.insert(0, self.usuario_actual.contacto)
        self.entry_telefono.grid(row=3, column=1, sticky='ew', padx=10)
        
        content.columnconfigure(1, weight=1)
        
        # Botones acción
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(
            btn_frame,
            text="💾 Guardar Cambios",
            command=self._guardar_informacion_personal
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="↺ Descartar",
            command=self._cargar_datos_actuales
        ).pack(side='left')

    def _crear_tab_contraseña(self, parent):
        """Tab para cambiar contraseña con validación"""
        
        # Instrucciones de seguridad
        frame_instrucciones = ttk.LabelFrame(parent, text="🔒 Seguridad", padding="12")
        frame_instrucciones.pack(fill='x', pady=(0, 15))
        
        ttk.Label(
            frame_instrucciones,
            text="Por seguridad, debes confirmar tu contraseña actual antes de establecer una nueva.",
            wraplength=400,
            font=('Segoe UI', 9)
        ).pack(anchor='w')
        
        # Campos de contraseña
        content = ttk.Frame(parent)
        content.pack(fill='both', expand=True)
        
        # Contraseña actual (con checkbox para mostrar)
        ttk.Label(content, text="Contraseña Actual:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=12)
        self.entry_pwd_actual = ttk.Entry(content, width=40, font=('Segoe UI', 10), show='●')
        self.entry_pwd_actual.grid(row=0, column=1, sticky='ew', padx=10)
        
        self.var_mostrar_pwd = tk.BooleanVar()
        chk_mostrar = ttk.Checkbutton(
            content,
            text="Mostrar",
            variable=self.var_mostrar_pwd,
            command=self._toggle_mostrar_contraseña
        )
        chk_mostrar.grid(row=0, column=2, sticky='w')
        
        # Separador visual
        ttk.Separator(content, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=15)
        
        # Nueva contraseña
        ttk.Label(content, text="Nueva Contraseña:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=12)
        self.entry_pwd_nueva = ttk.Entry(content, width=40, font=('Segoe UI', 10), show='●')
        self.entry_pwd_nueva.grid(row=2, column=1, sticky='ew', padx=10)
        
        # Requisitos de contraseña
        frame_requisitos = ttk.Frame(content)
        frame_requisitos.grid(row=3, column=0, columnspan=3, sticky='ew', pady=8)
        
        ttk.Label(
            frame_requisitos,
            text="Requisitos: mínimo 8 caracteres, incluir mayúscula, número y carácter especial",
            font=('Segoe UI', 8),
            foreground='#666666'
        ).pack(anchor='w')
        
        # Confirmar nueva contraseña
        ttk.Label(content, text="Confirmar Nueva Contraseña:", font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=12)
        self.entry_pwd_confirmar = ttk.Entry(content, width=40, font=('Segoe UI', 10), show='●')
        self.entry_pwd_confirmar.grid(row=4, column=1, sticky='ew', padx=10)
        
        content.columnconfigure(1, weight=1)
        
        # Botones acción
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(
            btn_frame,
            text="🔄 Cambiar Contraseña",
            command=self._cambiar_contraseña
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Limpiar",
            command=self._limpiar_campos_contraseña
        ).pack(side='left')

    # ===== MÉTODOS DE ACCIÓN =====
    
    def _cargar_datos_actuales(self):
        """Recarga los datos actuales en los campos"""
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, self.usuario_actual.usuario)
        
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, self.usuario_actual.nombre)
        
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, self.usuario_actual.email)
        
        self.entry_telefono.delete(0, tk.END)
        self.entry_telefono.insert(0, self.usuario_actual.contacto)
        
        messagebox.showinfo("Cancelado", "Se han descartado los cambios")

    def _guardar_informacion_personal(self):
        """Guarda cambios en información personal con validación"""
        try:
            usuario_nuevo = self.entry_usuario.get().strip()
            nombre_nuevo = self.entry_nombre.get().strip()
            email_nuevo = self.entry_email.get().strip()
            telefono_nuevo = self.entry_telefono.get().strip()
            
            # Validaciones básicas
            if not all([usuario_nuevo, nombre_nuevo, email_nuevo, telefono_nuevo]):
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            
            if len(nombre_nuevo) < 3:
                messagebox.showwarning("Error", "El nombre debe tener al menos 3 caracteres")
                return
            
            if '@' not in email_nuevo or '.' not in email_nuevo:
                messagebox.showwarning("Error", "Email inválido")
                return
            
            # Intentar actualizar
            exito = self.auth_service.actualizar_usuario_info(
                self.usuario_actual,
                usuario_nuevo,
                nombre_nuevo,
                email_nuevo,
                telefono_nuevo
            )
            
            if exito:
                # El objeto ya fue actualizado por AuthService, no necesita reasignación
                # Recargar usuario desde sesión para sincronización completa
                usuario_actualizado = self.auth_service.obtener_usuario_actual()
                if usuario_actualizado:
                    self.usuario_actual = usuario_actualizado
                
                # Actualizar nombre en el sidebar si hay callback
                if self.callback_actualizar_nombre:
                    self.callback_actualizar_nombre(self.usuario_actual.nombre)
                
                messagebox.showinfo("✅ Éxito", "Información personal actualizada")
            else:
                messagebox.showerror("Error", "No se pudo actualizar la información")
                
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def _toggle_mostrar_contraseña(self):
        """Muestra/oculta contraseña"""
        mostrar = self.var_mostrar_pwd.get()
        show_char = '' if mostrar else '●'
        self.entry_pwd_actual.config(show=show_char)
        self.entry_pwd_nueva.config(show=show_char)
        self.entry_pwd_confirmar.config(show=show_char)

    def _cambiar_contraseña(self):
        """Cambia contraseña con validación"""
        try:
            pwd_actual = self.entry_pwd_actual.get()
            pwd_nueva = self.entry_pwd_nueva.get()
            pwd_confirmar = self.entry_pwd_confirmar.get()
            
            # Validaciones
            if not pwd_actual:
                messagebox.showwarning("Error", "Debes ingresar tu contraseña actual")
                self.entry_pwd_actual.focus()
                return
            
            if not pwd_nueva:
                messagebox.showwarning("Error", "Debes ingresar una nueva contraseña")
                self.entry_pwd_nueva.focus()
                return
            
            if pwd_nueva != pwd_confirmar:
                messagebox.showwarning("Error", "Las nuevas contraseñas no coinciden")
                self.entry_pwd_confirmar.delete(0, tk.END)
                self.entry_pwd_confirmar.focus()
                return
            
            if len(pwd_nueva) < 8:
                messagebox.showwarning("Error", "La contraseña debe tener al menos 8 caracteres")
                return
            
            # Validar que tenga mayúscula, número y carácter especial
            if not any(c.isupper() for c in pwd_nueva):
                messagebox.showwarning("Error", "La contraseña debe incluir al menos una mayúscula")
                return
            
            if not any(c.isdigit() for c in pwd_nueva):
                messagebox.showwarning("Error", "La contraseña debe incluir al menos un número")
                return
            
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd_nueva):
                messagebox.showwarning("Error", "La contraseña debe incluir un carácter especial (!@#$%^&*)")
                return
            
            # Intentar cambiar contraseña
            exito = self.auth_service.cambiar_contraseña(
                self.usuario_actual,
                pwd_actual,
                pwd_nueva
            )
            
            if exito:
                self._limpiar_campos_contraseña()
                messagebox.showinfo("✅ Éxito", "Contraseña cambiada correctamente")
            else:
                messagebox.showerror("Error", "La contraseña actual es incorrecta")
                self.entry_pwd_actual.delete(0, tk.END)
                self.entry_pwd_actual.focus()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar contraseña: {str(e)}")

    def _limpiar_campos_contraseña(self):
        """Limpia todos los campos de contraseña"""
        self.entry_pwd_actual.delete(0, tk.END)
        self.entry_pwd_nueva.delete(0, tk.END)
        self.entry_pwd_confirmar.delete(0, tk.END)
        self.var_mostrar_pwd.set(False)
        self._toggle_mostrar_contraseña()
