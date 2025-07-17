# Sistema de Control de Llaves

## Descripción
Sistema de gestión para el control de entrega y devolución de llaves de aulas académicas. Permite llevar un registro detallado de quién tiene cada llave y cuándo fue entregada/devuelta.

## Características principales

### 🔑 Gestión de Llaves
- **Entrega de llaves**: Registro de entrega con fecha y hora
- **Devolución de llaves**: Control de devoluciones con timestamp
- **Estado en tiempo real**: Visualización del estado actual de cada llave
- **Historial completo**: Registro de todas las transacciones

### 📊 Gestión de Programación
- **Carga de programación**: Importación desde archivos Excel
- **Limpieza automática**: Consolidación de clases largas divididas en múltiples registros
- **Exportación limpia**: Generación de archivo Excel corregido
- **Búsqueda inteligente**: Localización rápida por documento y fecha
- **Vista completa**: Visualización integral de toda la programación
- **Filtros avanzados**: Filtrado por día, aula y combinaciones
- **Ordenamiento**: Clasificación por cualquier columna
- **Estadísticas**: Información en tiempo real de clases, profesores y aulas

### 🎨 Interfaz Intuitiva
- **Diseño moderno**: Interfaz gráfica amigable con colores institucionales
- **Navegación simple**: Acceso rápido a todas las funciones
- **Información clara**: Estados visuales con emojis y colores
- **Responsive**: Ventanas redimensionables con scrollbars
- **Panel de llaves prestadas**: Vista en tiempo real de todas las llaves entregadas
- **Devolución rápida**: Doble clic para devolver desde el panel de prestadas

## Estructura del Proyecto

```
ControlDeLLaves/
├── llaves_control/
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── assets/
│   │   └── estilo_tkinter.py   # Estilos y temas de la interfaz
│   ├── data/
│   │   └── registros_llaves.xlsx  # Base de datos de registros
│   ├── helpers/
│   │   ├── gestion_excel.py    # Manejo de archivos Excel
│   │   └── limpieza_programacion.py  # Procesamiento de datos
│   └── ui/
│       └── interfaz.py         # Interfaz gráfica principal
├── requirements.txt            # Dependencias del proyecto
└── README.md                  # Este archivo
```

## Instalación

### Prerrequisitos
- Python 3.7 o superior
- Pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd ControlDeLLaves
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python llaves_control/main.py
   ```

## Uso del Sistema

### 1. Cargar Programación Académica

1. **Preparar archivo Excel** con la siguiente estructura mínima:
   - `nroidenti`: Número de identificación del profesor
   - `profesor`: Nombre del profesor
   - `materia` o `MATERIA`: Nombre de la asignatura
   - `aula`: Código del aula
   - `dia`: Día de la semana
   - `horario`: Horario en formato "HH:MM A HH:MM"
   - `nro_estudiantes`: Número de estudiantes

2. **Cargar archivo**:
   - Clic en "Cargar Programación"
   - Seleccionar archivo Excel
   - El sistema automáticamente limpia y consolida los datos

3. **Generar archivo limpio** (opcional):
   - Clic en "Limpiar y Guardar Programación"
   - Elegir ubicación para guardar el archivo corregido

### 2. Buscar Clases de un Profesor

1. **Ingresar documento**: Escribir el número de identificación en el campo
2. **Búsqueda del día**: Clic en "Buscar Clases del Día" para ver solo las clases de hoy
3. **Ver todas**: Clic en "Ver Todas las Clases" para ver toda la programación del profesor

### 3. Gestionar Entrega de Llaves

1. **Seleccionar clase**: Hacer clic en una fila de la tabla
2. **Entregar llave**: Clic en "Entregar Llave"
   - Solo disponible para clases marcadas como "⭕ Disponible"
   - Se registra automáticamente fecha y hora
3. **Confirmar entrega**: El sistema muestra mensaje de confirmación

### 4. Gestionar Devolución de Llaves

1. **Seleccionar clase entregada**: Hacer clic en una fila marcada como "🔑 Entregada"
2. **Devolver llave**: Clic en "Devolver Llave"
3. **Confirmar devolución**: Se actualiza el registro automáticamente

### 5. Consultar Información

- **Llaves Entregadas**: Ver todas las llaves actualmente en poder de profesores
- **Historial**: Consultar el registro completo de todas las transacciones
- **Programación Completa**: Vista integral de toda la programación con filtros avanzados

### 6. Ver y Filtrar Programación Completa

1. **Acceder a la vista**: Clic en "Ver Programación Completa"
2. **Filtrar por día**: Seleccionar día específico del dropdown
3. **Filtrar por aula**: Seleccionar aula específica del dropdown
4. **Combinar filtros**: Usar ambos filtros simultáneamente
5. **Ordenar datos**: Clic en encabezados de columna para ordenar
6. **Exportar vista**: Guardar datos filtrados en Excel
7. **Limpiar filtros**: Restaurar vista completa
8. **Ver estadísticas**: Información en tiempo real de la vista actual

### 7. Monitoreo de Llaves Prestadas

El sistema incluye un **panel en tiempo real** que muestra todas las llaves actualmente prestadas:

1. **Vista automática**: Panel visible en la interfaz principal
2. **Información completa**: Documento, profesor, aula y hora de entrega
3. **Contador dinámico**: Total de llaves prestadas actualizado automáticamente
4. **Devolución rápida**: Doble clic en cualquier fila para devolver la llave
5. **Actualización automática**: Se actualiza después de cada entrega/devolución
6. **Botón de actualizar**: Refrescar manualmente cuando sea necesario

**Características del panel:**
- 🔴 **Texto rojo**: Cuando hay llaves prestadas
- 🟢 **Texto verde**: Cuando no hay llaves prestadas  
- 📊 **Estadísticas**: Contador en tiempo real
- ⚡ **Acceso rápido**: Doble clic para devolver

## Formato del Archivo de Programación

El sistema acepta archivos Excel (.xlsx, .xls) con las siguientes columnas:

### Columnas Requeridas
- `nroidenti`: Número de documento del profesor
- `profesor`: Nombre completo del profesor  
- `materia` o `MATERIA`: Nombre de la asignatura
- `aula`: Código o nombre del aula
- `dia`: Día de la semana (LUNES, MARTES, etc.)
- `horario`: Horario en formato "14:01 A 16:00"

### Columnas Opcionales
- `nro_estudiantes`: Cantidad de estudiantes
- `grupo`: Número de grupo
- `nivel_grupo`: Nivel del grupo
- `semestre`: Semestre académico
- `PROGRAMA`: Programa académico

### Ejemplo de datos:
```
nroidenti | profesor | materia | aula | dia | horario | nro_estudiantes
93387345 | AVELINO LEDESMA | INVESTIGACIÓN I | M405 | MARTES | 14:01 A 16:00 | 20
```

## Características Técnicas

### Consolidación Automática
El sistema detecta y consolida automáticamente:
- **Clases divididas**: Asignaturas largas divididas en múltiples registros
- **Horarios continuos**: Unifica 12:01-13:00 y 13:01-14:00 en 12:01-14:00
- **Duplicados**: Elimina registros redundantes

### Base de Datos
- **Archivo Excel**: `data/registros_llaves.xlsx`
- **Campos**: Documento, profesor, materia, aula, estado, timestamps
- **Backup automático**: Se preservan todos los registros históricos

### Estados de Llaves
- **⭕ Disponible**: Llave disponible para entrega
- **🔑 Entregada**: Llave en poder del profesor
- **Devuelta**: Llave devuelta (en historial)

## Solución de Problemas

### Error al cargar programación
- Verificar que el archivo sea Excel (.xlsx o .xls)
- Comprobar que existan las columnas requeridas
- Revisar formato de datos (fechas, números)

### No aparecen clases
- Verificar número de documento correcto
- Comprobar que el día coincida (sistema usa día actual)
- Revisar que la programación esté cargada

### Error en entrega/devolución
- Verificar que la clase esté seleccionada
- Comprobar estado de la llave
- Revisar permisos de escritura en carpeta data/

### Solución de Problemas Comunes

**Números de documento con .0**
- ✅ **Solucionado**: El sistema ahora limpia automáticamente los números
- Los documentos se muestran sin decimales (ej: 12345678 en lugar de 12345678.0)
- Funciona tanto en carga como en búsquedas y registros

## Contacto y Soporte

Para reportar errores o solicitar nuevas características, contactar al administrador del sistema.

---

**Versión**: 2.0  
**Fecha**: Enero 2025  
**Desarrollado para**: Control de Llaves Académicas