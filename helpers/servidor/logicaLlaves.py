from datetime import datetime, timedelta
import pandas as pd
from helpers.gestionExcel import (
    RegistrarEntrega,
    VerificarLlaveEntregada,
    LimpiarNumeroDocumento,
    RegistrarDevolucion
)
from helpers.limpiezaProgramacion import ObtenerRutaArchivo


def procesar_entrega(cedula):
    """Procesa la entrega automática basada en el número de documento NFC."""
    try:
        cedula_limpia = LimpiarNumeroDocumento(cedula)

        if VerificarLlaveEntregada(cedula_limpia):
            return {'success': False, 'mensaje': 'El docente ya tiene una llave entregada'}

        clase_actual = buscar_clase_actual(cedula_limpia)
        if not clase_actual:
            return {'success': False, 'mensaje': 'No se encontró clase activa'}

        if RegistrarEntrega(clase_actual):
            return {
                'success': True,
                'mensaje': 'Llave entregada exitosamente',
                'documento': cedula_limpia,
                'docente': clase_actual.get('profesor'),
                'aula': clase_actual.get('aula'),
                'horario': clase_actual.get('horario'),
                'materia': clase_actual.get('materia'),
                'fecha_entrega': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {'success': False, 'mensaje': 'Error al registrar la entrega'}
    except Exception as e:
        return {'success': False, 'mensaje': f'Error al procesar entrega: {str(e)}'}


def procesar_devolucion(cedula, aula):
    """Procesa la devolución de la llave según documento y aula."""
    try:
        cedula_limpia = LimpiarNumeroDocumento(cedula)
        resultado = RegistrarDevolucion(cedula_limpia, aula)

        if resultado:
            return {
                'success': True,
                'mensaje': 'Llave devuelta exitosamente',
                'documento': cedula_limpia,
                'aula': aula,
                'fecha_devolucion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {'success': False, 'mensaje': 'Error al registrar devolución'}
    except Exception as e:
        return {'success': False, 'mensaje': f'Error en devolución: {str(e)}'}


def buscar_clase_actual(cedula):
    """Busca la clase activa del docente según día y hora."""
    try:
        ruta_programacion = ObtenerRutaArchivo("programacionLimpiaActual.xlsx")
        df = pd.read_excel(ruta_programacion)
        ahora = datetime.now()
        dia_numero = ahora.weekday()
        dias_espanol = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        dia_actual = dias_espanol[dia_numero]
        hora_actual = ahora.time()

        df['Número de Documento'] = df['Número de Documento'].astype(str).apply(LimpiarNumeroDocumento)
        df_docente = df[(df['Número de Documento'] == cedula) & (df['Día'] == dia_actual)]

        if df_docente.empty:
            return None

        for _, fila in df_docente.iterrows():
            horario = str(fila['Horario'])
            if ' a ' in horario.lower():
                hora_ini_str, hora_fin_str = horario.lower().split(' a ')
                hora_ini = datetime.strptime(hora_ini_str.strip(), '%H:%M:%S').time()
                hora_fin = datetime.strptime(hora_fin_str.strip(), '%H:%M:%S').time()

                hora_ini_dt = datetime.combine(datetime.today(), hora_ini)
                ventana_inicio = (hora_ini_dt - timedelta(minutes=30)).time()

                if ventana_inicio <= hora_actual <= hora_fin:
                    return {
                        'nroidenti': cedula,
                        'profesor': str(fila['Docente']),
                        'dia': dia_actual,
                        'horario': horario,
                        'aula': str(fila['Aula']),
                        'materia': str(fila['Materia de la Clase'])
                    }
        return None
    except Exception as e:
        print(f"Error buscando clase actual: {e}")
        return None
