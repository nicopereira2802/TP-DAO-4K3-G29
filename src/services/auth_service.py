from src.repositories.db_connection import get_connection
import sqlite3


class AuthService:
    """
    Servicio de autenticación usando la tabla 'empleados'.

    Valida:
    - que exista un empleado con ese usuario y password
    - que esté activo

    Devuelve (ok: bool, resultado):
    - ok = True  -> resultado = dict con info básica del empleado
    - ok = False -> resultado = mensaje de error para mostrar en la UI
    """

    @staticmethod
    def login(username, password):
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            return False, "Usuario y contraseña son obligatorios."

        try:
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
            conn.close()

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                return False, (
                    "La base de datos está ocupada en este momento.\n"
                    "Cerrá otros programas que la estén usando y volvé a intentar."
                )
            return False, f"Ocurrió un error al acceder a la base de datos: {e}"

        except Exception as e:
            return False, f"Ocurrió un error inesperado al validar el usuario: {e}"

        if fila is None:
            # No encontró usuario+password
            return False, "Usuario o contraseña incorrectos."

        id_empleado, nombre, apellido, rol, activo = fila

        if not activo:
            return False, "El empleado está inactivo. No puede iniciar sesión."

        usuario = {
            "id_empleado": id_empleado,
            "username": username,
            "nombre_completo": f"{nombre} {apellido}",
            "rol": (rol or "").upper(),   # 'ADMIN' o 'EMPLEADO'
        }
        return True, usuario
