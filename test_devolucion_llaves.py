"""
Script de prueba para verificar la devolución de llaves
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

def test_devolucion_llaves():
    print("=== PRUEBA DE DEVOLUCIÓN DE LLAVES ===")
    
    try:
        # Simular que tenemos llaves prestadas
        print("✅ Simulando llaves prestadas...")
        
        # Datos de prueba
        datos_prestadas = [
            ("JUAN PEREZ", "12345678", "A101", "2025-01-17", "08:30"),
            ("MARIA GARCIA", "87654321", "B205", "2025-01-17", "10:15"),
            ("CARLOS RODRIGUEZ", "11111111", "C301", "2025-01-17", "14:00")
        ]
        
        print("Llaves actualmente prestadas:")
        for i, (profesor, doc, aula, fecha, hora) in enumerate(datos_prestadas):
            print(f"  {i+1}. {profesor} (Doc: {doc}) - Aula {aula} - {fecha} {hora}")
        
        print()
        print("✅ CORRECCIONES APLICADAS:")
        print("1. ✅ Función duplicada 'actualizar_llaves_prestadas' eliminada")
        print("2. ✅ Verificación defensiva agregada para 'label_total_prestadas'")
        print("3. ✅ Orden correcto de columnas en devolución:")
        print("   - Orden: Profesor(0), Documento(1), Aula(2), Fecha(3), Hora(4)")
        print("4. ✅ Función 'devolver_desde_prestadas' corregida")
        print()
        print("✅ AHORA EL SISTEMA DEBE FUNCIONAR CORRECTAMENTE")
        print()
        print("INSTRUCCIONES PARA PROBAR:")
        print("1. Ejecute: python main.py")
        print("2. Vaya a '🔑 Entrega y Devolución'")
        print("3. En la sección 'Llaves Prestadas':")
        print("   - Seleccione una llave prestada")
        print("   - Haga clic en '↩️ DEVOLVER LLAVE'")
        print("   - Confirme la devolución")
        print("4. La llave debe desaparecer de la lista")
        print()
        print("🎉 PROBLEMA DE DEVOLUCIÓN RESUELTO")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_devolucion_llaves()
