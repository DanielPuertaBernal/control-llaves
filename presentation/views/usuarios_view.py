"""
Vista de Gestión de Usuarios - Solo Admin
"""
import tkinter as tk
from tkinter import ttk, messagebox
from domain.usuario import RolUsuario
from domain.value_objects import Email, Telefono, NombreUsuario, Password


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
        
        # Encabezado con filtros
        filtro_frame = tk.Frame(tabla_frame, bg="white", height=40)
        filtro_frame.pack(fill=tk.X, pady=(0, 10))
        filtro_frame.pack_propagate(False)
        
        tk.Label(
            filtro_frame,
            text="Mostrar:",
            font=('Segoe UI', 10),
            bg="white"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.filtro_var = tk.StringVar(value="todos")
        
        tk.Radiobutton(
            filtro_frame,
            text="Todos",
            variable=self.filtro_var,
            value="todos",
            font=('Segoe UI', 10),
            bg="white",
            command=self._cargar_usuarios
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            filtro_frame,
            text="🟢 Activos",
            variable=self.filtro_var,
            value="activos",
            font=('Segoe UI', 10),
            bg="white",
            command=self._cargar_usuarios
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            filtro_frame,
            text="🔴 Inactivos",
            variable=self.filtro_var,
            value="inactivos",
            font=('Segoe UI', 10),
            bg="white",
            command=self._cargar_usuarios
        ).pack(side=tk.LEFT, padx=5)
        
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
        
        # Lado izquierdo - botones de acción
        left_frame = tk.Frame(acciones_frame, bg="#F5F7FA")
        left_frame.pack(side=tk.LEFT)
        
        tk.Button(
            left_frame,
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
            left_frame,
            text="🔒 Desactivar",
            font=('Segoe UI', 10),
            bg="#FF9800",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._desactivar_usuario
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            left_frame,
            text="✅ Reactivar",
            font=('Segoe UI', 10),
            bg="#2196F3",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._reactivar_usuario
        ).pack(side=tk.LEFT)
        
        # Lado derecho - contador
        self.label_contador = tk.Label(
            acciones_frame,
            text="",
            font=('Segoe UI', 9),
            bg="#F5F7FA",
            fg="#666"
        )
        self.label_contador.pack(side=tk.RIGHT)
    
    def _cargar_usuarios(self):
        """Carga la lista de usuarios auxiliares según filtro"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Obtener auxiliares (todos incluidos inactivos)
        auxiliares = self.auth_service.obtener_auxiliares(incluir_inactivos=True)
        
        # Aplicar filtro
        filtro = self.filtro_var.get() if hasattr(self, 'filtro_var') else "todos"
        
        if filtro == "activos":
            auxiliares = [aux for aux in auxiliares if aux.activo]
        elif filtro == "inactivos":
            auxiliares = [aux for aux in auxiliares if not aux.activo]
        # Si es "todos", no filtramos
        
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
        
        # Actualizar contador
        total = len(auxiliares)
        activos = sum(1 for aux in auxiliares if aux.activo)
        inactivos = total - activos
        self.label_contador.config(text=f"Total: {total} | 🟢 Activos: {activos} | 🔴 Inactivos: {inactivos}")
    
    def _mostrar_formulario_nuevo(self):
        """Muestra formulario para crear nuevo auxiliar"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Crear Nuevo Auxiliar")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.configure(bg="#f0f4f8")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (580 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=18)
        
        # Título simple sin banner
        tk.Label(
            main_frame,
            text="➕ Nuevo Auxiliar de Programación",
            font=('Segoe UI', 16, 'bold'),
            bg="#f0f4f8",
            fg="#1976D2"
        ).pack(pady=(0, 16))
        
        # Frame para campos con fondo blanco
        campos_frame = tk.Frame(main_frame, bg="white", relief=tk.SOLID, bd=1)
        campos_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Padding interno
        inner_frame = tk.Frame(campos_frame, bg="white")
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=12)

        # Dos columnas
        columns_frame = tk.Frame(inner_frame, bg="white")
        columns_frame.pack(fill=tk.BOTH, expand=True)

        left_col = tk.Frame(columns_frame, bg="white")
        right_col = tk.Frame(columns_frame, bg="white")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Campos con validación
        campos = {}
        entry_widgets = {}
        entry_errors = {}
        entry_tipos = {}
        field_index = 0
        
        def validar_campo_completo(entry, tipo='texto'):
            """
            Valida campo usando Value Objects del dominio
            Solo validaciones de UX aquí (vacío, visual feedback)
            """
            valor = entry.get().strip()
            
            error_label = entry_errors.get(entry)

            if not valor:
                entry.config(bg="#ffebee", relief=tk.SOLID, bd=2, highlightbackground="#ef5350")
                if error_label:
                    error_label.config(text="Campo obligatorio")
                return False
            
            try:
                # Validar usando Value Objects del dominio
                if tipo == 'email':
                    Email(valor)  # Lanza ValueError si inválido
                elif tipo == 'telefono':
                    Telefono(valor)
                elif tipo == 'usuario':
                    NombreUsuario(valor)
                
                # Si pasa, marcar como válido
                entry.config(bg="#e8f5e9", relief=tk.SOLID, bd=2, highlightbackground="#66BB6A")
                if error_label:
                    error_label.config(text="")
                return True
                
            except ValueError as e:
                # El dominio rechazó el valor
                entry.config(bg="#ffebee", relief=tk.SOLID, bd=2, highlightbackground="#ef5350")
                if error_label:
                    error_label.config(text=str(e))
                return False
        
        def crear_campo(label, es_password=False, tipo='texto'):
            nonlocal field_index
            parent = left_col if field_index % 2 == 0 else right_col
            field_index += 1
            # Label
            lbl = tk.Label(
                parent,
                text=label,
                font=('Segoe UI', 10, 'bold'),
                bg="white",
                fg="#2c3e50",
                anchor='w'
            )
            lbl.pack(fill='x', pady=(10, 5))
            
            # Entry con validación
            entry = tk.Entry(
                parent,
                font=('Segoe UI', 11),
                show='●' if es_password else '',
                relief=tk.SOLID,
                bg="white",
                fg="#263238",
                insertbackground="#1976D2",
                bd=2,
                highlightbackground="#90CAF9",
                highlightthickness=1
            )
            entry.pack(fill='x', ipady=8)
            
            # Validación en tiempo real para teléfono (solo UX)
            if tipo == 'telefono':
                def validar_tecla_telefono(event):
                    # Permitir teclas de edición y navegación
                    if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Home", "End", "Tab"):
                        return None
                    # Permitir combinaciones con Ctrl (copiar/pegar)
                    if event.state & 0x4:
                        return None
                    char = event.char
                    if char and not (char.isdigit() or char in ['+', '-', ' ', '(', ')']):
                        return 'break'  # Bloquea caracteres no permitidos
                
                entry.bind('<Key>', validar_tecla_telefono)
            
            # Evento para validar al perder el foco
            entry.bind('<FocusOut>', lambda e: validar_campo_completo(entry, tipo))
            
            # Label de error por campo
            error_lbl = tk.Label(
                parent,
                text="",
                font=('Segoe UI', 9),
                bg="white",
                fg="#d32f2f",
                anchor='w'
            )
            error_lbl.pack(fill='x', pady=(2, 2))

            entry_widgets[label] = entry
            entry_errors[entry] = error_lbl
            entry_tipos[entry] = tipo
            return entry
        
        campos['usuario'] = crear_campo("Usuario (único):", tipo='usuario')
        campos['nombre'] = crear_campo("Nombre completo:")
        campos['email'] = crear_campo("Email:", tipo='email')
        campos['contacto'] = crear_campo("Teléfono/Contacto:", tipo='telefono')
        campos['password'] = crear_campo("Contraseña (mín. 6 caracteres):", es_password=True)
        campos['confirmar'] = crear_campo("Confirmar contraseña:", es_password=True)
        
        # Frame para botones
        btn_frame = tk.Frame(main_frame, bg="#f0f4f8")
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Centrar botones
        btn_container = tk.Frame(btn_frame, bg="#f0f4f8")
        btn_container.pack(expand=True)
        
        def validar_todos_campos():
            """Valida todos los campos antes de crear"""
            todos_validos = True
            
            for entry in entry_widgets.values():
                tipo = entry_tipos.get(entry, 'texto')
                if not validar_campo_completo(entry, tipo):
                    todos_validos = False
            
            return todos_validos
        
        def crear_usuario():
            """Crea el usuario delegando validaciones al dominio"""
            # Validar visualmente todos los campos (solo UX)
            if not validar_todos_campos():
                messagebox.showwarning("Campos incompletos", "Complete todos los campos marcados en rojo")
                return
            
            # Obtener valores
            usuario = campos['usuario'].get().strip()
            nombre = campos['nombre'].get().strip()
            email = campos['email'].get().strip()
            contacto = campos['contacto'].get().strip()
            password = campos['password'].get()
            confirmar = campos['confirmar'].get()
            
            try:
                # Validar con Value Objects del dominio
                NombreUsuario(usuario)
                Email(email)
                Telefono(contacto)
                
                # Validar contraseñas con Password value object
                valida, mensaje_pass = Password.validar(password)
                if not valida:
                    campos['password'].config(bg="#ffebee", relief=tk.SOLID, bd=2, highlightbackground="#ef5350")
                    entry_errors.get(campos['password']).config(text=mensaje_pass)
                    messagebox.showwarning("Contraseña inválida", mensaje_pass)
                    campos['password'].focus()
                    return
                
                coinciden, mensaje_conf = Password.validar_confirmacion(password, confirmar)
                if not coinciden:
                    campos['password'].config(bg="#ffebee", relief=tk.SOLID, bd=2, highlightbackground="#ef5350")
                    campos['confirmar'].config(bg="#ffebee", relief=tk.SOLID, bd=2, highlightbackground="#ef5350")
                    entry_errors.get(campos['confirmar']).config(text=mensaje_conf)
                    messagebox.showerror("Error", mensaje_conf)
                    campos['confirmar'].focus()
                    return
                
            except ValueError as e:
                # El dominio rechazó los datos
                messagebox.showerror("Validación de dominio", str(e))
                return
            
            # Crear usuario
            # Crear usuario - el servicio maneja la persistencia
            try:
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
                    
            except ValueError as e:
                # Errores de validación de dominio
                messagebox.showerror("Error de validación", str(e))
        
        # Botón Crear con efecto hover
        btn_crear = tk.Button(
            btn_container,
            text="✓ CREAR USUARIO",
            font=('Segoe UI', 11, 'bold'),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=35,
            pady=14,
            command=crear_usuario
        )
        btn_crear.pack(side=tk.LEFT, padx=8)
        
        # Efectos hover para botón crear
        def on_enter_crear(e):
            btn_crear.config(bg="#45a049")
        
        def on_leave_crear(e):
            btn_crear.config(bg="#4CAF50")
        
        btn_crear.bind("<Enter>", on_enter_crear)
        btn_crear.bind("<Leave>", on_leave_crear)
        
        # Botón Cancelar con efecto hover
        btn_cancelar = tk.Button(
            btn_container,
            text="✕ CANCELAR",
            font=('Segoe UI', 11, 'bold'),
            bg="#607D8B",
            fg="white",
            activebackground="#546E7A",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=35,
            pady=14,
            command=dialog.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=8)
        
        # Efectos hover para botón cancelar
        def on_enter_cancelar(e):
            btn_cancelar.config(bg="#546E7A")
        
        def on_leave_cancelar(e):
            btn_cancelar.config(bg="#607D8B")
        
        btn_cancelar.bind("<Enter>", on_enter_cancelar)
        btn_cancelar.bind("<Leave>", on_leave_cancelar)
        
        # Focus en primer campo
        campos['usuario'].focus()
    
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
    
    def _reactivar_usuario(self):
        """Reactiva el usuario seleccionado"""
        seleccion = self.tabla.selection()
        
        if not seleccion:
            messagebox.showwarning("Sin selección", "Por favor seleccione un usuario")
            return
        
        item = self.tabla.item(seleccion[0])
        usuario = item['values'][0]
        estado = item['values'][4]
        
        if "Activo" in estado and "Inactivo" not in estado:
            messagebox.showinfo("Usuario activo", f"El usuario '{usuario}' ya está activo")
            return
        
        confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Desea reactivar al usuario '{usuario}'?\n\nPodrá iniciar sesión nuevamente."
        )
        
        if confirmar:
            exito, mensaje = self.auth_service.reactivar_usuario(usuario)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self._cargar_usuarios()
            else:
                messagebox.showerror("Error", mensaje)
