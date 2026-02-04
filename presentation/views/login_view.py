"""
Vista de Login - Autenticación de usuarios
"""
import tkinter as tk
from tkinter import ttk, messagebox
from application.service_factory import ServiceFactory


class LoginView:
    """Vista para autenticación de usuarios"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔑 Control de Llaves - Login")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        # Centrar en pantalla
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 450) // 2
        y = (self.root.winfo_screenheight() - 350) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # Service
        self.auth_service = ServiceFactory().get_auth_service()
        
        # Resultado
        self.usuario_autenticado = None
        self.login_exitoso = False
        
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea los componentes de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Título
        titulo = ttk.Label(
            main_frame,
            text="🔑 Control de Llaves",
            font=('Segoe UI', 18, 'bold')
        )
        titulo.pack(pady=(0, 5))
        
        subtitulo = ttk.Label(
            main_frame,
            text="Gestión de acceso académico",
            font=('Segoe UI', 10),
            foreground="#666"
        )
        subtitulo.pack(pady=(0, 30))
        
        # Separador
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 20))
        
        # Frame de formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Usuario
        ttk.Label(form_frame, text="Usuario:", font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        self.entry_usuario = ttk.Entry(form_frame, font=('Segoe UI', 10), width=35)
        self.entry_usuario.pack(fill='x', pady=(0, 15))
        self.entry_usuario.bind('<Return>', lambda e: self._hacer_login())
        
        # Contraseña
        ttk.Label(form_frame, text="Contraseña:", font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        self.entry_password = ttk.Entry(form_frame, font=('Segoe UI', 10), width=35, show='•')
        self.entry_password.pack(fill='x', pady=(0, 20))
        self.entry_password.bind('<Return>', lambda e: self._hacer_login())
        
        # Botón Login
        btn_login = ttk.Button(form_frame, text="Ingresar", command=self._hacer_login)
        btn_login.pack(fill='x', pady=(10, 0))
    
    def _hacer_login(self):
        """Procesa el login"""
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()
        
        if not usuario or not password:
            messagebox.showwarning("Campos vacíos", "Ingrese usuario y contraseña")
            return
        
        exito, mensaje, usuario_obj = self.auth_service.login(usuario, password)
        
        if exito:
            self.usuario_autenticado = usuario_obj
            self.login_exitoso = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", mensaje)
            self.entry_password.delete(0, tk.END)
            self.entry_usuario.focus()
    
    def obtener_resultado(self):
        return self.login_exitoso, self.usuario_autenticado


def mostrar_login() -> tuple:
    """
    Muestra la ventana de login y retorna el resultado
    
    Returns:
        tuple: (login_exitoso, usuario_autenticado)
    """
    root = tk.Tk()
    login_view = LoginView(root)
    root.mainloop()
    return login_view.obtener_resultado()
