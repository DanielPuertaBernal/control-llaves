"""
Funciones de exportación alternativas para el sistema de control de llaves
"""
import pandas as pd
import os
from datetime import datetime

def exportar_registro_simple(historial, archivo_salida):
    """
    Exporta el registro de manera simple sin dependencias adicionales
    """
    try:
        # Intentar con openpyxl primero
        try:
            with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
                historial.to_excel(writer, sheet_name='Registro_Entregas', index=False)
                
                # Metadatos
                metadatos = pd.DataFrame({
                    'Información': [
                        'Fecha de Exportación',
                        'Total de Registros',
                        'Sistema'
                    ],
                    'Valor': [
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        len(historial),
                        'Control de Llaves v2.0'
                    ]
                })
                metadatos.to_excel(writer, sheet_name='Metadatos', index=False)
            return True, "Exportación exitosa con openpyxl"
            
        except ImportError:
            # Fallback a xlsxwriter
            try:
                with pd.ExcelWriter(archivo_salida, engine='xlsxwriter') as writer:
                    historial.to_excel(writer, sheet_name='Registro_Entregas', index=False)
                return True, "Exportación exitosa con xlsxwriter"
                
            except ImportError:
                # Fallback a CSV
                archivo_csv = archivo_salida.replace('.xlsx', '.csv')
                historial.to_csv(archivo_csv, index=False)
                return True, f"Exportación exitosa a CSV: {archivo_csv}"
                
    except Exception as e:
        return False, f"Error en exportación: {str(e)}"

def exportar_programacion_simple(programacion, archivo_salida):
    """
    Exporta la programación de manera simple sin dependencias adicionales
    """
    try:
        # Limpiar documentos
        programacion_limpia = programacion.copy()
        programacion_limpia['nroidenti'] = programacion_limpia['nroidenti'].apply(
            lambda x: str(x).replace('.0', '') if str(x).endswith('.0') else str(x)
        )
        
        # Intentar con openpyxl primero
        try:
            with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
                programacion_limpia.to_excel(writer, sheet_name='Programacion_Limpia', index=False)
                
                # Metadatos
                metadatos = pd.DataFrame({
                    'Información': [
                        'Fecha de Exportación',
                        'Total de Registros',
                        'Profesores Únicos',
                        'Sistema'
                    ],
                    'Valor': [
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        len(programacion_limpia),
                        programacion_limpia['profesor'].nunique() if 'profesor' in programacion_limpia.columns else 0,
                        'Control de Llaves v2.0'
                    ]
                })
                metadatos.to_excel(writer, sheet_name='Metadatos', index=False)
            return True, "Exportación exitosa con openpyxl"
            
        except ImportError:
            # Fallback a xlsxwriter
            try:
                with pd.ExcelWriter(archivo_salida, engine='xlsxwriter') as writer:
                    programacion_limpia.to_excel(writer, sheet_name='Programacion_Limpia', index=False)
                return True, "Exportación exitosa con xlsxwriter"
                
            except ImportError:
                # Fallback a CSV
                archivo_csv = archivo_salida.replace('.xlsx', '.csv')
                programacion_limpia.to_csv(archivo_csv, index=False)
                return True, f"Exportación exitosa a CSV: {archivo_csv}"
                
    except Exception as e:
        return False, f"Error en exportación: {str(e)}"

def test_exportacion_funciones():
    """
    Prueba las funciones de exportación alternativas
    """
    print("=== PRUEBA DE FUNCIONES DE EXPORTACIÓN ===")
    
    # Crear datos de prueba
    datos_test = pd.DataFrame({
        'nroidenti': ['12345678.0', '87654321', '11111111.0'],
        'profesor': ['JUAN PEREZ', 'MARIA GARCIA', 'CARLOS RODRIGUEZ'],
        'materia': ['MATEMATICAS I', 'FISICA II', 'QUIMICA GENERAL'],
        'aula': ['A101', 'B205', 'C301'],
        'dia': ['LUNES', 'MARTES', 'MIERCOLES'],
        'horario': ['08:00-10:00', '10:00-12:00', '14:00-16:00'],
        'estado': ['Entregada', 'Devuelta', 'Entregada']
    })
    
    # Probar exportación de registro
    print("🔍 Probando exportación de registro...")
    exito, mensaje = exportar_registro_simple(datos_test, 'test_registro.xlsx')
    print(f"{'✅' if exito else '❌'} {mensaje}")
    
    # Probar exportación de programación
    print("🔍 Probando exportación de programación...")
    exito, mensaje = exportar_programacion_simple(datos_test, 'test_programacion.xlsx')
    print(f"{'✅' if exito else '❌'} {mensaje}")
    
    # Limpiar archivos de prueba
    for archivo in ['test_registro.xlsx', 'test_programacion.xlsx', 'test_registro.csv', 'test_programacion.csv']:
        if os.path.exists(archivo):
            os.remove(archivo)
            print(f"🗑️ Archivo {archivo} eliminado")

if __name__ == "__main__":
    test_exportacion_funciones()
