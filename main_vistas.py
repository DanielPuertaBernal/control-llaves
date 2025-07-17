"""
Sistema de Control de Llaves con Vistas Organizadas
Versión 2.0 - Enero 2025

Esta versión incluye:
- Vista de Entrega y Devolución
- Vista de Programación
- Vista de Informes
- Persistencia completa de datos
- Sistema mejorado de reportes
"""

import tkinter as tk
from ui.interfaz import App

def main():
    # Crear ventana principal
    root = tk.Tk()
    
    # Configurar ícono y propiedades de la ventana
    try:
        # Intentar establecer un ícono si existe
        root.iconbitmap("assets/icono.ico")
    except:
        pass  # Si no hay ícono, continuar sin él
    
    # Configuraciones adicionales
    root.resizable(True, True)  # Permitir redimensionar
    root.minsize(1000, 600)    # Tamaño mínimo
    
    # Crear la aplicación
    app = App(root)
    
    # Mensaje de bienvenida en consola
    print("=" * 60)
    print("🔑 SISTEMA DE CONTROL DE LLAVES v2.0")
    print("=" * 60)
    print("✅ Interfaz con vistas organizadas")
    print("✅ Sistema de persistencia robusto")
    print("✅ Reportes e informes avanzados")
    print("✅ Gestión completa de programación")
    print("-" * 60)
    print("📋 INSTRUCCIONES RÁPIDAS:")
    print("1. Use la pestaña 'Entrega y Devolución' para gestión diaria")
    print("2. Use la pestaña 'Programación' para cargar horarios")
    print("3. Use la pestaña 'Informes' para reportes y análisis")
    print("=" * 60)
    
    # Ejecutar la aplicación
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Sistema cerrado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔒 Sistema de Control de Llaves finalizado")

if __name__ == "__main__":
    main()
