# 🔑 Sistema de Control de Llaves

## 📋 Propósito

Sistema profesional para gestionar el préstamo y devolución de llaves de aulas universitarias con autenticación basada en roles. Permite llevar un registro completo de entregas, devoluciones y generar reportes del estado actual.

## ⚡ Funcionalidades Principales

- **🔐 Autenticación Segura**: Sistema de login con contraseñas cifradas (bcrypt)
- **👥 Control de Acceso (RBAC)**: Dos roles con permisos diferenciados
  - **Administrador**: Gestión de programación completa y creación de usuarios auxiliares
  - **Auxiliar**: Entrega/devolución de llaves, NFC, consultas y reportes
- **🔑 Gestión de Llaves**: Registro de entregas y devoluciones con NFC
- **📅 Programación Académica**: Carga y procesamiento de horarios de clases
- **📊 Reportes**: Historial completo y llaves pendientes
- **🔍 Búsqueda**: Por documento, nombre o aula
- **📈 Tiempo Real**: Estado actualizado automáticamente
- **🗄️ MongoDB**: Persistencia profesional NoSQL

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- MongoDB 4.4 o superior (local o remoto)

### 1. Configuración del entorno

```bash
# Clonar el repositorio
git clone https://github.com/DanielPuertaBernal/ControlDeLLaves.git
cd ControlDeLLaves

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar MongoDB

Cree un archivo `.env` en la raíz del proyecto:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=control_llaves
```

### 3. Crear primer usuario administrador

**IMPORTANTE**: Antes de ejecutar la aplicación por primera vez, debe crear el usuario administrador:

```bash
python crear_admin.py
```

Siga las instrucciones e ingrese:
- Usuario único
- Nombre completo
- Email
- Teléfono/contacto
- Contraseña (mínimo 6 caracteres)

**Guarde estas credenciales en un lugar seguro.**

### 4. Ejecutar aplicación

```bash
python main.py
```

## 👥 Gestión de Usuarios

### Roles del Sistema

#### 🔴 Administrador de Programación
- Cargar/actualizar programación académica completa
- Crear y gestionar usuarios auxiliares
- Desactivar usuarios
- **NO** tiene acceso a préstamo de llaves ni NFC

#### 🔵 Auxiliar de Programación
- Consultar programación del día actual
- Entregar y recibir llaves
- Usar sistema NFC
- Consultar historial y generar reportes
- **NO** puede gestionar otros usuarios

### Crear Auxiliares

1. Inicie sesión como **Administrador**
2. Seleccione **"👥 Gestión de Usuarios"** en el menú
3. Click en **"➕ Nuevo Auxiliar"**
4. Complete el formulario:
   - Usuario (único)
   - Nombre completo
   - Email (único)
   - Teléfono/Contacto
   - Contraseña (mínimo 6 caracteres)
5. Click en **"✅ Crear Usuario"**

Los auxiliares pueden iniciar sesión inmediatamente con sus credenciales.

## 📦 Dependencias

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `pymongo` | ≥4.7.0 | Conexión y operaciones con MongoDB |
| `bcrypt` | ≥4.0.0 | Cifrado de contraseñas (hashing seguro) |
| `pandas` | ≥2.0.0 | Procesamiento de datos y programación |
| `openpyxl` | ≥3.1.0 | Lectura de archivos Excel |
| `python-dotenv` | ≥1.0.0 | Gestión de variables de entorno |
| `pyserial` | ≥3.5 | Comunicación con lectores NFC |
| `tkinter` | - | Interfaz gráfica (incluida con Python) |

## 🎯 Uso Básico

### Como Administrador
1. **Cargar Programación**: Archivo Excel con horarios completos
2. **Gestionar Usuarios**: Crear auxiliares desde menú "Gestión de Usuarios"

### Como Auxiliar
1. **Consultar Programación del Día**: Ver clases programadas para hoy
2. **Entregar Llaves**: Buscar docente y registrar entrega (con/sin NFC)
3. **Devolver Llaves**: Marcar devolución desde historial
4. **Generar Informes**: Reportes del día y estadísticas

## 🏗️ Arquitectura

El sistema sigue **Clean Architecture** con 5 capas:

```
ControlDeLLaves/
├── domain/                    # Entidades de negocio
│   ├── usuario.py            # Usuario, RolUsuario
│   ├── llave_model.py        # Llave
│   └── docente_model.py      # Docente
├── application/              # Lógica de aplicación
│   ├── auth/                 # Sistema de autenticación
│   │   ├── auth_manager.py   # Hashing bcrypt
│   │   ├── session_manager.py # Gestión de sesiones
│   │   └── decorators.py     # RBAC decorators
│   ├── services/             # Servicios de negocio
│   └── service_factory.py    # Dependency injection
├── infrastructure/           # Persistencia y servicios externos
│   ├── repositories/         # MongoDB repositories
│   └── services/            # NFC, MongoDB client
├── presentation/            # Interfaz de usuario
│   ├── views/               # Vistas tkinter
│   ├── nfc_presenter.py     # Presenter NFC
│   └── assets/              # Estilos
├── controllers/             # Controladores MVC
├── main.py                  # Punto de entrada
├── crear_admin.py           # Script inicial admin
└── requirements.txt         # Dependencias
```

## 🔒 Seguridad

- ✅ Contraseñas cifradas con **bcrypt** (12 salt rounds)
- ✅ Control de acceso basado en roles (**RBAC**)
- ✅ Sesiones con expiración automática (8 horas)
- ✅ Validación de permisos en capa de servicio
- ✅ Índices únicos en MongoDB (usuario, email)
- ✅ Soft delete de usuarios (no eliminación física)

## 🛠️ Mantenimiento

### Respaldo de Base de Datos

```bash
# Exportar colección de usuarios
mongodump --db=control_llaves --collection=usuarios --out=backup/

# Restaurar
mongorestore --db=control_llaves backup/control_llaves/
```

### Cambiar Contraseña de Admin

Use el script `crear_admin.py` para crear un nuevo administrador si perdió acceso.
