"""
Vista de Gestión de Usuarios - Solo Admin
"""
import tkinter as tk
from tkinter import ttk, messagebox
from domain.usuario import RolUsuario
from application.service_factory import ServiceFactory


class UsuariosView:
    """Vista para gestión de usuarios (solo ADMIN_PROG)"""
    
    def __init__(self, parent, auth_service):
        """
        Inicializa la vista de usuarios
        
        Args:
            parent: Frame contenedor
            auth_service: Servicio de autenticación
        """
        self.parent = parent
        self.auth_service = auth_service
        
        # Frame principal
        self.frame = tk.Frame(parent, bg="#F5F7FA")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self._crear_interfaz()
        self._cargar_usuarios()
    
    def _crear_interfaz(self):
        """Crea la interfaz de gestión de usuarios"""
        # Header
        header = tk.Frame(self.frame, bg="#F5F7FA")
        header.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Label(
            header,
            text="👥 Gestión de Usuarios Auxiliares",
            font=('Segoe UI', 16, 'bold'),
            bg="#F5F7FA",
            fg="#263238"
        ).pack(side=tk.LEFT)
        
        # Botón nuevo usuario
        btn_nuevo = tk.Button(
            header,
            text="➕ Nuevo Auxiliar",
            font=('Segoe UI', 10, 'bold'),
            bg="#2196F3",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self._mostrar_formulario_nuevo
        )
        btn_nuevo.pack(side=tk.RIGHT)
        
        # Tabla de usuarios
        tabla_frame = tk.Frame(self.frame, bg="white", relief=tk.FLAT, bd=0)
        tabla_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=("Usuario", "Nombre", "Email", "Contacto", "Estado"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )
        scrollbar.config(command=self.tabla.yview)
        
        # Configurar columnas
        columnas = {
            "Usuario": 120,
            "Nombre": 200,
            "Email": 200,
            "Contacto": 150,
            "Estado": 100
        }
        
        for col, ancho in columnas.items():
            self.tabla.heading(col, text=col, anchor=tk.W)
            self.tabla.column(col, width=ancho, anchor=tk.W)
        
        self.tabla.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        acciones_frame = tk.Frame(self.frame, bg="#F5F7FA")
        acciones_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Button(
            acciones_frame,
            text="🔄 Actualizar",
            font=('Segoe UI', 10),
            bg="#4CAF50",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._cargar_usuarios
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            acciones_frame,
            text="🔒 Desactivar",
            font=('Segoe UI', 10),
            bg="#FF9800",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._desactivar_usuario
        ).pack(side=tk.LEFT)
    
    def _cargar_usuarios(self):
        """Carga la lista de usuarios auxiliares"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Obtener auxiliares
        auxiliares = self.auth_service.obtener_auxiliares()
        
        # Cargar en tabla
        for aux in auxiliares:
            estado = "🟢 Activo" if aux.activo else "🔴 Inactivo"
            self.tabla.insert("", tk.END, values=(
                aux.usuario,
                aux.nombre,
                aux.email,
                aux.contacto,
                estado
            ))
    
    def _mostrar_formulario_nuevo(self):
        """Muestra formulario para crear nuevo auxiliar"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Crear Nuevo Auxiliar")
        dialog.geometry("450x500")
        dialog.resizable(False, False)
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            main_frame,
            text="➕ Nuevo Auxiliar de Programación",
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=(0, 20))
        
        # Campos
        campos = {}
        
        def crear_campo(label, es_password=False):
            tk.Label(main_frame, text=label, font=('Segoe UI', 10)).pack(anchor='w', pady=(10, 5))
            entry = ttk.Entry(main_frame, font=('Segoe UI', 10), width=40, show='•' if es_password else None)
            entry.pack(fill='x')
            return entry
        
        campos['usuario'] = crear_campo("Usuario (único):")
        campos['nombre'] = crear_campo("Nombre completo:")
        campos['email'] = crear_campo("Email:")
        campos['contacto'] = crear_campo("Teléfono/Contacto:")
        campos['password'] = crear_campo("Contraseña (mín. 6 caracteres):", es_password=True)
        campos['confirmar'] = crear_campo("Confirmar contraseña:", es_password=True)
        
        # Botones
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=(30, 0))
        
        def crear_usuario():
            # Validar campos
            usuario = campos['usuario'].get().strip()
            nombre = campos['nombre'].get().strip()
            email = campos['email'].get().strip()
            contacto = campos['contacto'].get().strip()
            password = campos['password'].get()
            confirmar = campos['confirmar'].get()
            
            if not all([usuario, nombre, email, contacto, password]):
                messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos")
                return
            
            if len(password) < 6:
                messagebox.showwarning("Contraseña débil", "La contraseña debe tener al menos 6 caracteres")
                return
            
            if password != confirmar:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            # Crear usuario
            exito, mensaje = self.auth_service.crear_usuario(
                usuario=usuario,
                nombre=nombre,
                email=email,
                contacto=contacto,
                password=password,
                rol=RolUsuario.AUX_PROG
            )
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                dialog.destroy()
                self._cargar_usuarios()
            else:
                messagebox.showerror("Error", mensaje)
        
        tk.Button(
            btn_frame,
            text="✅ Crear Usuario",
            font=('Segoe UI', 11, 'bold'),
            bg="#4CAF50",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=crear_usuario
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=('Segoe UI', 11),
            bg="#757575",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=dialog.destroy
        ).pack(side=tk.LEFT)
    
    def _desactivar_usuario(self):
        """Desactiva el usuario seleccionado"""
        seleccion = self.tabla.selection()
        
        if not seleccion:
            messagebox.showwarning("Sin selección", "Por favor seleccione un usuario")
            return
        
        item = self.tabla.item(seleccion[0])
        usuario = item['values'][0]
        
        confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Desea desactivar al usuario '{usuario}'?\n\nNo podrá iniciar sesión."
        )
        
        if confirmar:
            exito, mensaje = self.auth_service.desactivar_usuario(usuario)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self._cargar_usuarios()
            else:
                messagebox.showerror("Error", mensaje)
