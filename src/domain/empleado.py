# src/domain/empleado.py

class Empleado:
    def __init__(
        self,
        id_empleado,
        nombre,
        apellido,
        dni,
        email,
        telefono,
        usuario,
        password,
        rol,
        activo=True,
    ):
        self.id_empleado = id_empleado
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.email = email
        self.telefono = telefono
        self.usuario = usuario
        self.password = password
        self.rol = rol          # "ADMIN" o "EMPLEADO"
        self.activo = activo

    def __str__(self):
        estado = "ACTIVO" if self.activo else "INACTIVO"
        return (
            f"Empleado(id={self.id_empleado}, nombre={self.nombre} {self.apellido}, "
            f"dni={self.dni}, usuario={self.usuario}, rol={self.rol}, estado={estado})"
        )
