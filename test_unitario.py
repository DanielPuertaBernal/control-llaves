# Archivo único para pruebas unitarias
import unittest
import pandas as pd
from llaves_control.helpers.limpieza_programacion import limpiar_programacion
from llaves_control.helpers.gestion_excel import *

class TestLimpiezaProgramacion(unittest.TestCase):
    def test_limpieza_total(self):
        # Aquí puedes agregar pruebas específicas
        pass
    
    def test_no_unificar_grupos_diferentes(self):
        """
        Test para verificar que no se unifiquen clases de grupos diferentes
        del mismo docente en el mismo día
        """
        # Crear datos de prueba que simulen el problema reportado
        datos_prueba = pd.DataFrame({
            'nroidenti': ['12345678', '12345678'],
            'profesor': ['JUAN PEREZ', 'JUAN PEREZ'],
            'materia': ['MATEMATICAS I', 'MATEMATICAS I'],
            'aula': ['AULA 101', 'AULA 101'],
            'dia': ['MARTES', 'MARTES'],
            'grupo': ['GRUPO A', 'GRUPO B'],
            'horario': ['7:00 a 10:00', '18:00 a 20:00'],
            'nro_estudiantes': [25, 30]
        })
        
        # Aplicar limpieza
        resultado = limpiar_programacion(datos_prueba)
        
        # Verificar que se mantienen 2 registros (uno por grupo)
        self.assertEqual(len(resultado), 2, 
                        "Debería mantener 2 registros para grupos diferentes")
        
        # Verificar que los grupos se mantienen separados
        grupos_resultado = sorted(resultado['Grupo'].tolist())
        self.assertEqual(grupos_resultado, ['GRUPO A', 'GRUPO B'],
                        "Los grupos deben mantenerse separados")
        
        print("✅ Test pasado: No se unifican clases de grupos diferentes")
    
    def test_caso_especifico_reportado(self):
        """
        Test del caso específico reportado: 
        Docente con clase de 7 a 10 y de 18 a 20 el mismo día con grupos diferentes
        """
        datos_caso_real = pd.DataFrame({
            'nroidenti': ['87654321', '87654321'],
            'profesor': ['MARIA RODRIGUEZ', 'MARIA RODRIGUEZ'],
            'materia': ['CALCULO I', 'CALCULO I'],
            'aula': ['AULA 205', 'AULA 205'],
            'dia': ['MARTES', 'MARTES'],
            'grupo': ['01', '02'],  # Grupos diferentes
            'horario': ['7:00 a 10:00', '18:00 a 20:00'],
            'nro_estudiantes': [28, 32]
        })
        
        # Aplicar limpieza
        resultado = limpiar_programacion(datos_caso_real)
        
        # Verificar que NO se unifique en un solo horario (7:00 a 20:00)
        self.assertEqual(len(resultado), 2, 
                        "No debe unificar clases de grupos diferentes")
        
        # Verificar horarios específicos
        horarios = sorted(resultado['Horario'].tolist())
        # Verificar que contiene partes de los horarios originales (formato puede variar)
        self.assertTrue(any('07:00' in h or '7:00' in h for h in horarios),
                       f"Debe mantener el horario matutino. Horarios: {horarios}")
        self.assertTrue(any('18:00' in h for h in horarios),
                       f"Debe mantener el horario vespertino. Horarios: {horarios}")
        
        print(f"✅ Test caso específico pasado: Horarios mantenidos correctamente: {horarios}")
    
    def test_gap_tiempo_mayor_30_minutos(self):
        """
        Test para verificar que clases con gap > 30 minutos se mantienen separadas
        aunque sean del mismo grupo y materia
        """
        datos_con_gap = pd.DataFrame({
            'nroidenti': ['11111111', '11111111'],
            'profesor': ['ANA GARCIA', 'ANA GARCIA'], 
            'materia': ['FISICA I', 'FISICA I'],
            'aula': ['LAB 101', 'LAB 101'],
            'dia': ['MIERCOLES', 'MIERCOLES'],
            'grupo': ['01', '01'],  # MISMO GRUPO
            'horario': ['10:00 a 12:00', '14:00 a 16:00'],  # GAP de 2 horas
            'nro_estudiantes': [20, 20]
        })
        
        # Aplicar limpieza
        resultado = limpiar_programacion(datos_con_gap)
        
        # Verificar que se mantienen 2 registros (gap > 30 min)
        self.assertEqual(len(resultado), 2,
                        f"Debe mantener 2 clases separadas por gap > 30min. Resultado: {len(resultado)}")
        
        # Verificar que NO se unifique en 10:00 a 16:00
        horarios = resultado['Horario'].tolist()
        no_unificado = not any('10:00' in h and '16:00' in h for h in horarios)
        self.assertTrue(no_unificado,
                       f"No debe unificar clases con gap > 30min. Horarios: {horarios}")
        
        print(f"✅ Test gap > 30min pasado: {horarios}")
    
    def test_clases_continuas_sin_gap(self):
        """
        Test para verificar que clases continuas (sin gap) sí se unifican
        """
        datos_continuos = pd.DataFrame({
            'nroidenti': ['22222222', '22222222'],
            'profesor': ['LUIS MARTINEZ', 'LUIS MARTINEZ'],
            'materia': ['QUIMICA I', 'QUIMICA I'],
            'aula': ['LAB 201', 'LAB 201'],
            'dia': ['JUEVES', 'JUEVES'],
            'grupo': ['02', '02'],  # MISMO GRUPO
            'horario': ['8:00 a 10:00', '10:00 a 12:00'],  # SIN GAP (continuas)
            'nro_estudiantes': [25, 25]
        })
        
        # Aplicar limpieza
        resultado = limpiar_programacion(datos_continuos)
        
        # Verificar que se unifique en 1 registro (sin gap)
        self.assertEqual(len(resultado), 1,
                        f"Debe unificar clases continuas. Resultado: {len(resultado)}")
        
        # Verificar que se unifique correctamente
        horario_unificado = resultado['Horario'].iloc[0]
        self.assertTrue('8:00' in horario_unificado and '12:00' in horario_unificado,
                       f"Debe unificar de 8:00 a 12:00. Resultado: {horario_unificado}")
        
        print(f"✅ Test clases continuas pasado: {horario_unificado}")
    
    def test_nombres_columnas_exportacion(self):
        """
        Test para verificar que las columnas tienen los nombres correctos
        """
        datos_prueba = pd.DataFrame({
            'semestre': ['2024-1'],
            'materia': ['MAT101'],
            'inp': ['INP001'],
            'grupo': ['01'],
            'nroidenti': ['12345678'],
            'profesor': ['JUAN PEREZ'],
            'dia': ['LUNES'],
            'horario': ['8:00 a 10:00'],
            'aula': ['AULA 101']
        })
        
        # Aplicar limpieza
        resultado = limpiar_programacion(datos_prueba)
        
        # Verificar nombres de columnas específicos (sin las columnas excluidas)
        columnas_esperadas = [
            'Código de la Materia', 'Grupo',
            'Número de Documento', 'Docente', 'Día', 'Horario', 'Aula', 'Observaciones'
        ]
        
        columnas_no_deseadas = ['Semestre', 'INP', 'Semanas', 'Número de Horas', 'Fecha Inicio', 'Fecha Fin']
        
        for col_esperada in columnas_esperadas:
            self.assertIn(col_esperada, resultado.columns,
                         f"La columna '{col_esperada}' debería estar presente")
        
        for col_no_deseada in columnas_no_deseadas:
            self.assertNotIn(col_no_deseada, resultado.columns,
                           f"La columna '{col_no_deseada}' NO debería estar presente")
        
        print(f"✅ Test nombres de columnas pasado: {list(resultado.columns)}")
    
    def test_valores_estudiantes(self):
        """
        Test para verificar que se muestran correctamente los valores de estudiantes
        """
        datos_estudiantes = pd.DataFrame({
            'nroidenti': ['12345678'],
            'profesor': ['MARIA LOPEZ'],
            'materia': ['FIS101'],
            'grupo': ['01'],
            'aula': ['LAB 201'],
            'dia': ['MARTES'],
            'horario': ['10:00 a 12:00'],
            'nro_estudiantes_premat': [15],  # Prematriculados
            'nro_estudiantes': [12],         # Matriculados 
            'TOTAL': [27]                    # Total
        })
        
        # Aplicar limpieza
        resultado = limpiar_programacion(datos_estudiantes)
        
        # Verificar que las columnas de estudiantes existen
        self.assertIn('Estudiantes Prematriculados', resultado.columns)
        self.assertIn('Estudiantes Matriculados', resultado.columns)
        self.assertIn('Total de Estudiantes', resultado.columns)
        
        # Verificar los valores específicos
        fila = resultado.iloc[0]
        premat_val = int(fila['Estudiantes Prematriculados'])
        matric_val = int(fila['Estudiantes Matriculados'])  
        total_val = int(fila['Total de Estudiantes'])
        
        self.assertEqual(premat_val, 15, 
                        "Debe mostrar 15 estudiantes prematriculados")
        self.assertEqual(matric_val, 12, 
                        "Debe mostrar 12 estudiantes matriculados")
        self.assertEqual(total_val, 27, 
                        "Debe mostrar 27 estudiantes en total")
        
        print(f"✅ Test valores estudiantes pasado:")
        print(f"   - Prematriculados: {premat_val}")
        print(f"   - Matriculados: {matric_val}")  
        print(f"   - Total: {total_val}")
    
    def test_calculo_total_estudiantes(self):
        """
        Test para verificar que el total se calcula correctamente sumando 
        prematriculados + matriculados (NO usando columna TOTAL externa)
        """
        datos_calculo = pd.DataFrame({
            'semestre': ['2024-1'],
            'materia': ['MAT101'], 
            'inp': ['001'],
            'grupo': ['01'],
            'nivel_grupo': ['PREGRADO'],
            'nroidenti': ['87654321'],
            'profesor': ['CARLOS MARTINEZ'],
            'dia': ['MIERCOLES'],
            'horario': ['14:00 a 16:00'],
            'aula': ['AULA 303'],
            'nro_estudiantes_premat': [8],    # Prematriculados
            'nro_estudiantes': [17],          # Matriculados
            'descripcion': ['ALGEBRA LINEAL'] # Descripción de la materia
        })
        
        # Aplicar limpieza
        resultado = limpiar_programacion(datos_calculo)
        
        # Verificar que el cálculo es correcto
        fila = resultado.iloc[0]
        premat_val = int(fila['Estudiantes Prematriculados'])
        matric_val = int(fila['Estudiantes Matriculados'])  
        total_val = int(fila['Total de Estudiantes'])
        
        # El total debe ser la SUMA de prematriculados + matriculados
        total_esperado = premat_val + matric_val
        
        self.assertEqual(premat_val, 8, "Debe mostrar 8 prematriculados")
        self.assertEqual(matric_val, 17, "Debe mostrar 17 matriculados")
        self.assertEqual(total_val, total_esperado, 
                        f"Total debe ser {total_esperado} (8+17), pero fue {total_val}")
        self.assertEqual(total_val, 25, "Total específico debe ser 25")
        
        # Verificar que descripción se mapea correctamente
        self.assertIn('Materia de la Clase', resultado.columns)
        
        print(f"✅ Test cálculo total pasado:")
        print(f"   - Prematriculados: {premat_val}")
        print(f"   - Matriculados: {matric_val}")
        print(f"   - Total calculado: {total_val} = {premat_val} + {matric_val}")

if __name__ == "__main__":
    unittest.main()
