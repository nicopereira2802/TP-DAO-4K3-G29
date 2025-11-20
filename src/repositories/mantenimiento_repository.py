from src.repositories.db_connection import get_connection
from src.domain.mantenimiento import Mantenimiento


class MantenimientoRepository:

    @staticmethod
    def crear(mantenimiento: Mantenimiento):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO mantenimientos (id_vehiculo, fecha_inicio, fecha_fin, descripcion)
                VALUES (?, ?, ?, ?)
                """,
                (
                    mantenimiento.id_vehiculo,
                    mantenimiento.fecha_inicio,
                    mantenimiento.fecha_fin,
                    mantenimiento.descripcion
                )
            )
            conn.commit()
            mantenimiento.id_mantenimiento = cursor.lastrowid
            return mantenimiento
        finally:
            conn.close()

    @staticmethod
    def listar():
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mantenimientos")
            filas = cursor.fetchall()

            mantenimientos = []
            for f in filas:
                mantenimientos.append(
                    Mantenimiento(
                        id_mantenimiento=f[0],
                        id_vehiculo=f[1],
                        fecha_inicio=f[2],
                        fecha_fin=f[3],
                        descripcion=f[4]
                    )
                )
            return mantenimientos
        finally:
            conn.close()

    @staticmethod
    def listar_por_vehiculo(id_vehiculo):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM mantenimientos WHERE id_vehiculo = ?",
                (id_vehiculo,)
            )
            filas = cursor.fetchall()

            mantenimientos = []
            for f in filas:
                mantenimientos.append(
                    Mantenimiento(
                        id_mantenimiento=f[0],
                        id_vehiculo=f[1],
                        fecha_inicio=f[2],
                        fecha_fin=f[3],
                        descripcion=f[4]
                    )
                )
            return mantenimientos
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(id_mantenimiento):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM mantenimientos WHERE id_mantenimiento = ?",
                (id_mantenimiento,)
            )
            f = cursor.fetchone()

            if not f:
                return None

            return Mantenimiento(
                id_mantenimiento=f[0],
                id_vehiculo=f[1],
                fecha_inicio=f[2],
                fecha_fin=f[3],
                descripcion=f[4]
            )
        finally:
            conn.close()

    @staticmethod
    def actualizar(mantenimiento: Mantenimiento):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE mantenimientos
                SET id_vehiculo = ?, fecha_inicio = ?, fecha_fin = ?, descripcion = ?
                WHERE id_mantenimiento = ?
                """,
                (
                    mantenimiento.id_vehiculo,
                    mantenimiento.fecha_inicio,
                    mantenimiento.fecha_fin,
                    mantenimiento.descripcion,
                    mantenimiento.id_mantenimiento
                )
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def eliminar(id_mantenimiento):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM mantenimientos WHERE id_mantenimiento = ?",
                (id_mantenimiento,)
            )
            conn.commit()
        finally:
            conn.close()
