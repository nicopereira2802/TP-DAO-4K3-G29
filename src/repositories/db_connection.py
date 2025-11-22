import sqlite3
from src.config.settings import DB_PATH

class DatabaseConnection:
    """
    Implementación del Patrón Singleton.
    Garantiza una única instancia de conexión a la BD para todo el sistema.
    """
    _instance = None
    _connection = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def get_connection(self):
        """
        Retorna la conexión activa. Si no existe o se cerró, crea una nueva.
        """
        if self._connection is None:
            try:
                # check_same_thread=False permite usar la conexión en hilos de GUI si fuera necesario
                self._connection = sqlite3.connect(DB_PATH, check_same_thread=False)
                self._connection.execute("PRAGMA foreign_keys = ON;")
            except sqlite3.Error as e:
                print(f"Error crítico conectando a BD: {e}")
                return None
        return self._connection

    def close_connection(self):
        """Cierra la conexión explícitamente si es necesario."""
        if self._connection:
            self._connection.close()
            self._connection = None

# -----------------------------------------------------------------------------
# Función helper global
# -----------------------------------------------------------------------------
def get_connection():
    """
    Función envoltorio para mantener compatibilidad con el resto de los repositorios.
    En lugar de crear una conexión nueva, pide la instancia al Singleton.
    """
    return DatabaseConnection().get_connection()

# -----------------------------------------------------------------------------
# Inicialización de la Base de Datos (Tu lógica original intacta)
# -----------------------------------------------------------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Verificar integridad de la tabla empleados (migración si faltan columnas clave)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empleados';")
    existe_empleados = cursor.fetchone() is not None

    if existe_empleados:
        cursor.execute("PRAGMA table_info(empleados);")
        cols = [fila[1] for fila in cursor.fetchall()]
        columnas_necesarias = {"telefono", "usuario", "password", "rol"}
        if not columnas_necesarias.issubset(set(cols)):
            cursor.execute("DROP TABLE empleados;")

    # 2. Creación de Tablas
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
            estado          TEXT    NOT NULL DEFAULT 'DISPONIBLE',
            km_actual       REAL    NOT NULL DEFAULT 0,
            combustible_actual REAL NOT NULL DEFAULT 0
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
            km_inicial     REAL    NOT NULL DEFAULT 0,
            km_final       REAL,
            combustible_inicial REAL NOT NULL DEFAULT 0,
            combustible_final   REAL,

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

    # 3. Migraciones (Agregar columnas nuevas a tablas viejas si hace falta)
    cursor.execute("PRAGMA table_info(vehiculos);")
    cols_v = [fila[1] for fila in cursor.fetchall()]
    if "km_actual" not in cols_v:
        cursor.execute("ALTER TABLE vehiculos ADD COLUMN km_actual REAL NOT NULL DEFAULT 0;")
    if "combustible_actual" not in cols_v:
        cursor.execute("ALTER TABLE vehiculos ADD COLUMN combustible_actual REAL NOT NULL DEFAULT 0;")

    cursor.execute("PRAGMA table_info(alquileres);")
    cols_a = [fila[1] for fila in cursor.fetchall()]
    if "km_inicial" not in cols_a:
        cursor.execute("ALTER TABLE alquileres ADD COLUMN km_inicial REAL NOT NULL DEFAULT 0;")
    if "km_final" not in cols_a:
        cursor.execute("ALTER TABLE alquileres ADD COLUMN km_final REAL;")
    if "combustible_inicial" not in cols_a:
        cursor.execute("ALTER TABLE alquileres ADD COLUMN combustible_inicial REAL NOT NULL DEFAULT 0;")
    if "combustible_final" not in cols_a:
        cursor.execute("ALTER TABLE alquileres ADD COLUMN combustible_final REAL;")

    conn.commit()
    # NOTA: No cerramos la conexión aquí porque al ser Singleton queremos que siga viva para la app.