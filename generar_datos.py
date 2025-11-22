from datetime import date, timedelta
import sqlite3
from src.repositories.db_connection import get_connection

# ==============================================================================
# CONFIGURACIÓN DE ESCENARIOS DE PRUEBA
# ==============================================================================
# Fechas clave para probar reportes (modificar si se desea otro mes)
MES_PRUEBA_INICIO = "2025-11-01"
MES_PRUEBA_FIN    = "2025-11-30"

# Total esperado para la prueba de reporte económico:
# Generaremos 8 alquileres cerrados en Noviembre.
# Cada uno costará $20,000.
# TOTAL ESPERADO EN REPORTE: $160,000.
PRECIO_TEST = 10000.0
DIAS_TEST = 2  # 2 días de alquiler = 20.000 total por alquiler

# ==============================================================================
# HELPERS
# ==============================================================================
def _tiene_columna(cursor, tabla, nombre_columna):
    cursor.execute(f"PRAGMA table_info({tabla});")
    cols = [row[1] for row in cursor.fetchall()]
    return nombre_columna in cols

def limpiar_datos(cursor):
    print("--- Limpiando base de datos (TRUNCATE simulado) ---")
    tablas = ["incidentes", "mantenimientos", "alquileres", "vehiculos", "clientes", "empleados"]
    for t in tablas:
        try:
            cursor.execute(f"DELETE FROM {t}")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}'") # Reset IDs
        except sqlite3.Error:
            pass
    print("    Base de datos vacía.")

# ==============================================================================
# GENERADORES
# ==============================================================================

def generar_admin(cursor):
    print(f"Generando Admin...")
    cursor.execute("""
        INSERT INTO empleados (nombre, apellido, dni, email, telefono, usuario, password, rol, activo)
        VALUES ('Admin', 'Principal', '11111111', 'admin@rentaya.com', '111111', 'admin', 'admin', 'ADMIN', 1)
    """)

def generar_empleados(cursor):
    print(f"Generando 5 Empleados...")
    datos = [
        ("Juan", "Vendedor", "22222222", "juan@empresa.com", "user1"),
        ("Ana", "Mostrador", "33333333", "ana@empresa.com", "user2"),
        ("Pedro", "Logistica", "44444444", "pedro@empresa.com", "user3"),
        ("Maria", "Gerente", "55555555", "maria@empresa.com", "user4"),
        ("Lucas", "Taller", "66666666", "lucas@empresa.com", "user5"),
    ]
    for nombre, apellido, dni, email, user in datos:
        cursor.execute("""
            INSERT INTO empleados (nombre, apellido, dni, email, telefono, usuario, password, rol, activo)
            VALUES (?, ?, ?, ?, '123456', ?, '1234', 'EMPLEADO', 1)
        """, (nombre, apellido, dni, email, user))

def generar_clientes(cursor, cantidad=100):
    print(f"Generando {cantidad} Clientes (IDs 1 al {cantidad})...")
    # Generamos 100 clientes fijos: Cliente 1, Cliente 2...
    for i in range(1, cantidad + 1):
        nombre = f"Cliente{i}"
        apellido = "Prueba"
        dni = str(10000000 + i) # DNIs del 10000001 al 10000100
        email = f"cliente{i}@test.com"
        telefono = f"351{i:07d}"
        
        cursor.execute("""
            INSERT INTO clientes (nombre, apellido, dni, email, telefono, activo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (nombre, apellido, dni, email, telefono))

def generar_vehiculos(cursor, cantidad=25):
    print(f"Generando {cantidad} Vehículos (IDs 1 al {cantidad})...")
    
    # Patrón fijo: AA001BB, AA002BB...
    # Precios escalonados para variedad
    
    tiene_km = _tiene_columna(cursor, "vehiculos", "km_actual")
    
    tipos = ["auto", "camioneta", "moto"]
    marcas = ["Toyota", "Ford", "Fiat", "Renault", "Honda"]
    
    for i in range(1, cantidad + 1):
        patente = f"AA{i:03d}BB" # Ej: AA001BB
        tipo = tipos[i % 3]      # Alterna tipos
        marca = marcas[i % 5]    # Alterna marcas
        modelo = f"Modelo-{i}"
        anio = 2020 + (i % 5)
        precio = 10000.0 # Precio fijo para facilitar cálculos mentales
        
        if tiene_km:
            cursor.execute("""
                INSERT INTO vehiculos (patente, marca, modelo, anio, tipo, precio_por_dia, activo, estado, km_actual, combustible_actual)
                VALUES (?, ?, ?, ?, ?, ?, 1, 'DISPONIBLE', ?, ?)
            """, (patente, marca, modelo, anio, tipo, precio, 0, 50.0))
        else:
            cursor.execute("""
                INSERT INTO vehiculos (patente, marca, modelo, anio, tipo, precio_por_dia, activo, estado)
                VALUES (?, ?, ?, ?, ?, ?, 1, 'DISPONIBLE')
            """, (patente, marca, modelo, anio, tipo, precio))

def generar_escenario_reportes(cursor):
    print("Generando Escenario de Pruebas (Alquileres)...")
    
    # ------------------------------------------------------------
    # ESCENARIO 1: 8 Alquileres CERRADOS en Noviembre 2025
    # Objetivo: Probar reporte "Alquileres por Mes" y "Resumen Económico"
    # Vehículos ID: 1 al 8
    # Clientes ID: 1 al 8
    # ------------------------------------------------------------
    
    fecha_ini = "2025-11-05"
    fecha_fin = "2025-11-07" # 2 días de diferencia
    precio_dia = 10000.0
    total = precio_dia * 2 # 20.000
    
    tiene_km = _tiene_columna(cursor, "alquileres", "km_inicial")

    for i in range(1, 9):
        # ID Cliente = i, ID Vehiculo = i
        if tiene_km:
            cursor.execute("""
                INSERT INTO alquileres 
                (id_cliente, id_vehiculo, id_empleado, fecha_inicio, fecha_fin, precio_por_dia, estado, total, km_inicial, km_final, combustible_inicial, combustible_final)
                VALUES (?, ?, 1, ?, ?, ?, 'CERRADO', ?, 0, 100, 50, 40)
            """, (i, i, fecha_ini, fecha_fin, precio_dia, total))
        else:
            cursor.execute("""
                INSERT INTO alquileres 
                (id_cliente, id_vehiculo, id_empleado, fecha_inicio, fecha_fin, precio_por_dia, estado, total)
                VALUES (?, ?, 1, ?, ?, ?, 'CERRADO', ?)
            """, (i, i, fecha_ini, fecha_fin, precio_dia, total))
            
    print(f"  -> Generados 8 alquileres cerrados en Nov 2025 (Total esperado: ${total * 8})")

    # ------------------------------------------------------------
    # ESCENARIO 2: 1 Alquiler ABIERTO (Vehículo 25)
    # Objetivo: Probar Dashboard 'Alquileres abiertos' y bloqueo de vehículo
    # ------------------------------------------------------------
    hoy = date.today().isoformat()
    manana = (date.today() + timedelta(days=1)).isoformat()
    
    vid = 25
    
    if tiene_km:
        cursor.execute("""
            INSERT INTO alquileres (id_cliente, id_vehiculo, id_empleado, fecha_inicio, fecha_fin, precio_por_dia, estado, total, km_inicial, combustible_inicial)
            VALUES (100, ?, 1, ?, ?, 15000, 'ABIERTO', 0, 1000, 50)
        """, (vid, hoy, manana))
    else:
        cursor.execute("""
            INSERT INTO alquileres (id_cliente, id_vehiculo, id_empleado, fecha_inicio, fecha_fin, precio_por_dia, estado, total)
            VALUES (100, ?, 1, ?, ?, 15000, 'ABIERTO', 0)
        """, (vid, hoy, manana))
        
    # Actualizar estado del vehículo a ALQUILADO
    cursor.execute("UPDATE vehiculos SET estado = 'ALQUILADO' WHERE id_vehiculo = ?", (vid,))
    print(f"  -> Generado 1 alquiler ABIERTO hoy (Vehículo ID {vid})")

    # ------------------------------------------------------------
    # ESCENARIO 3: Mantenimiento (Vehículo 24)
    # Objetivo: Probar Dashboard 'En mantenimiento' y bloqueo
    # ------------------------------------------------------------
    vid_mant = 24
    cursor.execute("""
        INSERT INTO mantenimientos (id_vehiculo, fecha_inicio, fecha_fin, descripcion)
        VALUES (?, ?, ?, 'Revisión Técnica Programada')
    """, (vid_mant, hoy, manana))
    
    # Actualizar estado del vehículo
    cursor.execute("UPDATE vehiculos SET estado = 'MANTENIMIENTO' WHERE id_vehiculo = ?", (vid_mant,))
    print(f"  -> Generado 1 mantenimiento activo hoy (Vehículo ID {vid_mant})")

    # ------------------------------------------------------------
    # ESCENARIO 4: Incidentes
    # Objetivo: Probar reporte de incidentes
    # ------------------------------------------------------------
    # Asignamos incidente al alquiler cerrado ID 1
    cursor.execute("""
        INSERT INTO incidentes (id_alquiler, tipo, descripcion, monto, estado)
        VALUES (1, 'DAÑO', 'Rayón en paragolpes', 5000, 'PENDIENTE')
    """)
    print("  -> Generado 1 incidente PENDIENTE ($5000) para Alquiler ID 1")


# ==============================================================================
# EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    conn = get_connection()
    try:
        limpiar_datos(conn.cursor())
        
        generar_admin(conn.cursor())
        generar_empleados(conn.cursor())
        generar_clientes(conn.cursor()) # 100
        generar_vehiculos(conn.cursor()) # 25
        
        generar_escenario_reportes(conn.cursor())
        
        conn.commit()
        print("\n=========================================")
        print(" DATOS FIJOS GENERADOS EXITOSAMENTE")
        print("=========================================")
        print("Credenciales Admin: admin / admin")
        print(f"Vehículos creados: 25")
        print(f"Clientes creados: 100")
        print(f"Alquileres de prueba en Noviembre 2025: 8")
        print("=========================================")
    finally:
        # Al ser un script externo, no importa cerrar la conexión del Singleton
        # o dejar que el proceso muera.
        pass