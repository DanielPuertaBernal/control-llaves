import tkinter as tk
from tkinter import ttk

def AplicarEstilo(root):
    """Aplica estilos personalizados a la aplicación con tema verde moderno"""
    style = ttk.Style(root)
    
    # Usar tema por defecto como base
    style.theme_use('default')

    # Configuración de colores - Paleta profesional azul y gris
    color_primario = "#1976D2"      # Azul corporativo vibrante
    color_secundario = "#42A5F5"    # Azul claro brillante
    color_acento = "#64B5F6"        # Azul celeste suave
    color_fondo = "#F5F7FA"         # Gris azulado muy claro
    color_sidebar = "#37474F"       # Gris azulado oscuro elegante
    color_texto = "#263238"         # Gris carbón oscuro
    color_texto_claro = "#546E7A"   # Gris medio
    color_blanco = "#FFFFFF"
    color_hover = "#2196F3"         # Azul brillante para hover
    color_card = "#FFFFFF"          # Blanco puro para tarjetas
    color_sombra = "#CFD8DC"        # Gris azulado claro para sombras
    color_salir = "#EF5350"         # Rojo coral para botón salir
    
    # Configurar el fondo de la ventana principal
    root.configure(bg=color_fondo)

    # Estilos para botones principales
    style.configure("TButton",
                    padding=(12, 10),
                    relief="flat",
                    background=color_secundario,
                    foreground=color_blanco,
                    font=('Segoe UI', 10, 'bold'),
                    borderwidth=0)
    
    style.map("TButton",
              background=[('active', color_hover),
                         ('pressed', color_primario)],
              foreground=[('disabled', '#9E9E9E')])
    
    # Estilo para botones del menú lateral
    style.configure("Sidebar.TButton",
                    padding=(15, 12),
                    relief="flat",
                    background=color_sidebar,
                    foreground=color_blanco,
                    font=('Segoe UI', 11),
                    borderwidth=0,
                    anchor="w")
    
    style.map("Sidebar.TButton",
              background=[('active', color_hover),
                         ('pressed', color_primario)])
    
    # Estilo para botón seleccionado
    style.configure("SidebarActive.TButton",
                    padding=(15, 12),
                    relief="flat",
                    background=color_primario,
                    foreground=color_blanco,
                    font=('Segoe UI', 11, 'bold'),
                    borderwidth=0,
                    anchor="w")
    
    # Estilo para botón de salir
    style.configure("Exit.TButton",
                    padding=(12, 10),
                    relief="flat",
                    background=color_salir,
                    foreground=color_blanco,
                    font=('Segoe UI', 10, 'bold'),
                    borderwidth=0)
    
    style.map("Exit.TButton",
              background=[('active', '#E53935'),
                         ('pressed', '#C62828')])

    # Estilos para LabelFrame (tarjetas)
    style.configure("TLabelframe",
                    background=color_card,
                    borderwidth=0,
                    relief="flat")
    
    style.configure("TLabelframe.Label",
                    background=color_card,
                    foreground="#424242",
                    font=('Segoe UI', 12, 'bold'))
    
    # Estilo para tarjetas con bordes redondeados (efecto visual)
    style.configure("Card.TFrame",
                    background=color_card,
                    relief="flat",
                    borderwidth=2)
    
    # Estilo para el sidebar
    style.configure("Sidebar.TFrame",
                    background=color_sidebar)
    
    # Estilo para el área principal
    style.configure("Content.TFrame",
                    background=color_fondo)

    # Estilos para Labels
    style.configure("TLabel",
                    background=color_fondo,
                    foreground="#212121",
                    font=('Segoe UI', 10))
    
    # Labels para títulos principales
    style.configure("Title.TLabel",
                    background=color_fondo,
                    foreground="#212121",
                    font=('Segoe UI', 20, 'bold'))
    
    # Labels para sidebar
    style.configure("Sidebar.TLabel",
                    background=color_sidebar,
                    foreground=color_blanco,
                    font=('Segoe UI', 10))
    
    # Labels para tarjetas
    style.configure("Card.TLabel",
                    background=color_card,
                    foreground="#424242",
                    font=('Segoe UI', 10))

    # Estilos para Entry (campos de búsqueda)
    style.configure("TEntry",
                    padding=10,
                    relief="flat",
                    borderwidth=1,
                    fieldbackground=color_blanco,
                    font=('Segoe UI', 10))
    
    style.map("TEntry",
              fieldbackground=[('focus', color_blanco)],
              bordercolor=[('focus', color_secundario)])
    
    # Estilo especial para búsqueda
    style.configure("Search.TEntry",
                    padding=10,
                    relief="flat",
                    borderwidth=0,
                    fieldbackground=color_blanco,
                    font=('Segoe UI', 10))

    # Estilos para Frame
    style.configure("TFrame",
                    background=color_fondo)

    # Estilos para Treeview (tabla) modernizado con colores profesionales
    style.configure("Treeview.Heading",
                    font=('Segoe UI', 10, 'bold'),
                    background="#424242",
                    foreground=color_blanco,
                    relief="flat",
                    borderwidth=0)
    
    style.map("Treeview.Heading",
              background=[('active', '#616161')])

    style.configure("Treeview",
                    background=color_blanco,
                    foreground="#212121",
                    fieldbackground=color_blanco,
                    font=('Segoe UI', 9),
                    rowheight=32,
                    borderwidth=0,
                    relief="flat")
    
    style.map("Treeview",
              background=[('selected', '#E0E0E0')],
              foreground=[('selected', '#212121')])

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

def ConfigurarVentanaPrincipal(root):
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
