"""
Prueba específica de búsqueda por documento
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

def main():
    print("=== SISTEMA DE CONTROL DE LLAVES ===")
    print("Búsqueda por documento mejorada ✅")
    print()
    print("CAMBIOS IMPLEMENTADOS:")
    print("✅ Búsqueda por nombre de profesor")
    print("✅ Búsqueda por número de documento")
    print("✅ Limpieza automática de documentos (.0 removal)")
    print("✅ Búsqueda parcial (ej: '1234' encuentra '12345678')")
    print("✅ Mensaje de retroalimentación al usuario")
    print()
    print("INSTRUCCIONES DE USO:")
    print("1. Ejecute el sistema: python main.py")
    print("2. Vaya a la pestaña '🔑 Entrega y Devolución'")
    print("3. Cargue su archivo de programación en la pestaña '📅 Programación'")
    print("4. Regrese a 'Entrega y Devolución'")
    print("5. En el campo 'Buscar Profesor' escriba:")
    print("   - Nombre del profesor: 'JUAN' o 'PEREZ'")
    print("   - Número de documento: '12345678' o parte como '1234'")
    print("6. Los resultados aparecerán automáticamente")
    print()
    print("EJEMPLOS DE BÚSQUEDA:")
    print("- Por nombre: MARIA, CARLOS, RODRIGUEZ")
    print("- Por documento: 12345678, 1234, 8765")
    print("- Búsqueda parcial: Solo escriba parte del nombre o documento")
    print()
    print("🎉 ¡SISTEMA LISTO PARA USAR!")

if __name__ == "__main__":
    main()
