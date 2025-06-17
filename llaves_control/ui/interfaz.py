import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from helpers.limpieza_programacion import limpiar_programacion
from helpers.gestion_excel import registrar_entrega, registrar_devolucion, filtrar_llaves, inicializar_registro
from assets.estilo_tkinter import aplicar_estilo
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Llaves")
        self.programacion = None
        inicializar_registro()

        # Botón para cargar programación
        ttk.Button(root, text="Cargar Programación", command=self.cargar_programacion).pack(pady=5)

        # Campo para buscar por documento
        self.doc_entry = ttk.Entry(root)
        self.doc_entry.pack()
        ttk.Button(root, text="Buscar Clases", command=self.buscar_clases).pack(pady=5)

        # Tabla
        self.tree = ttk.Treeview(root, columns=("materia", "aula", "horario", "estado"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack()

    def cargar_programacion(self):
        file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xls *.xlsx")])
        if file:
            df = pd.read_excel(file)
            self.programacion = limpiar_programacion(df)
            messagebox.showinfo("Éxito", "Programación cargada y limpiada")

    def buscar_clases(self):
        doc = self.doc_entry.get().strip()
        if not self.programacion is None:
            hoy = pd.Timestamp.today().day_name().lower()
            clases = self.programacion[(self.programacion['nroidenti'] == doc) & (self.programacion['dia'] == hoy)]
            self.tree.delete(*self.tree.get_children())
            for _, fila in clases.iterrows():
                self.tree.insert('', 'end', values=(
                    fila['materia'], fila['aula'], fila['horario'], 'Sin entregar'
                ))
        else:
            messagebox.showerror("Error", "Carga primero una programación.")
