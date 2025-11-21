import random
from datetime import date, timedelta, datetime

from src.repositories.db_connection import get_connection


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _tiene_columna(cursor, tabla, nombre_columna):
    cursor.execute(f"PRAGMA table_info({tabla});")
    cols = [row[1] for row in cursor.fetchall()]
    return nombre_columna in cols


# -------------------------------------------------
# Empleados / Admin
# -------------------------------------------------
def generar_admin():
    conn = get_connection()
    cur = conn.cursor()

    print("Creando admin...")

    # Intento crear solo si no existe
    cur.execute("SELECT COUNT(*) FROM empleados WHERE usuario = 'admin';")
    ya_existe = cur.fetchone()[0] > 0
    if ya_existe:
        print("  - Admin ya existe, se omite.")
        conn.close()
        return

    cur.execute(
        """
        INSERT INTO empleados
            (nombre, apellido, dni, email, telefono, usuario, password, rol, activo)
        VALUES
            ('Admin', 'Principal', '99999999',
             'admin@rentaya.com', '3510000000',
             'admin', 'admin', 'ADMIN', 1)
        """
    )

    conn.commit()
    conn.close()
    print("  - Admin creado (usuario=admin, pass=admin).")


def generar_empleados(cant=5):
    conn = get_connection()
    cur = conn.cursor()

    print(f"Generando {cant} empleados...")

    nombres = ["Luis", "Carlos", "Pedro", "Néstor", "Diego", "Tomás"]
    apellidos = ["Paredes", "Martín", "Acosta", "Luna", "Oliva", "Gutiérrez"]

    for _ in range(cant):
        n = random.choice(nombres)
        a = random.choice(apellidos)
        dni = random.randint(20000000, 35000000)
        email = f"{n.lower()}.{a.lower()}.{dni}@empresa.com"
        tel = f"351{random.randint(5000000, 9999999)}"
        usuario = f"{n.lower()}{dni}"
        password = "empleado"  # simple para pruebas

        cur.execute(
            """
            INSERT INTO empleados
                (nombre, apellido, dni, email, telefono, usuario, password, rol, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'EMPLEADO', 1)
            """,
            (n, a, str(dni), email, tel, usuario, password),
        )

    conn.commit()
    conn.close()
    print("  - Empleados generados.")


# -------------------------------------------------
# Clientes
# -------------------------------------------------
def generar_clientes(cant=30):
    conn = get_connection()
    cur = conn.cursor()

    print(f"Generando {cant} clientes...")

    nombres = ["Juan", "Pedro", "Luis", "Nicolás", "Matías", "Hernán", "Mario", "Diego", "Andrés", "Federico"]
    apellidos = ["Gómez", "Pereira", "López", "Martínez", "Ferreyra", "Castro", "Ramos", "Suárez", "Ojeda", "Álvarez"]

    usados_dni = set()

    for _ in range(cant):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)

        while True:
            dni = str(random.randint(20000000, 50000000))
            if dni not in usados_dni:
                usados_dni.add(dni)
                break

        email = f"{nombre.lower()}.{apellido.lower()}.{dni}@gmail.com"
        telefono = str(random.randint(1000000, 9000000))

        cur.execute(
            """
            INSERT INTO clientes (nombre, apellido, dni, email, telefono, activo)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (nombre, apellido, dni, email, telefono),
        )

    conn.commit()
    conn.close()
    print("  - Clientes generados.")


# -------------------------------------------------
# Vehículos (soporta o no km/combustible según la BD)
# -------------------------------------------------
def generar_vehiculos(cant=20):
    conn = get_connection()
    cur = conn.cursor()

    print(f"Generando {cant} vehículos...")

    marcas = ["Ford", "Chevrolet", "Volkswagen", "Peugeot", "Toyota", "Fiat"]
    modelos = ["Fiesta", "Corsa", "Gol", "208", "Onix", "Clio", "Focus"]
    tipos = ["auto", "camioneta", "moto"]

    tiene_km = _tiene_columna(cur, "vehiculos", "km_actual")
    tiene_comb = _tiene_columna(cur, "vehiculos", "combustible_actual")

    for _ in range(cant):
        marca = random.choice(marcas)
        modelo = random.choice(modelos)
        anio = random.randint(2000, 2024)
        tipo = random.choice(tipos)
        precio = random.randint(5000, 30000)

        # Patente alternada vieja/nueva
        if random.random() < 0.5:
            patente = "{}{}{}{:03d}".format(
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                random.randint(0, 999),
            )
        else:
            patente = "{}{}{:03d}{}{}".format(
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                random.randint(0, 999),
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            )

        km_actual = random.randint(0, 250000)
        combustible_actual = round(random.uniform(0, 50), 1)

        if tiene_km or tiene_comb:
            cur.execute(
                """
                INSERT INTO vehiculos
                    (patente, marca, modelo, anio, tipo, precio_por_dia,
                     activo, estado, km_actual, combustible_actual)
                VALUES (?, ?, ?, ?, ?, ?, 1, 'DISPONIBLE', ?, ?)
                """,
                (patente, marca, modelo, anio, tipo, precio, km_actual, combustible_actual),
            )
        else:
            cur.execute(
                """
                INSERT INTO vehiculos
                    (patente, marca, modelo, anio, tipo, precio_por_dia, activo, estado)
                VALUES (?, ?, ?, ?, ?, ?, 1, 'DISPONIBLE')
                """,
                (patente, marca, modelo, anio, tipo, precio),
            )

    conn.commit()
    conn.close()
    print("  - Vehículos generados.")


# -------------------------------------------------
# Mantenimientos
# -------------------------------------------------
def generar_mantenimientos(cant=10):
    conn = get_connection()
    cur = conn.cursor()

    print(f"Generando {cant} mantenimientos...")

    cur.execute("SELECT id_vehiculo FROM vehiculos")
    lista = [r[0] for r in cur.fetchall()]
    if not lista:
        conn.close()
        print("  - No hay vehículos, no se generan mantenimientos.")
        return

    descripciones = ["Cambio de aceite", "Frenos", "Revisión general", "Correa", "Neumáticos"]

    for _ in range(cant):
        vid = random.choice(lista)

        inicio = date.today() - timedelta(days=random.randint(0, 60))
        fin = inicio + timedelta(days=random.randint(1, 5))
        desc = random.choice(descripciones)

        cur.execute(
            """
            INSERT INTO mantenimientos
                (id_vehiculo, fecha_inicio, fecha_fin, descripcion)
            VALUES (?, ?, ?, ?)
            """,
            (vid, inicio.isoformat(), fin.isoformat(), desc),
        )

    conn.commit()
    conn.close()
    print("  - Mantenimientos generados.")


# -------------------------------------------------
# Alquileres (soporta o no km/combustible según la BD)
# -------------------------------------------------
def generar_alquileres(cant=40):
    conn = get_connection()
    cur = conn.cursor()

    print(f"Generando {cant} alquileres...")

    cur.execute("SELECT id_cliente FROM clientes")
    clientes = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT id_empleado FROM empleados")
    empleados = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT id_vehiculo FROM vehiculos")
    vehiculos = [r[0] for r in cur.fetchall()]

    if not clientes or not empleados or not vehiculos:
        conn.close()
        print("  - Faltan datos para generar alquileres.")
        return

    tiene_km_ini = _tiene_columna(cur, "alquileres", "km_inicial")
    tiene_km_fin = _tiene_columna(cur, "alquileres", "km_final")
    tiene_ci = _tiene_columna(cur, "alquileres", "combustible_inicial")
    tiene_cf = _tiene_columna(cur, "alquileres", "combustible_final")

    for _ in range(cant):
        cid = random.choice(clientes)
        eid = random.choice(empleados)
        vid = random.choice(vehiculos)

        inicio = date.today() - timedelta(days=random.randint(1, 90))
        fin = inicio + timedelta(days=random.randint(1, 10))
        precio_dia = random.randint(5000, 30000)
        monto_extra = random.randint(0, 20000)

        if tiene_km_ini or tiene_km_fin or tiene_ci or tiene_cf:
            # busco km/comb del vehículo si existen columnas
            cur.execute(
                "SELECT km_actual, combustible_actual FROM vehiculos WHERE id_vehiculo = ?",
                (vid,),
            )
            row = cur.fetchone()
            km_i = row[0] if row and row[0] is not None else 0
            comb_i = row[1] if row and row[1] is not None else 0.0

            km_f = km_i + random.randint(10, 500)
            comb_f = max(0, comb_i - random.uniform(0, 10))

            cur.execute(
                """
                INSERT INTO alquileres
                    (id_cliente, id_vehiculo, id_empleado,
                     fecha_inicio, fecha_fin, precio_por_dia,
                     estado, total,
                     km_inicial, km_final, combustible_inicial, combustible_final)
                VALUES (?, ?, ?, ?, ?, ?, 'CERRADO', ?, ?, ?, ?, ?)
                """,
                (
                    cid, vid, eid,
                    inicio.isoformat(), fin.isoformat(), precio_dia,
                    monto_extra,
                    km_i, km_f, comb_i, comb_f,
                ),
            )
        else:
            cur.execute(
                """
                INSERT INTO alquileres
                    (id_cliente, id_vehiculo, id_empleado,
                     fecha_inicio, fecha_fin, precio_por_dia,
                     estado, total)
                VALUES (?, ?, ?, ?, ?, ?, 'CERRADO', ?)
                """,
                (
                    cid, vid, eid,
                    inicio.isoformat(), fin.isoformat(), precio_dia,
                    monto_extra,
                ),
            )

    conn.commit()
    conn.close()
    print("  - Alquileres generados.")


# -------------------------------------------------
# Incidentes (según schema: id_alquiler, tipo, descripcion, monto, estado)
#   ➜ ahora intenta poner fecha dentro del rango del alquiler (si existe columna fecha)
# -------------------------------------------------
def generar_incidentes(cant=20):
    conn = get_connection()
    cur = conn.cursor()

    print(f"Generando {cant} incidentes...")

    # Traigo alquileres con fechas para poder generar una fecha coherente
    cur.execute("SELECT id_alquiler, fecha_inicio, fecha_fin FROM alquileres")
    alquileres = cur.fetchall()  # (id, fecha_inicio, fecha_fin)

    if not alquileres:
        conn.close()
        print("  - No hay alquileres, no se generan incidentes.")
        return

    tiene_fecha = _tiene_columna(cur, "incidentes", "fecha")

    tipos = ["Rotura leve", "Rotura severa", "Multa", "Choque"]
    estados = ["ABIERTO", "RESUELTO"]

    def parse_fecha(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    for _ in range(cant):
        aid, f_ini_str, f_fin_str = random.choice(alquileres)
        f_ini = parse_fecha(f_ini_str)
        f_fin = parse_fecha(f_fin_str) or f_ini

        # elijo una fecha de incidente dentro del rango del alquiler
        if f_ini and f_fin and f_fin >= f_ini:
            delta = (f_fin - f_ini).days
            offset = random.randint(0, max(delta, 0))
            f_inc = f_ini + timedelta(days=offset)
        else:
            # fallback: uso fecha_fin o hoy
            f_inc = f_fin or f_ini or date.today()

        tipo = random.choice(tipos)
        desc = f"Incidente: {tipo.lower()}"
        monto = random.randint(1000, 50000)
        estado = random.choice(estados)

        if tiene_fecha:
            # Si la columna fecha existe, la usamos
            cur.execute(
                """
                INSERT INTO incidentes
                    (id_alquiler, tipo, descripcion, monto, estado, fecha)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (aid, tipo, desc, monto, estado, f_inc.isoformat()),
            )
        else:
            # Si todavía no existe columna fecha, insertamos como antes
            cur.execute(
                """
                INSERT INTO incidentes
                    (id_alquiler, tipo, descripcion, monto, estado)
                VALUES (?, ?, ?, ?, ?)
                """,
                (aid, tipo, desc, monto, estado),
            )

    conn.commit()
    conn.close()
    print("  - Incidentes generados.")


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    print("\n==== GENERACIÓN DE DATOS DE PRUEBA ====\n")

    generar_admin()
    generar_empleados()
    generar_clientes()
    generar_vehiculos()
    generar_alquileres()
    generar_mantenimientos()
    generar_incidentes()

    print("\n==== FINALIZADO ====\n")


if __name__ == "__main__":
    main()
