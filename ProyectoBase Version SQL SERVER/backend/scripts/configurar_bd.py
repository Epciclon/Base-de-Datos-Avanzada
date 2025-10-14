import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyodbc
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

def crear_base_datos():
    """Crear la base de datos BancoPichincha si no existe"""
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "sync")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "BancoPichincha")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    if not DB_PASSWORD:
        print("❌ Error: Debes configurar DB_PASSWORD en el archivo .env")
        print("Ejemplo: DB_PASSWORD=tu_password_de_sql_server")
        return False
    
    try:
        # Conectar al servidor (sin especificar base de datos)
        connection_string = f"DRIVER={{{DB_DRIVER}}};SERVER={DB_HOST};UID={DB_USER};PWD={DB_PASSWORD};TrustServerCertificate=yes"
        
        print(f"🔌 Conectando a SQL Server en {DB_HOST}...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{DB_NAME}'")
        if cursor.fetchone():
            print(f"✅ La base de datos '{DB_NAME}' ya existe")
        else:
            # Crear la base de datos
            print(f"🏗️ Creando base de datos '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE [{DB_NAME}]")
            conn.commit()
            print(f"✅ Base de datos '{DB_NAME}' creada exitosamente")
        
        cursor.close()
        conn.close()
        
        # Ahora ejecutar el script SQL para crear las tablas
        print(f"📋 Ejecutando script de creación de tablas...")
        ejecutar_script_sql()
        
        return True
        
    except pyodbc.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def ejecutar_script_sql():
    """Ejecutar el script pichincha2.sql para crear las tablas"""
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "sync")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "BancoPichincha")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    try:
        # Conectar a la base de datos específica
        connection_string = f"DRIVER={{{DB_DRIVER}}};SERVER={DB_HOST};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD};TrustServerCertificate=yes"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Leer el archivo SQL
        sql_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pichincha2.sql")
        
        if not os.path.exists(sql_file_path):
            print(f"❌ No se encontró el archivo SQL en: {sql_file_path}")
            return False
        
        print(f"📖 Leyendo script SQL desde: {sql_file_path}")
        
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir el contenido por comandos (separados por 'go')
        commands = sql_content.split('go')
        
        print(f"🔧 Ejecutando {len(commands)} comandos SQL...")
        
        for i, command in enumerate(commands):
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    conn.commit()
                    print(f"✅ Comando {i+1}/{len(commands)} ejecutado")
                except pyodbc.Error as e:
                    # Ignorar errores de objetos que ya existen
                    if "already exists" in str(e) or "Ya existe" in str(e):
                        print(f"⚠️ Comando {i+1}: Objeto ya existe (ignorado)")
                    else:
                        print(f"❌ Error en comando {i+1}: {e}")
        
        cursor.close()
        conn.close()
        
        print("✅ Script SQL ejecutado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando script SQL: {e}")
        return False

def verificar_conexion():
    """Verificar que la conexión a la base de datos funciona"""
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "sync")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "BancoPichincha")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    try:
        connection_string = f"DRIVER={{{DB_DRIVER}}};SERVER={DB_HOST};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD};TrustServerCertificate=yes"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Verificar algunas tablas principales
        tablas_principales = ['PERSONA', 'CLIENTE', 'CUENTA', 'CAJERO', 'TARJETA']
        
        print("🔍 Verificando tablas principales...")
        for tabla in tablas_principales:
            cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{tabla}'")
            if cursor.fetchone()[0] > 0:
                print(f"✅ Tabla {tabla}: OK")
            else:
                print(f"❌ Tabla {tabla}: NO ENCONTRADA")
        
        cursor.close()
        conn.close()
        
        print("✅ Verificación de conexión completada")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando conexión: {e}")
        return False

def main():
    """Función principal"""
    print("🏦 === CONFIGURACIÓN BASE DE DATOS BANCO PICHINCHA ===")
    print()
    
    # Verificar variables de entorno
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPor favor configura estas variables en el archivo .env")
        return
    
    print("📋 Configuración actual:")
    print(f"   - Host: {os.getenv('DB_HOST')}")
    print(f"   - Usuario: {os.getenv('DB_USER')}")
    print(f"   - Base de datos: {os.getenv('DB_NAME')}")
    print(f"   - Driver: {os.getenv('DB_DRIVER')}")
    print()
    
    # Crear base de datos y tablas
    if crear_base_datos():
        print()
        # Verificar conexión
        verificar_conexion()
        print()
        print("🎉 ¡Configuración completada!")
        print("Backend listo para usar:")
        print("   python run.py  # Para iniciar el servidor")
    else:
        print("❌ Configuración fallida")

if __name__ == "__main__":
    main()
