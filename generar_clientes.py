from src.repositories.db_connection import get_connection
import random

def main(cantidad=50):
    conn = get_connection()
    cur = conn.cursor()

    print(f"Generando {cantidad} clientes...")

    nombres = ["Juan", "Pedro", "Luis", "Nicolás", "Matías", "Hernán", "Mario", "Diego", "Andrés", "Federico"]
    apellidos = ["Gómez", "Pereira", "López", "Martínez", "Ferreyra", "Castro", "Ramos", "Suárez", "Ojeda", "Álvarez"]

    usados_dni = set()

    for _ in range(cantidad):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)

        # DNI único (al menos dentro de este script)
        while True:
            dni = str(random.randint(20000000, 50000000))
            if dni not in usados_dni:
                usados_dni.add(dni)
                break

        # Email único usando el DNI
        email = f"{nombre.lower()}.{apellido.lower()}.{dni}@gmail.com"
        telefono = str(random.randint(1000000, 9000000))

        cur.execute(
            """
            INSERT INTO clientes (nombre, apellido, dni, email, telefono, activo)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (nombre, apellido, dni, email, telefono)
        )

    conn.commit()
    conn.close()
    print("Clientes de prueba generados correctamente.")


if __name__ == "__main__":
    main()
