# ERROR DE EXPORTACIÓN CORREGIDO

## 🔍 PROBLEMA IDENTIFICADO
```
TclError: bad option "-initialname": must be -confirmoverwrite, -defaultextension, -filetypes, -initialdir, -initialfile, -parent, -title, or -typevariable
```

## ✅ SOLUCIÓN APLICADA

### **Error Original:**
```python
# ❌ INCORRECTO
archivo_salida = filedialog.asksaveasfilename(
    title="Guardar Registro de Entregas",
    defaultextension=".xlsx",
    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
    initialname=f"registro_entregas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"  # ← ERROR
)
```

### **Corrección Aplicada:**
```python
# ✅ CORRECTO
archivo_salida = filedialog.asksaveasfilename(
    title="Guardar Registro de Entregas",
    defaultextension=".xlsx",
    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
    initialfile=f"registro_entregas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"  # ← CORREGIDO
)
```

## 🔧 CAMBIOS REALIZADOS

### **Funciones Corregidas:**
1. ✅ **`exportar_registro_entregas()`** - Línea ~637
2. ✅ **`exportar_programacion_limpia()`** - Línea ~714

### **Cambio Específico:**
- **ANTES**: `initialname=` (opción inválida)
- **AHORA**: `initialfile=` (opción correcta)

## 📋 OPCIONES VÁLIDAS PARA `asksaveasfilename()`

Las opciones permitidas son:
- ✅ `-confirmoverwrite`
- ✅ `-defaultextension` 
- ✅ `-filetypes`
- ✅ `-initialdir`
- ✅ `-initialfile` ← **OPCIÓN CORRECTA**
- ✅ `-parent`
- ✅ `-title`
- ✅ `-typevariable`

## 🎯 FUNCIONALIDAD RESTAURADA

### **Exportación de Registro:**
```python
def exportar_registro_entregas(self):
    archivo_salida = filedialog.asksaveasfilename(
        title="Guardar Registro de Entregas",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=f"registro_entregas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    # ... resto de la función
```

### **Exportación de Programación:**
```python
def exportar_programacion_limpia(self):
    archivo_salida = filedialog.asksaveasfilename(
        title="Guardar Programación Limpia",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=f"programacion_limpia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    # ... resto de la función
```

## 🚀 CÓMO USAR AHORA

### **Paso 1: Ejecutar el Sistema**
```bash
python main.py
```

### **Paso 2: Usar Exportación**
1. Ir a "🔑 Entrega y Devolución"
2. Hacer clic en "📊 Exportar Registro" o "📄 Exportar Programación"
3. El diálogo se abrirá con nombre de archivo automático
4. Seleccionar ubicación y confirmar

### **Paso 3: Verificar Resultados**
- ✅ Diálogo se abre sin errores
- ✅ Nombre de archivo automático aparece
- ✅ Archivo Excel se crea correctamente
- ✅ Metadatos incluidos en archivo

## 🎉 ESTADO ACTUAL

**✅ ERROR COMPLETAMENTE SOLUCIONADO**

### **Beneficios:**
- 🔧 **Sintaxis correcta** de tkinter filedialog
- 📁 **Nombres automáticos** con timestamp
- 📊 **Exportación funcional** de registro y programación
- 🚀 **Sistema estable** sin errores de diálogo

### **Archivos Exportados:**
- `registro_entregas_20250118_103045.xlsx`
- `programacion_limpia_20250118_103045.xlsx`

**🎯 FUNCIONES DE EXPORTACIÓN RESTAURADAS Y FUNCIONANDO**

## 🔍 VERIFICACIÓN

Para verificar que todo funciona:
1. Ejecutar: `python test_exportacion_corregida.py`
2. Revisar que no hay errores de sintaxis
3. Probar exportación en el sistema principal
4. Confirmar que los diálogos se abren correctamente

**✅ SISTEMA LISTO PARA EXPORTAR SIN ERRORES**
