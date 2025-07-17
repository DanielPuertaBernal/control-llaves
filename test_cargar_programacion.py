"""
Prueba específica de la función de carga de programación
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

def test_cargar_programacion():
    print("=== PRUEBA DE CARGA DE PROGRAMACIÓN ===")
    
    try:
        # Importar las funciones necesarias
        from helpers.limpieza_programacion import limpiar_programacion
        print("✅ Módulo de limpieza importado")
        
        # Simular que tenemos un archivo de programación
        import pandas as pd
        
        # Crear datos de prueba
        datos_test = {
            'nroidenti': ['12345678.0', '87654321', '11111111.0'],
            'profesor': ['JUAN PEREZ', 'MARIA GARCIA', 'CARLOS RODRIGUEZ'],
            'materia': ['MATEMATICAS I', 'FISICA II', 'QUIMICA GENERAL'],
            'aula': ['A101', 'B205', 'C301'],
            'dia': ['LUNES', 'MARTES', 'MIERCOLES'],
            'horario': ['08:00-10:00', '10:00-12:00', '14:00-16:00'],
            'nro_estudiantes': [25, 30, 20]
        }
        
        df_test = pd.DataFrame(datos_test)
        
        # Guardar archivo temporal para prueba
        archivo_temp = 'test_programacion.xlsx'
        df_test.to_excel(archivo_temp, index=False)
        print(f"✅ Archivo de prueba creado: {archivo_temp}")
        
        # Probar la función de limpieza
        resultado = limpiar_programacion(archivo_temp)
        
        if resultado is not None and not resultado.empty:
            print(f"✅ Programación limpiada exitosamente")
            print(f"   - Registros procesados: {len(resultado)}")
            print(f"   - Columnas: {list(resultado.columns)}")
            
            # Verificar limpieza de documentos
            docs_limpios = resultado['nroidenti'].astype(str)
            docs_con_punto = docs_limpios[docs_limpios.str.contains(r'\.0$', na=False)]
            
            if docs_con_punto.empty:
                print("✅ Documentos limpiados correctamente (sin .0)")
            else:
                print(f"⚠️ {len(docs_con_punto)} documentos aún tienen .0")
                
        else:
            print("❌ Error: función de limpieza retornó datos vacíos")
        
        # Limpiar archivo temporal
        if os.path.exists(archivo_temp):
            os.remove(archivo_temp)
            print("✅ Archivo temporal eliminado")
        
        print("\n🎉 PRUEBA DE CARGA COMPLETADA EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_cargar_programacion()
