"""
Script de prueba para verificar la búsqueda por documento en el sistema
"""
import pandas as pd
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'llaves_control'))

def test_busqueda_documento():
    print("=== PRUEBA DE BÚSQUEDA POR DOCUMENTO ===")
    
    # Datos de prueba simulando la programación
    datos_programacion = {
        'nroidenti': ['12345678.0', '87654321', '11111111.0', '22222222', '33333333.0'],
        'profesor': ['JUAN PEREZ', 'MARIA GARCIA', 'CARLOS RODRIGUEZ', 'ANA MARTINEZ', 'LUIS GOMEZ'],
        'materia': ['MATEMATICAS I', 'FISICA II', 'QUIMICA GENERAL', 'HISTORIA', 'BIOLOGIA'],
        'aula': ['A101', 'B205', 'C301', 'D402', 'E503'],
        'dia': ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES'],
        'horario': ['08:00-10:00', '10:00-12:00', '14:00-16:00', '16:00-18:00', '07:00-09:00']
    }
    
    df_programacion = pd.DataFrame(datos_programacion)
    print("Datos de programación creados:")
    print(df_programacion.to_string())
    print()
    
    # Simular búsqueda por documento
    def buscar_por_documento(df, termino):
        """Simula la función de búsqueda mejorada"""
        termino = termino.strip().upper()
        
        # Crear columna con documentos limpios
        df_busqueda = df.copy()
        df_busqueda['nroidenti_limpio'] = df_busqueda['nroidenti'].astype(str).str.replace('.0', '', regex=False)
        
        # Buscar por nombre O por documento
        resultados = df_busqueda[
            (df_busqueda['profesor'].str.contains(termino, case=False, na=False)) |
            (df_busqueda['nroidenti_limpio'].str.contains(termino, case=False, na=False))
        ]
        
        return resultados
    
    # Pruebas de búsqueda
    casos_prueba = [
        '12345678',    # Documento sin .0
        '87654321',    # Documento que ya no tiene .0
        '1111',        # Parte de un documento
        'JUAN',        # Nombre del profesor
        'GARCIA',      # Apellido del profesor
        '2222'         # Parte de otro documento
    ]
    
    for caso in casos_prueba:
        print(f"--- Buscando: '{caso}' ---")
        resultados = buscar_por_documento(df_programacion, caso)
        
        if not resultados.empty:
            print(f"✅ Encontrados {len(resultados)} resultado(s):")
            for _, fila in resultados.iterrows():
                doc_limpio = str(fila['nroidenti']).replace('.0', '')
                print(f"   - {fila['profesor']} (Doc: {doc_limpio}) - {fila['materia']} - Aula {fila['aula']}")
        else:
            print("❌ No se encontraron resultados")
        print()
    
    print("🎉 PRUEBA DE BÚSQUEDA COMPLETADA")

if __name__ == "__main__":
    test_busqueda_documento()
