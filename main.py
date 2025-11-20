from src.repositories.db_connection import init_db

def main():
    print("Inicializando base de datos...")
    init_db()
    print("BD lista.\n")

if __name__ == "__main__":
    main()
