"""
Script de prueba para verificar conexión a MongoDB Atlas
"""
import os
import urllib.parse
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Obtener credenciales
mongo_uri = os.getenv("MONGO_URI")
password = os.getenv("MONGO_PASSWORD")

print("=" * 60)
print("PRUEBA DE CONEXIÓN A MONGODB ATLAS")
print("=" * 60)

print(f"\n1. URI base (sin contraseña): {mongo_uri}")
print(f"2. Contraseña sin codificar: {password}")

# Codificar la contraseña
escaped_password = urllib.parse.quote_plus(password)
print(f"3. Contraseña codificada: {escaped_password}")

# Construir URI completa
full_uri = mongo_uri.replace('@', f':{escaped_password}@')
print(f"\n4. URI completa: {full_uri}")

print("\n" + "=" * 60)
print("INTENTANDO CONECTAR...")
print("=" * 60)

try:
    client = MongoClient(full_uri, serverSelectionTimeoutMS=5000)
    
    # Probar ping
    client.admin.command('ping')
    print("✅ ¡CONEXIÓN EXITOSA!")
    
    # Mostrar bases de datos disponibles
    print(f"\nBases de datos disponibles:")
    for db_name in client.list_database_names():
        print(f"  - {db_name}")
    
    # Verificar la base de datos objetivo
    db_name = os.getenv("MONGO_DB")
    db = client[db_name]
    print(f"\nBase de datos objetivo: {db_name}")
    print(f"Colecciones en {db_name}:")
    collections = db.list_collection_names()
    if collections:
        for col in collections:
            print(f"  - {col}")
    else:
        print("  (vacía)")
    
    client.close()
    
except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN:")
    print(f"   {type(e).__name__}: {e}")
    print("\n" + "=" * 60)
    print("POSIBLES CAUSAS:")
    print("=" * 60)
    print("1. Usuario o contraseña incorrectos en MongoDB Atlas")
    print("2. IP no agregada a la whitelist en Network Access")
    print("3. Usuario no tiene permisos en la base de datos")
    print("4. El cluster está apagado o suspendido")
    print("\nVerifica en MongoDB Atlas:")
    print("• Database Access: que el usuario 'DanielPB' exista")
    print("• Network Access: que tu IP esté permitida (o usa 0.0.0.0/0)")
    print("• Que el cluster esté activo")
