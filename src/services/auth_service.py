from src.repositories.db_connection import get_connection
import sqlite3

class AuthService:
    """
    Servicio de autenticación.
    """

    @staticmethod
    def login(username, password):
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            return False, "Usuario y contraseña son obligatorios."

        try:
            # Obtenemos la conexión Singleton (NO la cerramos al final)
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id_empleado, nombre, apellido, rol, activo
                  FROM empleados
                 WHERE usuario = ?
                   AND password = ?
                """,
                (username, password),
            )
            fila = cursor.fetchone()
            # Eliminamos conn.close()

        except sqlite3.OperationalError as e:
            return False, f"Error de BD: {e}"
        except Exception as e:
            return False, f"Error inesperado: {e}"

        if fila is None:
            return False, "Usuario o contraseña incorrectos."

        id_empleado, nombre, apellido, rol, activo = fila

        if not activo:
            return False, "El empleado está inactivo."

        usuario = {
            "id_empleado": id_empleado,
            "username": username,
            "nombre_completo": f"{nombre} {apellido}",
            "rol": (rol or "").upper(),
        }
        return True, usuario