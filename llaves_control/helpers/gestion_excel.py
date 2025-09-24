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
        
        # Encabezados
        headers = [
            'nroidenti', 'profesor', 'materia', 'aula',
            'dia', 'horario', 'nro_estudiantes',
            'fecha_entrega', 'hora_entrega', 'fecha_devolucion', 'hora_devolucion',
            'estado', 'observaciones'
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
        
        # Verificar si ya tiene una llave prestada - optimizado
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and str(row[0]) == nroidenti_limpio and row[11] == 'Entregada':
                return False  # Ya tiene una llave prestada
        
        # Preparar nuevo registro
        ahora = datetime.now()
        nuevo_registro = [
            nroidenti_limpio,
            info_clase.get('profesor', ''),
            info_clase.get('materia', ''),
            info_clase.get('aula', ''),
            info_clase.get('dia', ''),
            info_clase.get('horario', ''),
            info_clase.get('nro_estudiantes', 0),
            ahora.strftime('%Y-%m-%d'),
            ahora.strftime('%H:%M:%S'),
            '',  # fecha_devolucion
            '',  # hora_devolucion
            'Entregada',
            ''   # observaciones
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
        
        # Buscar la llave entregada más reciente para este documento
        fila_encontrada = None
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            if row and str(row[0].value) == nroidenti_limpio and row[11].value == 'Entregada':
                fila_encontrada = row_idx
        
        if fila_encontrada:
            # Actualizar registro
            ahora = datetime.now()
            ws.cell(row=fila_encontrada, column=12, value='Devuelta')  # estado
            ws.cell(row=fila_encontrada, column=10, value=ahora.strftime('%Y-%m-%d'))  # fecha_devolucion
            ws.cell(row=fila_encontrada, column=11, value=ahora.strftime('%H:%M:%S'))  # hora_devolucion
            
            # Guardar
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
        
        # Verificar si tiene llaves entregadas
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and str(row[0]) == nroidenti_limpio and row[11] == 'Entregada':
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
            if row and row[11] == 'Entregada':  # estado == 'Entregada'
                registro = dict(zip(headers, row))
                registro['nroidenti'] = limpiar_numero_documento(registro['nroidenti'])
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
                registro['nroidenti'] = limpiar_numero_documento(registro['nroidenti'])
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