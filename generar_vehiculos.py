from src.repositories.db_connection import get_connection
import random
import string

def generar_patente():
    """Genera patente Mercosur válida: AA123BB."""
    letras = string.ascii_uppercase
    return (
        random.choice(letras)
        + random.choice(letras)
        + str(random.randint(100, 999))
        + random.choice(letras)
        + random.choice(letras)
    )

def main(cantidad=50):
    conn = get_connection()
    cur = conn.cursor()

    print(f"Generando {cantidad} vehículos...")

    marcas = [
        "Toyota", "Volkswagen", "Chevrolet", "Renault", "Ford",
        "Peugeot", "Fiat", "Nissan", "Honda", "Hyundai"
    ]
    modelos = [
        "Corolla", "Gol", "Onix", "Clio", "Fiesta",
        "208", "Cronos", "Versa", "Civic", "Tucson"
    ]
    tipos = ["auto", "moto", "camioneta"]

    usadas = set()

    for _ in range(cantidad):
        # Patente única dentro de este script
        while True:
            patente = generar_patente()
            if patente not in usadas:
                usadas.add(patente)
                break

        marca = random.choice(marcas)
        modelo = random.choice(modelos)
        anio = random.randint(2000, 2023)
        tipo = random.choice(tipos)
        precio_por_dia = random.randint(5000, 25000)

        cur.execute(
            """
            INSERT INTO vehiculos
                (patente, marca, modelo, anio, tipo, precio_por_dia, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (patente, marca, modelo, anio, tipo, precio_por_dia)
        )

    conn.commit()
    conn.close()
    print("Vehículos de prueba generados correctamente.")


if __name__ == "__main__":
    main()
