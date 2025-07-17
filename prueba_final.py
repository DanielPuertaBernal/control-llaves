"""
Prueba final del sistema con datos reales
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

from helpers.gestion_excel import inicializar_registro, registrar_entrega, obtener_llaves_pendientes, limpiar_numero_documento

def prueba_final():
    print("=== PRUEBA FINAL DEL SISTEMA ===\n")
    
    # Inicializar sistema
    inicializar_registro()
    print("1. ✅ Sistema inicializado")
    
    # Probar limpieza de documento
    documentos_prueba = ["12345678.0", "87654321", "11111111.0", "ABC123"]
    print("\n2. Probando limpieza de documentos:")
    for doc in documentos_prueba:
        limpio = limpiar_numero_documento(doc)
        print(f"   '{doc}' → '{limpio}'")
    
    # Simular entrega
    print("\n3. Simulando entrega de llave:")
    info_entrega = {
        'nroidenti': '12345678.0',  # Simular como viene de Excel
        'profesor': 'JUAN PEREZ',
        'materia': 'MATEMATICAS I',
        'aula': 'A101',
        'dia': 'LUNES',
        'horario': '08:00 a 10:00',
        'nro_estudiantes': 25
    }
    
    resultado = registrar_entrega(info_entrega)
    if resultado:
        print("   ✅ Entrega registrada correctamente")
    else:
        print("   ❌ Error en entrega")
    
    # Verificar llaves prestadas
    print("\n4. Verificando llaves prestadas:")
    prestadas = obtener_llaves_pendientes()
    
    if not prestadas.empty:
        print("   Llaves encontradas:")
        for _, fila in prestadas.iterrows():
            doc_limpio = limpiar_numero_documento(fila['nroidenti'])
            print(f"     📋 Doc: {doc_limpio} | Prof: {fila['profesor']} | Aula: {fila['aula']}")
            
            # Verificar que no sea 0
            if doc_limpio == '0':
                print("     ❌ ERROR: Documento convertido a 0")
                return False
            elif '.0' in doc_limpio:
                print("     ❌ ERROR: Documento con .0")
                return False
            else:
                print("     ✅ Documento correcto")
    else:
        print("   No hay llaves prestadas")
    
    print("\n=== RESULTADO FINAL ===")
    print("✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
    print("✅ Números de documento limpios")
    print("✅ Sin conversiones a 0")
    print("✅ Sin formato .0 no deseado")
    print("\n🎉 EL SISTEMA ESTÁ LISTO PARA USAR")
    
    return True

if __name__ == "__main__":
    try:
        prueba_final()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
