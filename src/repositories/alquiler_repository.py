from src.repositories.db_connection import get_connection
from src.domain.alquiler import Alquiler


class AlquilerRepository:

    @staticmethod
    def crear(alquiler: Alquiler):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO alquileres (
                    id_cliente,
                    id_vehiculo,
                    id_empleado,
                    fecha_inicio,
                    fecha_fin,
                    precio_por_dia,
                    estado,
                    total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alquiler.id_cliente,
                    alquiler.id_vehiculo,
                    alquiler.id_empleado,
                    alquiler.fecha_inicio,
                    alquiler.fecha_fin,
                    alquiler.precio_por_dia,
                    alquiler.estado,
                    alquiler.total
                )
            )

            conn.commit()
            alquiler.id_alquiler = cursor.lastrowid
            return alquiler
        finally:
            conn.close()

    @staticmethod
    def listar():
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM alquileres")
            filas = cursor.fetchall()

            alquileres = []
            for f in filas:
                alquileres.append(
                    Alquiler(
                        id_alquiler=f[0],
                        id_cliente=f[1],
                        id_vehiculo=f[2],
                        id_empleado=f[3],
                        fecha_inicio=f[4],
                        fecha_fin=f[5],
                        precio_por_dia=f[6],
                        estado=f[7],
                        total=f[8]
                    )
                )
            return alquileres
        finally:
            conn.close()

    @staticmethod
    def listar_por_cliente(id_cliente):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM alquileres WHERE id_cliente = ?",
                (id_cliente,)
            )
            filas = cursor.fetchall()

            alquileres = []
            for f in filas:
                alquileres.append(
                    Alquiler(
                        id_alquiler=f[0],
                        id_cliente=f[1],
                        id_vehiculo=f[2],
                        id_empleado=f[3],
                        fecha_inicio=f[4],
                        fecha_fin=f[5],
                        precio_por_dia=f[6],
                        estado=f[7],
                        total=f[8]
                    )
                )
            return alquileres
        finally:
            conn.close()

    @staticmethod
    def listar_por_vehiculo(id_vehiculo):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM alquileres WHERE id_vehiculo = ?",
                (id_vehiculo,)
            )
            filas = cursor.fetchall()

            alquileres = []
            for f in filas:
                alquileres.append(
                    Alquiler(
                        id_alquiler=f[0],
                        id_cliente=f[1],
                        id_vehiculo=f[2],
                        id_empleado=f[3],
                        fecha_inicio=f[4],
                        fecha_fin=f[5],
                        precio_por_dia=f[6],
                        estado=f[7],
                        total=f[8]
                    )
                )
            return alquileres
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(id_alquiler):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM alquileres WHERE id_alquiler = ?",
                (id_alquiler,)
            )
            f = cursor.fetchone()

            if not f:
                return None

            return Alquiler(
                id_alquiler=f[0],
                id_cliente=f[1],
                id_vehiculo=f[2],
                id_empleado=f[3],
                fecha_inicio=f[4],
                fecha_fin=f[5],
                precio_por_dia=f[6],
                estado=f[7],
                total=f[8]
            )
        finally:
            conn.close()

    @staticmethod
    def actualizar(alquiler: Alquiler):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE alquileres
                SET id_cliente = ?,
                    id_vehiculo = ?,
                    id_empleado = ?,
                    fecha_inicio = ?,
                    fecha_fin = ?,
                    precio_por_dia = ?,
                    estado = ?,
                    total = ?
                WHERE id_alquiler = ?
                """,
                (
                    alquiler.id_cliente,
                    alquiler.id_vehiculo,
                    alquiler.id_empleado,
                    alquiler.fecha_inicio,
                    alquiler.fecha_fin,
                    alquiler.precio_por_dia,
                    alquiler.estado,
                    alquiler.total,
                    alquiler.id_alquiler
                )
            )

            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def actualizar_estado_y_total(id_alquiler, nuevo_estado, nuevo_total):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE alquileres
                SET estado = ?, total = ?
                WHERE id_alquiler = ?
                """,
                (nuevo_estado, nuevo_total, id_alquiler)
            )

            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def existe_alquiler_activo_en_rango(id_vehiculo, fecha_desde, fecha_hasta):
        """
        Devuelve True si el vehículo tiene algún alquiler 'ABIERTO'
        o en fechas solapadas con el rango dado.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM alquileres
                WHERE id_vehiculo = ?
                  AND estado = 'ABIERTO'
                  AND NOT (fecha_fin < ? OR fecha_inicio > ?)
                """,
                (id_vehiculo, fecha_desde, fecha_hasta)
            )

            cantidad = cursor.fetchone()[0]
            return cantidad > 0
        finally:
            conn.close()
