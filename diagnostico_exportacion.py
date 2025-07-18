"""
Script de diagnóstico para problemas de exportación
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

def diagnosticar_exportacion():
    print("=== DIAGNÓSTICO DE EXPORTACIÓN ===")
    print()
    
    # Verificar dependencias
    print("🔍 VERIFICANDO DEPENDENCIAS...")
    
    # Pandas
    try:
        import pandas as pd
        print(f"✅ pandas: {pd.__version__}")
    except ImportError as e:
        print(f"❌ pandas: NO INSTALADO - {e}")
        return False
    
    # OpenPyXL
    try:
        import openpyxl
        print(f"✅ openpyxl: {openpyxl.__version__}")
    except ImportError as e:
        print(f"❌ openpyxl: NO INSTALADO - {e}")
        print("   📋 Solución: pip install openpyxl")
        return False
    
    # Tkinter
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
        print("✅ tkinter: Disponible")
    except ImportError as e:
        print(f"❌ tkinter: NO DISPONIBLE - {e}")
        return False
    
    # Datetime
    try:
        from datetime import datetime
        print(f"✅ datetime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except ImportError as e:
        print(f"❌ datetime: NO DISPONIBLE - {e}")
        return False
    
    print()
    print("🔍 PROBANDO FUNCIONALIDAD DE EXPORTACIÓN...")
    
    # Crear datos de prueba
    try:
        datos_test = pd.DataFrame({
            'nroidenti': ['12345678', '87654321', '11111111'],
            'profesor': ['JUAN PEREZ', 'MARIA GARCIA', 'CARLOS RODRIGUEZ'],
            'materia': ['MATEMATICAS I', 'FISICA II', 'QUIMICA GENERAL'],
            'aula': ['A101', 'B205', 'C301'],
            'dia': ['LUNES', 'MARTES', 'MIERCOLES'],
            'horario': ['08:00-10:00', '10:00-12:00', '14:00-16:00'],
            'estado': ['Entregada', 'Devuelta', 'Entregada']
        })
        print("✅ Datos de prueba creados")
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return False
    
    # Probar exportación a Excel
    try:
        archivo_test = 'test_exportacion.xlsx'
        
        # Usando ExcelWriter
        with pd.ExcelWriter(archivo_test, engine='openpyxl') as writer:
            datos_test.to_excel(writer, sheet_name='Datos_Principales', index=False)
            
            # Metadatos
            metadatos = pd.DataFrame({
                'Info': ['Fecha', 'Registros', 'Profesores'],
                'Valor': [datetime.now().strftime('%Y-%m-%d'), len(datos_test), datos_test['profesor'].nunique()]
            })
            metadatos.to_excel(writer, sheet_name='Metadatos', index=False)
        
        print(f"✅ Archivo Excel creado: {archivo_test}")
        
        # Verificar que el archivo existe
        if os.path.exists(archivo_test):
            size = os.path.getsize(archivo_test)
            print(f"✅ Archivo verificado: {size} bytes")
            
            # Leer el archivo para verificar contenido
            df_verificacion = pd.read_excel(archivo_test, sheet_name='Datos_Principales')
            print(f"✅ Contenido verificado: {len(df_verificacion)} filas")
            
            # Limpiar archivo de prueba
            os.remove(archivo_test)
            print("✅ Archivo de prueba eliminado")
            
        else:
            print("❌ Archivo no se creó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error en exportación de prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("🔍 VERIFICANDO FUNCIONES DEL SISTEMA...")
    
    # Verificar funciones del helper
    try:
        from helpers.gestion_excel import obtener_historial_completo
        print("✅ Función obtener_historial_completo importada")
    except ImportError as e:
        print(f"❌ Error importando obtener_historial_completo: {e}")
        return False
    
    try:
        from helpers.limpieza_programacion import limpiar_programacion
        print("✅ Función limpiar_programacion importada")
    except ImportError as e:
        print(f"❌ Error importando limpiar_programacion: {e}")
        return False
    
    print()
    print("🎉 DIAGNÓSTICO COMPLETADO")
    print("✅ Todas las dependencias están disponibles")
    print("✅ La funcionalidad de exportación debería funcionar correctamente")
    
    print()
    print("🔧 POSIBLES CAUSAS DE ERRORES:")
    print("1. Archivo Excel abierto en otro programa")
    print("2. Permisos de escritura en la carpeta de destino")
    print("3. Nombre de archivo inválido o muy largo")
    print("4. Datos corruptos en el DataFrame")
    print("5. Falta de espacio en disco")
    
    return True

if __name__ == "__main__":
    if diagnosticar_exportacion():
        print("\n🚀 SISTEMA LISTO PARA EXPORTAR")
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS - REVISE LAS DEPENDENCIAS")
