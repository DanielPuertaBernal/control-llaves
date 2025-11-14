# 🔑 Sistema de Control de Llaves

## 📋 Propósito

Sistema para gestionar el préstamo y devolución de llaves de aulas universitarias. Permite llevar un registro completo de entregas, devoluciones y generar reportes del estado actual.

## ⚡ Funcionalidades Principales

- **🔑 Gestión de Llaves**: Registro de entregas y devoluciones
- **📅 Programación Académica**: Carga y procesamiento de horarios de clases
- **📊 Reportes**: Historial completo y llaves pendientes
- **🔍 Búsqueda**: Por documento, nombre o aula
- **📈 Tiempo Real**: Estado actualizado automáticamente

## 🚀 Instalación

### Prerrequisitos
- Python 3.7 o superior

### Instalación con entorno virtual (Recomendado)
```bash
# Clonar el repositorio
git clone https://github.com/DanielPuertaBernal/ControlDeLLaves.git
cd ControlDeLLaves

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

### Instalación sin entorno virtual
```bash
git clone https://github.com/DanielPuertaBernal/ControlDeLLaves.git
cd ControlDeLLaves
pip install -r requirements.txt
python main.py
```

## 📦 Dependencias

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `openpyxl` | ≥3.1.0 | Manipulación de archivos Excel |
| `pandas` | ≥2.0.0 | Procesamiento de datos |
| `tkinter` | - | Interfaz gráfica (incluida con Python) |

## 🎯 Uso Básico

1. **Cargar Programación**: Importar archivo Excel con horarios de clases
2. **Entregar Llaves**: Buscar profesor y registrar entrega
3. **Devolver Llaves**: Marcar devolución desde el historial
4. **Ver Reportes**: Consultar llaves pendientes o historial completo

## 📁 Estructura

```
ControlDeLLaves/
├── main.py           # Archivo principal
├── assets/           # Estilos de interfaz
├── helpers/          # Lógica de negocio
├── ui/              # Interfaz gráfica
└── data/            # Archivos de datos (local)
```
