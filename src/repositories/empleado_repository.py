from src.repositories.db_connection import get_connection
from src.domain.empleado import Empleado


class EmpleadoRepository:

    @staticmethod
    def crear(empleado: Empleado):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO empleados
                    (nombre, apellido, dni, email, telefono, usuario, password, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    empleado.nombre,
                    empleado.apellido,
                    empleado.dni,
                    empleado.email,
                    empleado.telefono,
                    empleado.usuario,
                    empleado.password,
                    empleado.rol,
                    1,
                ),
            )

            conn.commit()
            empleado.id_empleado = cursor.lastrowid
            return empleado
        finally:
            conn.close()

    @staticmethod
    def listar():
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_empleado, nombre, apellido, dni, email,
                       telefono, usuario, password, rol, activo
                FROM empleados
                """
            )
            filas = cursor.fetchall()

            empleados = []
            for f in filas:
                empleados.append(
                    Empleado(
                        id_empleado=f[0],
                        nombre=f[1],
                        apellido=f[2],
                        dni=f[3],
                        email=f[4],
                        telefono=f[5],
                        usuario=f[6],
                        password=f[7],
                        rol=f[8],
                        activo=bool(f[9]),
                    )
                )
            return empleados
        finally:
            conn.close()

    @staticmethod
    def buscar_por_dni(dni):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_empleado, nombre, apellido, dni, email,
                       telefono, usuario, password, rol, activo
                FROM empleados
                WHERE dni = ?
                """,
                (dni,),
            )
            f = cursor.fetchone()

            if not f:
                return None

            return Empleado(
                id_empleado=f[0],
                nombre=f[1],
                apellido=f[2],
                dni=f[3],
                email=f[4],
                telefono=f[5],
                usuario=f[6],
                password=f[7],
                rol=f[8],
                activo=bool(f[9]),
            )
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(id_empleado):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_empleado, nombre, apellido, dni, email,
                       telefono, usuario, password, rol, activo
                FROM empleados
                WHERE id_empleado = ?
                """,
                (id_empleado,),
            )
            f = cursor.fetchone()

            if not f:
                return None

            return Empleado(
                id_empleado=f[0],
                nombre=f[1],
                apellido=f[2],
                dni=f[3],
                email=f[4],
                telefono=f[5],
                usuario=f[6],
                password=f[7],
                rol=f[8],
                activo=bool(f[9]),
            )
        finally:
            conn.close()

    @staticmethod
    def actualizar(empleado: Empleado):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE empleados
                   SET nombre   = ?,
                       apellido = ?,
                       dni      = ?,
                       email    = ?,
                       telefono = ?,
                       usuario  = ?,
                       password = ?,
                       rol      = ?,
                       activo   = ?
                 WHERE id_empleado = ?
                """,
                (
                    empleado.nombre,
                    empleado.apellido,
                    empleado.dni,
                    empleado.email,
                    empleado.telefono,
                    empleado.usuario,
                    empleado.password,
                    empleado.rol,
                    1 if empleado.activo else 0,
                    empleado.id_empleado,
                ),
            )

            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def inactivar(id_empleado):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE empleados SET activo = 0 WHERE id_empleado = ?",
                (id_empleado,),
            )
            conn.commit()
        finally:
            conn.close()
