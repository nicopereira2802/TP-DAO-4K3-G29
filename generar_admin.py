import sqlite3
from src.repositories.db_connection import DB_PATH, get_connection

def generar_admin():
    print(">>> Generando ADMIN...")

    conn = get_connection()
    cursor = conn.cursor()

    # Verificar si ya existe un admin
    cursor.execute("SELECT COUNT(*) FROM empleados WHERE usuario = 'admin'")
    existe = cursor.fetchone()[0]

    if existe > 0:
        print("❌ Ya existe un usuario ADMIN en la base de datos.")
        conn.close()
        return

    # Datos del admin
    nombre = "Sistema"
    apellido = "Administrador"
    dni = "99999999"
    email = "admin@sistema.com"
    telefono = "3510000000"
    usuario = "admin"
    password = "admin123"
    rol = "ADMIN"
    activo = 1

    try:
        cursor.execute(
            """
            INSERT INTO empleados
            (nombre, apellido, dni, email, telefono, usuario, password, rol, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (nombre, apellido, dni, email, telefono, usuario, password, rol, activo)
        )
        conn.commit()
        print("✅ ADMIN generado correctamente.")
        print("Usuario: admin")
        print("Contraseña: admin123")

    except sqlite3.IntegrityError as e:
        print("❌ Error de integridad:", e)

    except Exception as e:
        print("❌ Error inesperado:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    print(f"Usando base de datos: {DB_PATH}")
    generar_admin()
