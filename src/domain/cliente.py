# src/domain/cliente.py

class Cliente:
    def __init__(
        self,
        id: int,
        nombre: str,
        apellido: str,
        dni: str,
        email: str,
        telefono: str,
        activo: bool = True,
    ):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.email = email
        self.telefono = telefono
        self.activo = activo

    def __repr__(self) -> str:
        estado = "ACTIVO" if self.activo else "INACTIVO"
        return (
            f"Cliente(id={self.id}, nombre={self.nombre}, "
            f"apellido={self.apellido}, dni={self.dni}, estado={estado})"
        )
