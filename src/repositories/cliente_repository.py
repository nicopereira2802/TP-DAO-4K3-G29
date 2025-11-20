from src.repositories.db_connection import get_connection
from src.domain.cliente import Cliente


class ClienteRepository:

    @staticmethod
    def crear(cliente: Cliente):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO clientes (nombre, apellido, dni, email, telefono, activo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cliente.nombre, cliente.apellido, cliente.dni,
                 cliente.email, cliente.telefono, 1)
            )

            conn.commit()
            cliente.id = cursor.lastrowid
            return cliente
        finally:
            conn.close()

    @staticmethod
    def listar():
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM clientes WHERE activo = 1")
            filas = cursor.fetchall()

            clientes = []
            for f in filas:
                clientes.append(
                    Cliente(
                        id=f[0],
                        nombre=f[1],
                        apellido=f[2],
                        dni=f[3],
                        email=f[4],
                        telefono=f[5],
                        activo=bool(f[6]),
                    )
                )
            return clientes
        finally:
            conn.close()

    @staticmethod
    def buscar_por_dni(dni):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM clientes WHERE dni = ?", (dni,))
            f = cursor.fetchone()

            if not f:
                return None

            return Cliente(
                id=f[0],
                nombre=f[1],
                apellido=f[2],
                dni=f[3],
                email=f[4],
                telefono=f[5],
                activo=bool(f[6]),
            )
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(id_cliente):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,))
            f = cursor.fetchone()

            if not f:
                return None

            return Cliente(
                id=f[0],
                nombre=f[1],
                apellido=f[2],
                dni=f[3],
                email=f[4],
                telefono=f[5],
                activo=bool(f[6]),
            )
        finally:
            conn.close()

    @staticmethod
    def actualizar(cliente: Cliente):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE clientes
                SET nombre=?, apellido=?, dni=?, email=?, telefono=?
                WHERE id_cliente=?
                """,
                (cliente.nombre, cliente.apellido, cliente.dni,
                 cliente.email, cliente.telefono, cliente.id)
            )

            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def inactivar(id_cliente):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE clientes SET activo = 0 WHERE id_cliente = ?",
                (id_cliente,)
            )

            conn.commit()
        finally:
            conn.close()
