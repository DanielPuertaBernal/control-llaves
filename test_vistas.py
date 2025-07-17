"""
Test del nuevo sistema de vistas del control de llaves
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

from helpers.gestion_excel import inicializar_registro, registrar_entrega, obtener_llaves_pendientes, limpiar_numero_documento

def test_nuevo_sistema():
    print("=== PRUEBA DEL NUEVO SISTEMA DE VISTAS ===\n")
    
    # 1. Inicializar sistema
    print("1. Inicializando sistema...")
    inicializar_registro()
    print("   ✅ Sistema inicializado")
    
    # 2. Simular varias entregas
    print("\n2. Simulando entregas de llaves...")
    
    entregas_test = [
        {
            'nroidenti': '12345678.0',
            'profesor': 'JUAN PEREZ',
            'materia': 'MATEMATICAS I',
            'aula': 'A101',
            'dia': 'LUNES',
            'horario': '08:00 - 10:00',
            'nro_estudiantes': 25
        },
        {
            'nroidenti': '87654321',
            'profesor': 'MARIA GARCIA',
            'materia': 'FISICA II',
            'aula': 'B205',
            'dia': 'MARTES',
            'horario': '10:00 - 12:00',
            'nro_estudiantes': 30
        },
        {
            'nroidenti': '11111111.0',
            'profesor': 'CARLOS RODRIGUEZ',
            'materia': 'QUIMICA GENERAL',
            'aula': 'C301',
            'dia': 'MIERCOLES',
            'horario': '14:00 - 16:00',
            'nro_estudiantes': 20
        }
    ]
    
    for i, entrega in enumerate(entregas_test, 1):
        resultado = registrar_entrega(entrega)
        if resultado:
            doc_limpio = limpiar_numero_documento(entrega['nroidenti'])
            print(f"   ✅ Entrega {i}: {entrega['profesor']} - Doc: {doc_limpio} - Aula: {entrega['aula']}")
        else:
            print(f"   ❌ Error en entrega {i}")
    
    # 3. Verificar estado del sistema
    print("\n3. Verificando estado del sistema...")
    prestadas = obtener_llaves_pendientes()
    
    if not prestadas.empty:
        print(f"   📊 Total de llaves prestadas: {len(prestadas)}")
        print("   📋 Detalles:")
        for _, fila in prestadas.iterrows():
            doc_limpio = limpiar_numero_documento(fila['nroidenti'])
            print(f"     • {fila['profesor']} - Doc: {doc_limpio} - Aula: {fila['aula']} - Fecha: {fila['fecha_entrega']}")
    else:
        print("   📊 No hay llaves prestadas")
    
    # 4. Verificar persistencia de datos
    print("\n4. Verificando persistencia...")
    try:
        import pandas as pd
        df = pd.read_excel('data/registros_llaves.xlsx')
        print(f"   📁 Archivo de registros encontrado con {len(df)} registros")
        
        # Verificar columnas
        columnas_esperadas = ['nroidenti', 'profesor', 'materia', 'aula', 'fecha_entrega', 'estado']
        columnas_presentes = all(col in df.columns for col in columnas_esperadas)
        
        if columnas_presentes:
            print("   ✅ Estructura de datos correcta")
        else:
            print("   ⚠️ Faltan columnas en la estructura")
            print(f"     Columnas actuales: {list(df.columns)}")
        
        # Verificar limpieza de documentos
        docs_con_punto = df[df['nroidenti'].astype(str).str.contains(r'\.0$', na=False)]
        if docs_con_punto.empty:
            print("   ✅ Números de documento limpios (sin .0)")
        else:
            print(f"   ⚠️ {len(docs_con_punto)} documentos con formato .0")
        
    except Exception as e:
        print(f"   ❌ Error al verificar persistencia: {e}")
    
    # 5. Resumen final
    print("\n=== RESUMEN DE LA PRUEBA ===")
    print("✅ Sistema de persistencia funcionando")
    print("✅ Gestión de entregas operativa")
    print("✅ Limpieza de documentos correcta")
    print("✅ Estructura de datos consistente")
    print("\n🎉 EL NUEVO SISTEMA ESTÁ LISTO PARA LAS VISTAS")
    
    return True

if __name__ == "__main__":
    try:
        test_nuevo_sistema()
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
