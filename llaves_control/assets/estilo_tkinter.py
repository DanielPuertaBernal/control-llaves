import tkinter as tk
from tkinter import ttk

def aplicar_estilo(root):
    """Aplica estilos personalizados a la aplicación"""
    style = ttk.Style(root)
    
    # Usar tema por defecto como base
    style.theme_use('default')

    # Configuración de colores
    color_primario = "#2E7D32"      # Verde oscuro
    color_secundario = "#4CAF50"    # Verde claro
    color_acento = "#81C784"        # Verde muy claro
    color_fondo = "#F5F5F5"         # Gris claro
    color_texto = "#212121"         # Gris oscuro
    color_blanco = "#FFFFFF"
    
    # Configurar el fondo de la ventana principal
    root.configure(bg=color_fondo)

    # Estilos para botones
    style.configure("TButton",
                    padding=(10, 8),
                    relief="flat",
                    background=color_secundario,
                    foreground=color_blanco,
                    font=('Segoe UI', 10, 'bold'),
                    borderwidth=0)
    
    style.map("TButton",
              background=[('active', color_primario),
                         ('pressed', color_primario)],
              foreground=[('disabled', 'gray')])

    # Estilos para LabelFrame
    style.configure("TLabelframe",
                    background=color_fondo,
                    borderwidth=2,
                    relief="solid")
    
    style.configure("TLabelframe.Label",
                    background=color_fondo,
                    foreground=color_primario,
                    font=('Segoe UI', 11, 'bold'))

    # Estilos para Labels
    style.configure("TLabel",
                    background=color_fondo,
                    foreground=color_texto,
                    font=('Segoe UI', 10))

    # Estilos para Entry
    style.configure("TEntry",
                    padding=5,
                    relief="solid",
                    borderwidth=1,
                    font=('Segoe UI', 10))

    # Estilos para Frame
    style.configure("TFrame",
                    background=color_fondo)

    # Estilos para Treeview (tabla)
    style.configure("Treeview.Heading",
                    font=('Segoe UI', 10, 'bold'),
                    background=color_primario,
                    foreground=color_blanco,
                    relief="raised",
                    borderwidth=2)
    
    style.map("Treeview.Heading",
              background=[('active', color_secundario)])

    style.configure("Treeview",
                    background=color_blanco,
                    foreground=color_texto,
                    fieldbackground=color_blanco,
                    font=('Segoe UI', 9),
                    rowheight=28,
                    borderwidth=2,
                    relief="solid")
    
    style.map("Treeview",
              background=[('selected', color_acento)],
              foreground=[('selected', color_texto)])

    # Configurar estilos específicos para filas alternadas
    style.configure("Treeview.Item",
                    borderwidth=1,
                    relief="solid")

    # Estilos para Scrollbar
    style.configure("Vertical.TScrollbar",
                    background=color_fondo,
                    troughcolor=color_fondo,
                    borderwidth=0,
                    arrowcolor=color_primario,
                    darkcolor=color_secundario,
                    lightcolor=color_secundario)

    # Estilos para Combobox
    style.configure("TCombobox",
                    padding=5,
                    relief="solid",
                    borderwidth=1,
                    font=('Segoe UI', 10),
                    fieldbackground=color_blanco,
                    selectbackground=color_acento)
    
    style.map("TCombobox",
              focuscolor=[('!focus', color_secundario)],
              bordercolor=[('focus', color_primario)])

def configurar_ventana_principal(root):
    """Configuración adicional para la ventana principal"""
    # Centrar la ventana en la pantalla
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Configurar el icono de la ventana (opcional)
    try:
        root.iconbitmap('assets/icon.ico')
    except:
        pass  # Si no existe el icono, continuar sin él
