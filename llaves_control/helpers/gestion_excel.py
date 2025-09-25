from datetime import datetime
import os
from openpyxl import Workbook, load_workbook

# Obtener la ruta del directorio llaves_control
def obtener_ruta_data():
    """Obtiene la ruta correcta del directorio data dentro de llaves_control"""
    ruta_actual = os.path.dirname(os.path.abspath(__file__))  # helpers
    ruta_llaves_control = os.path.dirname(ruta_actual)  # llaves_control
    return os.path.join(ruta_llaves_control, "data")

def obtener_ruta_archivo(nombre_archivo):
    """Obtiene la ruta completa de un archivo en el directorio data"""
    return os.path.join(obtener_ruta_data(), nombre_archivo)

RUTA_REGISTRO = obtener_ruta_archivo('registros_llaves.xlsx')

def inicializar_registro():
    """Inicializa el archivo de registro si no existe"""
    directorio_data = obtener_ruta_data()
    if not os.path.exists(directorio_data):
        os.makedirs(directorio_data)
    
    if not os.path.exists(RUTA_REGISTRO):
        wb = Workbook()
        ws = wb.active
        
        # Encabezados actualizados según los requerimientos
        headers = [
            'Número de Documento', 'Docente', 'Día', 'Horario', 'Aula', 'Materia de la Clase',
            'Fecha de entrega', 'Hora de entrega', 'Fecha de devolución', 'Hora de devolución',
            'Estado'
        ]
        
        ws.append(headers)
        wb.save(RUTA_REGISTRO)

def limpiar_numero_documento(doc):
    """Limpia el número de documento eliminando .0 si existe"""
    doc_str = str(doc)
    if doc_str.endswith('.0'):
        return doc_str[:-2]
    return doc_str

def registrar_entrega(info_clase):
    """Registra la entrega de una llave con persistencia completa"""
    try:
        # Verificar si el archivo existe, si no crearlo
        if not os.path.exists(RUTA_REGISTRO):
            inicializar_registro()
        
        # Cargar workbook
        try:
            wb = load_workbook(RUTA_REGISTRO)
            ws = wb.active
        except:
            # Si falla, crear uno nuevo
            inicializar_registro()
            wb = load_workbook(RUTA_REGISTRO)
            ws = wb.active
        
        # Limpiar el número de documento
        nroidenti_limpio = limpiar_numero_documento(info_clase['nroidenti'])
        
        # Verificar si ya tiene una llave prestada - buscar en la columna correcta del estado
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and str(row[0]) == nroidenti_limpio and row[10] == 'En Préstamo':  # Columna 10 es 'Estado'
                return False  # Ya tiene una llave prestada
        
        # Preparar nuevo registro con la nueva estructura
        ahora = datetime.now()
        nuevo_registro = [
            nroidenti_limpio,                                    # Número de Documento
            info_clase.get('profesor', ''),                      # Docente
            info_clase.get('dia', ''),                          # Día
            info_clase.get('horario', ''),                      # Horario
            info_clase.get('aula', ''),                         # Aula
            info_clase.get('materia', ''),                      # Materia de la Clase
            ahora.strftime('%Y-%m-%d'),                         # Fecha de entrega
            ahora.strftime('%H:%M:%S'),                         # Hora de entrega
            '',                                                 # Fecha de devolución
            '',                                                 # Hora de devolución
            'En Préstamo'                                       # Estado
        ]
        
        # Agregar registro
        ws.append(nuevo_registro)
        
        # Guardar con manejo de errores
        try:
            wb.save(RUTA_REGISTRO)
            wb.close()
            return True
        except Exception as e:
            print(f"Error al guardar registro: {e}")
            return False
            
    except Exception as e:
        print(f"Error general en registrar_entrega: {e}")
        return False

def registrar_devolucion(nroidenti):
    """Registra la devolución de una llave por número de documento"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            return False
        
        wb = load_workbook(RUTA_REGISTRO)
        ws = wb.active
        
        # Limpiar el número de documento
        nroidenti_limpio = limpiar_numero_documento(nroidenti)
        
        # Buscar la llave entregada más reciente para este documento (sin fecha de devolución)
        fila_encontrada = None
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            if (row and str(row[0].value) == nroidenti_limpio and row[10].value == 'En Préstamo' and 
                (row[8].value is None or row[8].value == '' or row[8].value == 'N/A')):  # Sin fecha de devolución
                fila_encontrada = row_idx

        if fila_encontrada:
            # Actualizar registro con indexación base 1 (Excel)
            ahora = datetime.now()
            # Cambiar estado a "Devuelta" y registrar fecha/hora de devolución
            ws.cell(row=fila_encontrada, column=11, value='Devuelta')                     # Columna K: Estado
            ws.cell(row=fila_encontrada, column=9, value=ahora.strftime('%Y-%m-%d'))      # Columna I: Fecha de devolución
            ws.cell(row=fila_encontrada, column=10, value=ahora.strftime('%H:%M:%S'))     # Columna J: Hora de devolución            # Guardar
            wb.save(RUTA_REGISTRO)
            wb.close()
            return True
        else:
            wb.close()
            return False
            
    except Exception as e:
        print(f"Error al registrar devolución: {e}")
        return False

def verificar_llave_entregada(nroidenti):
    """Verifica si un profesor ya tiene una llave entregada"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            return False
        
        wb = load_workbook(RUTA_REGISTRO, read_only=True)
        ws = wb.active
        
        # Limpiar el número de documento
        nroidenti_limpio = limpiar_numero_documento(nroidenti)
        
        # Verificar si tiene llaves en préstamo - columna 10 es 'Estado'
        for row in ws.iter_rows(min_row=2, values_only=True):
            if (row and str(row[0]) == nroidenti_limpio and row[10] == 'En Préstamo'):
                wb.close()
                return True
        
        wb.close()
        return False
        
    except Exception as e:
        print(f"Error al verificar llave entregada: {e}")
        return False

def obtener_llaves_pendientes():
    """Obtiene todas las llaves que están entregadas (pendientes de devolución)"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            return []
        
        wb = load_workbook(RUTA_REGISTRO, read_only=True)
        ws = wb.active
        
        pendientes = []
        headers = [cell.value for cell in ws[1]]
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and any(row):  # Si la fila no está completamente vacía
                estado = row[10] if len(row) > 10 else None  # Columna 10 es 'Estado'
                
                # Solo incluir registros que estén "En Préstamo"
                if estado == 'En Préstamo':
                    registro = dict(zip(headers, row))
                    registro['Número de Documento'] = limpiar_numero_documento(registro['Número de Documento'])
                    pendientes.append(registro)
        
        wb.close()
        return pendientes
        
    except Exception as e:
        print(f"Error al obtener llaves pendientes: {e}")
        return []

def obtener_historial_completo():
    """Obtiene el historial completo de entregas y devoluciones"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            return []
        
        wb = load_workbook(RUTA_REGISTRO, read_only=True)
        ws = wb.active
        
        historial = []
        headers = [cell.value for cell in ws[1]]
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row:
                registro = dict(zip(headers, row))
                registro['Número de Documento'] = limpiar_numero_documento(registro['Número de Documento'])
                historial.append(registro)
        
        wb.close()
        return historial
        
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []

def generar_respaldo():
    """Genera un respaldo del archivo de registros"""
    try:
        if os.path.exists(RUTA_REGISTRO):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ruta_respaldo = obtener_ruta_archivo(f'respaldo_registros_{timestamp}.xlsx')
            
            # Copiar archivo usando openpyxl
            wb = load_workbook(RUTA_REGISTRO)
            wb.save(ruta_respaldo)
            wb.close()
            
            return ruta_respaldo
        return None
        
    except Exception as e:
        print(f"Error al generar respaldo: {e}")
        return None

def migrar_estructura_registro():
    """Migra el archivo de registros existente a la nueva estructura"""
    try:
        if not os.path.exists(RUTA_REGISTRO):
            print("No existe archivo de registros para migrar")
            return True
        
        # Generar respaldo antes de migrar
        respaldo = generar_respaldo()
        if respaldo:
            print(f"Respaldo generado en: {respaldo}")
        
        # Cargar archivo existente
        wb = load_workbook(RUTA_REGISTRO)
        ws = wb.active
        
        # Obtener todos los datos existentes
        datos_existentes = []
        headers_viejos = [cell.value for cell in ws[1]]
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row:
                registro = dict(zip(headers_viejos, row))
                datos_existentes.append(registro)
        
        wb.close()
        
        # Crear nuevo archivo con estructura actualizada
        wb_nuevo = Workbook()
        ws_nuevo = wb_nuevo.active
        
        # Nuevos encabezados
        headers_nuevos = [
            'Número de Documento', 'Docente', 'Día', 'Horario', 'Aula', 'Materia de la Clase',
            'Fecha de entrega', 'Hora de entrega', 'Fecha de devolución', 'Hora de devolución',
            'Estado'
        ]
        
        ws_nuevo.append(headers_nuevos)
        
        # Migrar datos existentes
        for registro in datos_existentes:
            # Determinar estado basado en si tiene fecha de devolución
            fecha_devolucion = registro.get('fecha_devolucion', '')
            estado_actual = 'En Préstamo'  # Por defecto, las entregas están "En Préstamo"
            if fecha_devolucion and fecha_devolucion != '' and fecha_devolucion != 'N/A':
                estado_actual = 'Devuelta'  # Si tiene fecha de devolución, está "Devuelta"
            
            nuevo_registro = [
                limpiar_numero_documento(registro.get('nroidenti', '')),  # Número de Documento
                registro.get('profesor', ''),                             # Docente
                registro.get('dia', ''),                                 # Día
                registro.get('horario', ''),                             # Horario
                registro.get('aula', ''),                                # Aula
                registro.get('materia', ''),                             # Materia de la Clase
                registro.get('fecha_entrega', ''),                       # Fecha de entrega
                registro.get('hora_entrega', ''),                        # Hora de entrega
                fecha_devolucion,                                        # Fecha de devolución
                registro.get('hora_devolucion', ''),                     # Hora de devolución
                estado_actual                                            # Estado
            ]
            
            ws_nuevo.append(nuevo_registro)
        
        # Guardar archivo migrado
        wb_nuevo.save(RUTA_REGISTRO)
        wb_nuevo.close()
        
        print(f"Migración completada. {len(datos_existentes)} registros migrados.")
        return True
        
    except Exception as e:
        print(f"Error al migrar estructura: {e}")
        return False