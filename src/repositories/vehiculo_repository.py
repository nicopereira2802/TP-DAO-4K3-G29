from src.repositories.db_connection import get_connection
from src.domain.vehiculo import Vehiculo

class VehiculoRepository:

    @staticmethod
    def crear(vehiculo: Vehiculo):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO vehiculos (
                patente, marca, modelo, anio, tipo, precio_por_dia,
                activo, estado, km_actual, combustible_actual
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                vehiculo.patente, vehiculo.marca, vehiculo.modelo, vehiculo.anio,
                vehiculo.tipo, vehiculo.precio_por_dia, 1 if vehiculo.activo else 0,
                vehiculo.estado or "DISPONIBLE", vehiculo.km_actual, vehiculo.combustible_actual,
            ),
        )
        conn.commit()
        vehiculo.id_vehiculo = cursor.lastrowid
        return vehiculo

    @staticmethod
    def listar():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehiculos WHERE activo = 1")
        filas = cursor.fetchall()

        vehiculos = []
        for f in filas:
            # Mapeo seguro de índices
            estado = f[8] if len(f) > 8 else "DISPONIBLE"
            km_actual = f[9] if len(f) > 9 else 0
            comb_actual = f[10] if len(f) > 10 else 0.0

            vehiculos.append(Vehiculo(
                id_vehiculo=f[0], patente=f[1], marca=f[2], modelo=f[3], anio=f[4],
                tipo=f[5], precio_por_dia=f[6], activo=bool(f[7]),
                estado=estado, km_actual=km_actual, combustible_actual=comb_actual
            ))
        return vehiculos

    @staticmethod
    def buscar_por_patente(patente):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehiculos WHERE patente = ?", (patente,))
        f = cursor.fetchone()

        if not f: return None

        estado = f[8] if len(f) > 8 else "DISPONIBLE"
        km_actual = f[9] if len(f) > 9 else 0
        comb_actual = f[10] if len(f) > 10 else 0.0

        return Vehiculo(
            id_vehiculo=f[0], patente=f[1], marca=f[2], modelo=f[3], anio=f[4],
            tipo=f[5], precio_por_dia=f[6], activo=bool(f[7]),
            estado=estado, km_actual=km_actual, combustible_actual=comb_actual
        )

    @staticmethod
    def obtener_por_id(id_vehiculo):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehiculos WHERE id_vehiculo = ?", (id_vehiculo,))
        f = cursor.fetchone()

        if not f: return None

        estado = f[8] if len(f) > 8 else "DISPONIBLE"
        km_actual = f[9] if len(f) > 9 else 0
        comb_actual = f[10] if len(f) > 10 else 0.0

        return Vehiculo(
            id_vehiculo=f[0], patente=f[1], marca=f[2], modelo=f[3], anio=f[4],
            tipo=f[5], precio_por_dia=f[6], activo=bool(f[7]),
            estado=estado, km_actual=km_actual, combustible_actual=comb_actual
        )

    @staticmethod
    def actualizar(vehiculo: Vehiculo):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE vehiculos
            SET patente=?, marca=?, modelo=?, anio=?, tipo=?, precio_por_dia=?,
                estado=?, km_actual=?, combustible_actual=?
            WHERE id_vehiculo=?
            """,
            (
                vehiculo.patente, vehiculo.marca, vehiculo.modelo, vehiculo.anio,
                vehiculo.tipo, vehiculo.precio_por_dia, vehiculo.estado,
                vehiculo.km_actual, vehiculo.combustible_actual, vehiculo.id_vehiculo
            ),
        )
        conn.commit()

    @staticmethod
    def inactivar(id_vehiculo):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE vehiculos SET activo = 0 WHERE id_vehiculo = ?", (id_vehiculo,))
        conn.commit()