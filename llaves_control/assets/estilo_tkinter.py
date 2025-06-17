import tkinter as tk
from tkinter import ttk

def aplicar_estilo(root):
    style = ttk.Style(root)
    root.tk.call('source', 'azure.tcl')  # Requiere tema si quieres personalizar más
    style.theme_use('default')

    style.configure("TButton",
                    padding=6,
                    relief="flat",
                    background="#4CAF50",
                    foreground="white",
                    font=('Segoe UI', 10, 'bold'))
    
    style.map("TButton",
              background=[('active', '#45a049')],
              foreground=[('disabled', 'gray')])

    style.configure("Treeview.Heading",
                    font=('Segoe UI', 10, 'bold'),
                    background="#4CAF50",
                    foreground="white")
