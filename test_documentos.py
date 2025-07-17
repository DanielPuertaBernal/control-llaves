"""
Script de prueba específico para verificar números de documento
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

import pandas as pd
from helpers.limpieza_programacion import limpiar_programacion
from helpers.gestion_excel import limpiar_numero_documento

def test_documentos():
    print("=== PRUEBA ESPECÍFICA DE NÚMEROS DE DOCUMENTO ===\n")
    
    # Test de la función de limpieza
    print("1. Probando función limpiar_numero_documento:")
    casos_prueba = [
        "12345678.0",
        "12345678", 
        "87654321.0",
        "ABC123",
        "999999999.0",
        "123.456.789",
        ""
    ]
    
    for caso in casos_prueba:
        resultado = limpiar_numero_documento(caso)
        print(f"   '{caso}' → '{resultado}'")
    
    print("\n2. Probando con datos simulados de Excel:")
    # Simular datos como vienen de Excel (números se vuelven float)
    datos_excel = {
        'nroidenti': [12345678.0, 87654321.0, 11111111.0, 22222222.0],
        'profesor': ['JUAN PEREZ', 'MARIA GARCIA', 'CARLOS LOPEZ', 'ANA MARTINEZ'],
        'MATERIA': ['MATEMATICAS I', 'FISICA II', 'QUIMICA', 'BIOLOGIA'],
        'aula': ['A101', 'B205', 'C301', 'C302'],
        'dia': ['LUNES', 'MARTES', 'JUEVES', 'VIERNES'],
        'horario': ['08:00 A 10:00', '14:00 A 16:00', '16:00 A 18:00', '10:00 A 12:00']
    }
    
    df_excel = pd.DataFrame(datos_excel)
    print("   Datos originales (como vienen de Excel):")
    for _, fila in df_excel.iterrows():
        print(f"     {fila['nroidenti']} ({type(fila['nroidenti'])}) - {fila['profesor']}")
    
    print("\n3. Después de la limpieza:")
    df_limpio = limpiar_programacion(df_excel)
    for _, fila in df_limpio.iterrows():
        print(f"     {fila['nroidenti']} ({type(fila['nroidenti'])}) - {fila['profesor']}")
    
    print("\n4. Verificación de problemas:")
    problemas = []
    
    for _, fila in df_limpio.iterrows():
        doc = str(fila['nroidenti'])
        if doc == '0':
            problemas.append(f"Documento convertido a 0: {fila['profesor']}")
        elif '.0' in doc:
            problemas.append(f"Documento con .0: {doc} - {fila['profesor']}")
    
    if problemas:
        print("   ❌ PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"     - {problema}")
    else:
        print("   ✅ No se encontraron problemas con los números de documento")
    
    print("\n=== RESULTADO DE LA PRUEBA ===")
    if not problemas:
        print("✅ ÉXITO: Todos los números de documento se manejan correctamente")
        print("✅ No hay conversiones a 0")
        print("✅ No hay formato .0 no deseado")
    else:
        print("❌ FALLÓ: Se encontraron problemas con los números de documento")
    
    return len(problemas) == 0

if __name__ == "__main__":
    try:
        exito = test_documentos()
        if exito:
            print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        else:
            print("\n⚠️ PRUEBA FALLÓ - Revisar problemas arriba")
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
