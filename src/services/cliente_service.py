from typing import List
from sqlite3 import IntegrityError, OperationalError

from src.domain.cliente import Cliente
from src.repositories.cliente_repository import ClienteRepository


class ClienteService:
    def __init__(self, repo=None):
        self._repo = repo or ClienteRepository

    def listar_clientes(self) -> List[Cliente]:
        return self._repo.listar()

    def crear_cliente(self, nombre: str, dni: str, email: str, telefono: str) -> Cliente:
        nombre = nombre.strip()
        partes = nombre.split()
        if len(partes) > 1:
            nombre_pila = " ".join(partes[:-1])
            apellido = partes[-1]
        else:
            nombre_pila = nombre
            apellido = ""

        cliente = Cliente(
            id=None,
            nombre=nombre_pila,
            apellido=apellido,
            dni=dni,
            email=email,
            telefono=telefono,
            activo=True,
        )

        try:
            return self._repo.crear(cliente)

        except IntegrityError:
            raise Exception(
                "Ya existe un cliente registrado con ese DNI.\n"
                "No se permiten DNI duplicados."
            )

        except OperationalError as e:
            if "database is locked" in str(e).lower():
                raise Exception(
                    "La base de datos está ocupada en este momento.\n"
                    "Cerrá otros programas que la estén usando y volvé a intentar."
                )
            raise

        except Exception as e:
            raise Exception(f"Ocurrió un error al crear el cliente: {e}")

    def modificar_cliente(
        self,
        cliente_id: int,
        nombre: str,
        dni: str,
        email: str,
        telefono: str,
        activo: bool,
    ) -> Cliente:
        cliente = self._repo.obtener_por_id(cliente_id)
        if cliente is None:
            raise ValueError(f"Cliente con id {cliente_id} no encontrado")

        nombre = nombre.strip()
        partes = nombre.split()
        if len(partes) > 1:
            nombre_pila = " ".join(partes[:-1])
            apellido = partes[-1]
        else:
            nombre_pila = nombre
            apellido = ""

        cliente.nombre = nombre_pila
        cliente.apellido = apellido
        cliente.dni = dni
        cliente.email = email
        cliente.telefono = telefono
        cliente.activo = activo

        try:
            self._repo.actualizar(cliente)
            return cliente

        except IntegrityError:
            raise Exception(
                "El DNI ingresado ya está asociado a otro cliente.\n"
                "No se permiten DNI duplicados."
            )

        except OperationalError as e:
            if "database is locked" in str(e).lower():
                raise Exception(
                    "La base de datos está ocupada en este momento.\n"
                    "Cerrá otros programas que la estén usando y volvé a intentar."
                )
            raise

        except Exception as e:
            raise Exception(f"Ocurrió un error al modificar el cliente: {e}")

    def desactivar_cliente(self, cliente_id: int):
        self._repo.inactivar(cliente_id)
