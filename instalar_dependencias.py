"""
Script para instalar las dependencias necesarias para la exportación
"""
import subprocess
import sys
import os

def instalar_dependencias():
    print("=== INSTALACIÓN DE DEPENDENCIAS ===")
    print()
    
    dependencias = [
        "pandas",
        "openpyxl",
        "xlsxwriter"
    ]
    
    for dep in dependencias:
        print(f"📦 Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} instalado exitosamente")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando {dep}: {e}")
            print(f"   Intente manualmente: pip install {dep}")
        print()
    
    print("🔍 VERIFICANDO INSTALACIÓN...")
    print()
    
    # Verificar pandas
    try:
        import pandas as pd
        print(f"✅ pandas {pd.__version__} - OK")
    except ImportError:
        print("❌ pandas - NO DISPONIBLE")
    
    # Verificar openpyxl
    try:
        import openpyxl
        print(f"✅ openpyxl {openpyxl.__version__} - OK")
    except ImportError:
        print("❌ openpyxl - NO DISPONIBLE")
    
    # Verificar xlsxwriter
    try:
        import xlsxwriter
        print(f"✅ xlsxwriter {xlsxwriter.__version__} - OK")
    except ImportError:
        print("❌ xlsxwriter - NO DISPONIBLE")
    
    print()
    print("🎉 INSTALACIÓN COMPLETADA")
    print("📋 Ahora puede ejecutar el sistema sin problemas de exportación")

if __name__ == "__main__":
    instalar_dependencias()
