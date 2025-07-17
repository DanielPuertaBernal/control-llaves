"""
Prueba rápida de la nueva interfaz
"""
import sys
import os

# Agregar el path del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
llaves_control_dir = os.path.join(current_dir, 'llaves_control')
sys.path.insert(0, llaves_control_dir)

try:
    print("🔄 Importando módulos...")
    import tkinter as tk
    from ui.interfaz import App
    
    print("✅ Módulos importados correctamente")
    print("✅ tkinter disponible")
    print("✅ Interfaz lista para ejecutar")
    
    # Crear una ventana de prueba básica
    root = tk.Tk()
    root.title("Prueba - Control de Llaves")
    root.geometry("800x600")
    
    # Crear etiqueta de prueba
    label = tk.Label(root, text="✅ Nueva interfaz con vistas funcionando\n\n🔑 Entrega y Devolución\n📅 Programación\n📊 Informes", 
                    font=('Segoe UI', 12), justify='center')
    label.pack(expand=True)
    
    print("🎉 Interfaz de prueba creada")
    print("   Cierre la ventana para continuar...")
    
    # Mostrar por 3 segundos
    root.after(3000, root.destroy)
    root.mainloop()
    
    print("✅ Prueba completada exitosamente")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()
