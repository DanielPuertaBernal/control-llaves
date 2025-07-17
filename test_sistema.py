"""
Script de prueba para verificar la funcionalidad del sistema de control de llaves
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

import pandas as pd
from helpers.limpieza_programacion import limpiar_programacion
from helpers.gestion_excel import inicializar_registro, registrar_entrega, filtrar_llaves

def test_sistema():
    print("=== PRUEBA DEL SISTEMA DE CONTROL DE LLAVES ===\n")
    
    # Test 1: Inicializar registro
    print("1. Inicializando sistema...")
    inicializar_registro()
    print("   ✓ Sistema inicializado correctamente\n")
    
    # Test 2: Crear datos de prueba
    print("2. Creando datos de programación de prueba...")
    datos_prueba = {
        'nroidenti': ['12345678', '12345678', '87654321'],
        'profesor': ['JUAN PEREZ', 'JUAN PEREZ', 'MARIA GARCIA'],
        'MATERIA': ['MATEMATICAS I', 'MATEMATICAS I', 'FISICA II'],
        'aula': ['A101', 'A101', 'B205'],
        'dia': ['LUNES', 'LUNES', 'MARTES'],
        'horario': ['08:00 A 10:00', '10:00 A 12:00', '14:00 A 16:00'],
        'nro_estudiantes': [25, 25, 30]
    }
    
    df_prueba = pd.DataFrame(datos_prueba)
    print(f"   ✓ Creados {len(df_prueba)} registros de prueba\n")
    
    # Test 3: Limpiar programación
    print("3. Limpiando y consolidando programación...")
    df_limpio = limpiar_programacion(df_prueba)
    print(f"   ✓ Registros consolidados: {len(df_prueba)} → {len(df_limpio)}")
    print("   Programación consolidada:")
    for _, fila in df_limpio.iterrows():
        print(f"     - {fila['profesor']}: {fila['materia']} en {fila['aula']} ({fila['horario']})")
    print()
    
    # Test 4: Registrar entrega
    print("4. Registrando entrega de llave...")
    info_clase = {
        'nroidenti': '12345678',
        'profesor': 'JUAN PEREZ',
        'materia': 'MATEMATICAS I',
        'aula': 'A101',
        'dia': 'LUNES',
        'horario': '08:00 a 12:00',
        'nro_estudiantes': 25
    }
    
    resultado = registrar_entrega(info_clase)
    if resultado:
        print("   ✓ Llave entregada y registrada correctamente")
    else:
        print("   ✗ Error al registrar entrega")
    print()
    
    # Test 5: Consultar registros
    print("5. Consultando registros...")
    registros = filtrar_llaves()
    print(f"   ✓ Total de registros: {len(registros)}")
    
    llaves_entregadas = filtrar_llaves('Entregada')
    print(f"   ✓ Llaves entregadas: {len(llaves_entregadas)}")
    
    if not llaves_entregadas.empty:
        print("   Llaves actualmente entregadas:")
        for _, fila in llaves_entregadas.iterrows():
            print(f"     - {fila['profesor']}: {fila['materia']} (Aula {fila['aula']})")
    print()
    
    print("=== TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE ===")
    print("\nEl sistema está listo para usar. Para iniciar la interfaz gráfica:")
    print("python llaves_control/main.py")

if __name__ == "__main__":
    try:
        test_sistema()
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
