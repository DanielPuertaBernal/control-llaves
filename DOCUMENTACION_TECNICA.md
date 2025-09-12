# Sistema de Control de Llaves - Documentación Técnica

## Descripción General

Sistema modular para gestión de entrega y devolución de llaves académicas con arquitectura basada en vistas especializadas. Procesa programación académica, gestiona registros de llaves y genera informes exportables.

## Arquitectura del Sistema

### Estructura Modular

```
llaves_control/
├── main.py                    # Punto de entrada
├── ui/
│   ├── interfaz.py           # Coordinador principal (27 líneas)
│   ├── entrega_devolucion.py # Vista gestión de llaves
│   ├── programacion.py       # Vista procesamiento académico  
│   └── informes.py           # Vista reportes y análisis
├── helpers/
│   ├── gestion_excel.py      # Persistencia y registros
│   └── limpieza_programacion.py # Procesamiento de datos
├── assets/
│   └── estilo_tkinter.py     # Estilos y temas UI
└── data/
    └── registros_llaves.xlsx # Base de datos Excel
```

### Patrón de Diseño

- **Separación de responsabilidades**: Cada módulo tiene una función específica
- **Vista-Controlador**: Las vistas manejan UI y lógica de negocio
- **Inyección de dependencias**: App principal se inyecta en vistas
- **Persistencia centralizada**: Helpers manejan datos y archivos

## Flujo de Trabajo del Sistema

### 1. Inicialización

```
main.py → App() → inicializar_registro() → aplicar_estilo() → crear_vistas_modulares()
```

### 2. Carga de Programación

```
Vista Programación → cargar_programacion() → limpiar_programacion() → App.programacion
```

- **Entrada**: Archivo Excel/CSV con programación académica
- **Proceso**: Limpieza, consolidación, suma estudiantes (premat + matriculados)
- **Salida**: DataFrame procesado en memoria

### 3. Búsqueda de Profesores

```
Vista Entrega → buscar_profesor() → filtrar_por_nombre_y_documento() → mostrar_resultados()
```

- **Entrada**: Término de búsqueda (nombre o documento)
- **Proceso**: Búsqueda dual en programación cargada
- **Salida**: Lista filtrada en TreeView

### 4. Gestión de Llaves

```
Entrega: seleccionar_profesor() → registrar_entrega() → actualizar_persistencia()
Devolución: seleccionar_prestada() → registrar_devolucion() → actualizar_estado()
```

### 5. Generación de Informes

```
Vista Informes → generar_informe() → procesar_datos() → mostrar_resultados() → exportar()
```

## Documentación de Funciones

### Módulo: `helpers/gestion_excel.py`

#### `inicializar_registro()`

- **Entrada**: Ninguna
- **Proceso**: Crea estructura de carpetas y archivo Excel base
- **Salida**: Archivo `data/registros_llaves.xlsx` inicializado
- **Uso**: Ejecutado al inicio de la aplicación

#### `registrar_entrega(info_clase: dict) -> bool`

- **Entrada**:
  ```python
  {
      'nroidenti': str,      # Documento limpio
      'profesor': str,       # Nombre profesor
      'materia': str,        # Materia
      'aula': str,          # Código aula
      'dia': str,           # Día semana
      'horario': str,       # Horario clase
      'nro_estudiantes': int # Total estudiantes
  }
  ```
- **Proceso**: Valida no duplicados, registra con timestamp
- **Salida**: `True` si éxito, `False` si error o ya prestada

#### `registrar_devolucion(nroidenti: str) -> bool`

- **Entrada**: Documento del profesor (string)
- **Proceso**: Busca última entrega activa, actualiza estado
- **Salida**: `True` si devolución exitosa, `False` si no encontrada

#### `obtener_llaves_pendientes() -> pd.DataFrame`

- **Entrada**: Ninguna
- **Proceso**: Filtra registros con estado 'Entregada'
- **Salida**: DataFrame con llaves no devueltas

#### `limpiar_numero_documento(doc) -> str`

- **Entrada**: Documento (cualquier tipo)
- **Proceso**: Convierte a string, elimina '.0' si existe
- **Salida**: Documento limpio como string

### Módulo: `helpers/limpieza_programacion.py`

#### `limpiar_programacion(archivo_o_df) -> pd.DataFrame`

- **Entrada**: Ruta Excel/CSV o DataFrame
- **Proceso**:
  1. Limpia documentos (elimina .0)
  2. Calcula `nro_estudiantes` = premat + matriculados o usa TOTAL
  3. Procesa horarios (múltiples formatos)
  4. Agrupa clases largas divididas
- **Salida**: DataFrame consolidado y limpio

#### `guardar_programacion_limpia(df: pd.DataFrame, ruta: str) -> str`

- **Entrada**: DataFrame procesado, ruta opcional
- **Proceso**: Aplica limpieza y guarda Excel
- **Salida**: Ruta del archivo guardado

### Módulo: `ui/entrega_devolucion.py`

#### `buscar_profesor(self, event=None)`

- **Entrada**: Texto de búsqueda desde UI
- **Proceso**:
  1. Búsqueda por nombre (contains, case-insensitive)
  2. Búsqueda por documento (partial match)
  3. Combina resultados con OR lógico
- **Salida**: Actualiza TreeView con resultados

#### `entregar_llave_seleccionada(self)`

- **Entrada**: Selección de TreeView
- **Proceso**: Valida no duplicados, prepara info_clase, registra
- **Salida**: Mensaje éxito/error, actualiza llaves prestadas

#### `exportar_registro_entregas(self)`

- **Entrada**: Ninguna (usa historial completo)
- **Proceso**:
  1. Obtiene historial completo
  2. Genera metadatos (fecha, totales, estadísticas)
  3. Crea Excel con 2 hojas
- **Salida**: Archivo Excel con registro + metadatos

#### `exportar_programacion_limpia(self)`

- **Entrada**: Programación en memoria
- **Proceso**: Aplica limpieza, genera metadatos
- **Salida**: Archivo Excel limpio con estadísticas

### Módulo: `ui/programacion.py`

#### `cargar_programacion(self)`

- **Entrada**: Archivo Excel/CSV seleccionado
- **Proceso**:
  1. Validación de columnas requeridas
  2. Llamada a `limpiar_programacion()`
  3. Actualización de App.programacion
- **Salida**: Programación cargada, actualiza UI

#### `mostrar_programacion_en_vista(self)`

- **Entrada**: `App.programacion` (DataFrame)
- **Proceso**: Itera filas, limpia documentos, formatea datos
- **Salida**: TreeView poblado con datos limpios

### Módulo: `ui/informes.py`

#### `generar_informe_llaves_pendientes(self)`

- **Entrada**: Ninguna
- **Proceso**: Llama `obtener_llaves_pendientes()`, procesa
- **Salida**: TreeView con llaves no devueltas

#### `generar_informe_todas_entregas(self)`

- **Entrada**: Ninguna
- **Proceso**: Llama `obtener_historial_completo()`, procesa
- **Salida**: TreeView con historial completo

#### `exportar_informe(self)`

- **Entrada**: Datos actuales del TreeView
- **Proceso**: Convierte TreeView a DataFrame, exporta Excel
- **Salida**: Archivo Excel con informe actual

## Flujos de Datos Críticos

### Cálculo de Estudiantes

```python
# Prioridad 1: Columna TOTAL si existe
if 'TOTAL' in df.columns:
    df['nro_estudiantes'] = df['TOTAL']
else:
    # Prioridad 2: Suma premat + matriculados
    premat = df.get('nro_estudiantes_premat', 0)
    mat = df.get('nro_estudiantes', 0) 
    df['nro_estudiantes'] = premat + mat
```

### Limpieza de Documentos

```python
def limpiar_documento(doc):
    doc_str = str(doc)
    if doc_str.endswith('.0'):
        return doc_str[:-2]  # Elimina .0
    return doc_str
```

### Búsqueda Dual

```python
# Por nombre
mask_nombre = df['profesor'].str.contains(termino, case=False)
# Por documento
mask_documento = df['nroidenti_limpio'].str.contains(termino, case=False)
# Combinación OR
resultados = df[mask_nombre | mask_documento]
```

## Estados del Sistema

### Estados de Llaves

- **Disponible**: En programación, no entregada
- **Entregada**: Registrada como prestada
- **Devuelta**: Registrada como devuelta (histórico)

### Estados de Datos

- **Sin programación**: App.programacion = None
- **Programación cargada**: App.programacion = DataFrame
- **Programación original**: App.programacion_original = DataFrame sin procesar

## Estructura de Datos

### Registro de Llaves (Excel)

```python
columns = [
    'nroidenti',        # str: Documento limpio
    'profesor',         # str: Nombre completo  
    'materia',          # str: Materia
    'aula',            # str: Código aula
    'dia',             # str: Día semana
    'horario',         # str: Horario
    'nro_estudiantes', # int: Total estudiantes
    'fecha_entrega',   # str: YYYY-MM-DD
    'hora_entrega',    # str: HH:MM:SS
    'fecha_devolucion', # str: YYYY-MM-DD o vacío
    'hora_devolucion', # str: HH:MM:SS o vacío
    'estado',          # str: 'Entregada' | 'Devuelta'
    'observaciones'    # str: Notas adicionales
]
```

### Programación Académica

```python
# Columnas requeridas
required = ['nroidenti', 'profesor', 'aula']

# Columnas procesadas
processed_columns = [
    'nroidenti',       # str: Documento limpio
    'profesor',        # str: Nombre
    'materia',         # str: Materia
    'aula',           # str: Aula
    'dia',            # str: Día (mayúscula)
    'horario',        # str: Formato consolidado
    'nro_estudiantes', # float: Total calculado
    'hora_ini',       # time: Hora inicio
    'hora_fin'        # time: Hora fin
]
```

## Manejo de Errores

### Validaciones Principales

1. **Programación**: Verificar columnas requeridas antes de procesar
2. **Entrega**: Validar no duplicados por documento
3. **Archivos**: Manejo de permisos y existencia
4. **Formatos**: Validación de tipos de datos

### Recuperación de Errores

- **Archivos corruptos**: Reinicialización automática
- **Datos faltantes**: Valores por defecto
- **Errores UI**: Mensajes informativos al usuario

## Rendimiento y Optimización

### Estrategias Implementadas

- **Limpieza bajo demanda**: Solo al cargar programación
- **Búsqueda incremental**: Filtrado en memoria
- **Persistencia selectiva**: Solo cambios necesarios
- **UI no bloqueante**: Operaciones rápidas en thread principal

---

**Versión**: 2.0 Modular
**Arquitectura**: Vista-Controlador con Helpers
**Persistencia**: Excel con pandas
**UI**: tkinter con ttk
**Fecha**: Septiembre 2025
