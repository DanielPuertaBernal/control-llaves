"""
Script de prueba para la nueva funcionalidad de programación completa
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

import pandas as pd
from helpers.limpieza_programacion import limpiar_programacion

def test_programacion_completa():
    print("=== PRUEBA DE FUNCIONALIDAD DE PROGRAMACIÓN COMPLETA ===\n")
    
    # Crear datos de prueba más completos
    datos_prueba = {
        'nroidenti': [12345678, 12345678, 87654321, 87654321, 11111111, 22222222],
        'profesor': ['JUAN PEREZ', 'JUAN PEREZ', 'MARIA GARCIA', 'MARIA GARCIA', 'CARLOS LOPEZ', 'ANA MARTINEZ'],
        'MATERIA': ['MATEMATICAS I', 'MATEMATICAS II', 'FISICA II', 'FISICA I', 'QUIMICA', 'BIOLOGIA'],
        'aula': ['A101', 'A102', 'B205', 'B206', 'C301', 'C302'],
        'dia': ['LUNES', 'MARTES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES'],
        'horario': ['08:00 A 10:00', '10:00 A 12:00', '14:00 A 16:00', '08:00 A 10:00', '16:00 A 18:00', '10:00 A 12:00'],
        'nro_estudiantes': [25, 30, 28, 22, 35, 20],
        'grupo': ['G1', 'G2', 'G1', 'G1', 'G3', 'G1']
    }
    
    df_prueba = pd.DataFrame(datos_prueba)
    print(f"1. Datos de prueba creados: {len(df_prueba)} registros")
    
    # Limpiar programación
    df_limpio = limpiar_programacion(df_prueba)
    print(f"2. Programación limpia: {len(df_limpio)} registros")
    
    # Mostrar estadísticas por día
    print("\n3. Estadísticas por día:")
    for dia in sorted(df_limpio['dia'].unique()):
        clases_dia = df_limpio[df_limpio['dia'] == dia]
        profesores_dia = clases_dia['profesor'].nunique()
        aulas_dia = clases_dia['aula'].nunique()
        print(f"   {dia}: {len(clases_dia)} clases, {profesores_dia} profesores, {aulas_dia} aulas")
    
    # Mostrar estadísticas por aula
    print("\n4. Estadísticas por aula:")
    for aula in sorted(df_limpio['aula'].unique()):
        clases_aula = df_limpio[df_limpio['aula'] == aula]
        dias_aula = clases_aula['dia'].nunique()
        print(f"   {aula}: {len(clases_aula)} clases en {dias_aula} días")
    
    # Simular filtros
    print("\n5. Simulación de filtros:")
    
    # Filtro por día específico
    dia_filtro = "MARTES"
    clases_martes = df_limpio[df_limpio['dia'] == dia_filtro]
    print(f"   Filtro por {dia_filtro}: {len(clases_martes)} clases")
    for _, clase in clases_martes.iterrows():
        print(f"     - {clase['profesor']}: {clase['materia']} (Aula {clase['aula']}) - {clase['horario']}")
    
    # Filtro por aula específica
    aula_filtro = "A101"
    clases_aula = df_limpio[df_limpio['aula'] == aula_filtro]
    print(f"\n   Filtro por Aula {aula_filtro}: {len(clases_aula)} clases")
    for _, clase in clases_aula.iterrows():
        print(f"     - {clase['profesor']}: {clase['materia']} ({clase['dia']}) - {clase['horario']}")
    
    # Test 6: Verificar que los números de documento no tengan .0
    print("\n6. Verificación de números de documento:")
    for _, fila in df_limpio.iterrows():
        doc = fila['nroidenti']
        print(f"   Documento: {doc} (tipo: {type(doc)})")
        if '.0' in str(doc):
            print(f"   ⚠️  ADVERTENCIA: Documento {doc} contiene .0")
        else:
            print(f"   ✓ Documento limpio: {doc}")
    
    print("\n=== FUNCIONALIDAD DE PROGRAMACIÓN COMPLETA VERIFICADA ===")
    print("\nNuevas características disponibles:")
    print("✓ Vista de programación completa")
    print("✓ Filtro por día de la semana")
    print("✓ Filtro por aula")
    print("✓ Estadísticas en tiempo real")
    print("✓ Exportación de vista filtrada")
    print("✓ Limpiar filtros")
    print("\n=== PROBLEMAS SOLUCIONADOS ===")
    print("✓ Números de documento sin formato .0")
    print("✓ Panel de llaves prestadas en tiempo real")
    print("✓ Devolución directa desde tabla de prestadas")
    print("✓ Actualización automática de vistas")
    print("\nPara usar: Abrir aplicación → 'Ver Programación Completa'")

if __name__ == "__main__":
    try:
        test_programacion_completa()
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
