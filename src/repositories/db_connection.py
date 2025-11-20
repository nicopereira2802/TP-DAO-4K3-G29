import sqlite3
from src.config.settings import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='empleados';"
    )
    existe_empleados = cursor.fetchone() is not None

    if existe_empleados:
        cursor.execute("PRAGMA table_info(empleados);")
        cols = [fila[1] for fila in cursor.fetchall()]

        columnas_necesarias = {"telefono", "usuario", "password", "rol"}
        if not columnas_necesarias.issubset(set(cols)):
            cursor.execute("DROP TABLE empleados;")

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT    NOT NULL,
            apellido       TEXT    NOT NULL,
            dni            TEXT    NOT NULL UNIQUE,
            email          TEXT    NOT NULL UNIQUE,
            telefono       TEXT,
            activo         INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS empleados (
            id_empleado    INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT    NOT NULL,
            apellido       TEXT    NOT NULL,
            dni            TEXT    NOT NULL UNIQUE,
            email          TEXT    NOT NULL UNIQUE,
            telefono       TEXT,
            usuario        TEXT    NOT NULL UNIQUE,
            password       TEXT    NOT NULL,
            rol            TEXT    NOT NULL,
            activo         INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS vehiculos (
            id_vehiculo     INTEGER PRIMARY KEY AUTOINCREMENT,
            patente         TEXT    NOT NULL UNIQUE,
            marca           TEXT    NOT NULL,
            modelo          TEXT    NOT NULL,
            anio            INTEGER NOT NULL,
            tipo            TEXT    NOT NULL,
            precio_por_dia  REAL    NOT NULL,
            activo          INTEGER NOT NULL DEFAULT 1,
            estado          TEXT    NOT NULL DEFAULT 'DISPONIBLE'
        );

        CREATE TABLE IF NOT EXISTS alquileres (
            id_alquiler    INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente     INTEGER NOT NULL,
            id_vehiculo    INTEGER NOT NULL,
            id_empleado    INTEGER NOT NULL,
            fecha_inicio   TEXT    NOT NULL,
            fecha_fin      TEXT    NOT NULL,
            precio_por_dia REAL    NOT NULL,
            estado         TEXT    NOT NULL,
            total          REAL    NOT NULL DEFAULT 0,

            FOREIGN KEY (id_cliente)  REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_vehiculo) REFERENCES vehiculos(id_vehiculo),
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
        );

        CREATE TABLE IF NOT EXISTS mantenimientos (
            id_mantenimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_vehiculo      INTEGER NOT NULL,
            fecha_inicio     TEXT    NOT NULL,
            fecha_fin        TEXT    NOT NULL,
            descripcion      TEXT    NOT NULL,

            FOREIGN KEY (id_vehiculo) REFERENCES vehiculos(id_vehiculo)
        );

        CREATE TABLE IF NOT EXISTS incidentes (
            id_incidente  INTEGER PRIMARY KEY AUTOINCREMENT,
            id_alquiler   INTEGER NOT NULL,
            tipo          TEXT    NOT NULL,
            descripcion   TEXT    NOT NULL,
            monto         REAL    NOT NULL,
            estado        TEXT    NOT NULL,

            FOREIGN KEY (id_alquiler) REFERENCES alquileres(id_alquiler)
        );

        CREATE INDEX IF NOT EXISTS idx_alquileres_fecha_inicio
            ON alquileres (fecha_inicio);

        CREATE INDEX IF NOT EXISTS idx_mantenimientos_fecha_inicio
            ON mantenimientos (fecha_inicio);

        CREATE INDEX IF NOT EXISTS idx_incidentes_id_alquiler
            ON incidentes (id_alquiler);
        """
    )

    conn.commit()
    conn.close()
