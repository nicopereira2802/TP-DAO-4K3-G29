from src.domain.empleado import Empleado
from src.repositories.empleado_repository import EmpleadoRepository
import sqlite3


class EmpleadoService:

    @staticmethod
    def _email_valido(email):
        email = email.strip()

        # No espacios
        if " " in email:
            return False

        # Debe tener exactamente 1 "@"
        if email.count("@") != 1:
            return False

        parte_local, dominio = email.split("@")

        # Parte antes del @ debe existir
        if not parte_local:
            return False

        # Dominio debe existir
        if not dominio:
            return False

        # Dominio debe tener al menos un punto
        if "." not in dominio:
            return False

        # El dominio no puede empezar con "."
        if dominio.startswith("."):
            return False

        # No permitir partes vacías en el dominio
        partes_dominio = dominio.split(".")
        for p in partes_dominio:
            if not p:
                return False

        return True

    # ================== ALTA ==================

    @staticmethod
    def crear_empleado(nombre, apellido, dni, email, telefono, usuario, password, rol):
        # Limpieza
        nombre = (nombre or "").strip()
        apellido = (apellido or "").strip()
        dni = (dni or "").strip()
        email = (email or "").strip()
        telefono = (telefono or "").strip()
        usuario = (usuario or "").strip()
        password = (password or "").strip()
        rol = (rol or "").strip().upper()

        # Validaciones básicas
        if not nombre:
            return False, "El nombre no puede estar vacío."

        if not apellido:
            return False, "El apellido no puede estar vacío."

        if not dni:
            return False, "El DNI no puede estar vacío."

        if not dni.isdigit():
            return False, "El DNI debe contener solo números."

        if len(dni) < 7 or len(dni) > 10:
            return False, "El DNI debe tener entre 7 y 10 dígitos."

        if not email:
            return False, "El email no puede estar vacío."

        if not EmpleadoService._email_valido(email):
            return False, "El email no tiene un formato válido."

        if not usuario:
            return False, "El usuario no puede estar vacío."

        if " " in usuario:
            return False, "El usuario no puede contener espacios."

        if not password or len(password) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."

        if rol not in ("ADMIN", "EMPLEADO"):
            return False, "El rol debe ser ADMIN o EMPLEADO."

        # Validación de DNI duplicado 
        existente = EmpleadoRepository.buscar_por_dni(dni)
        if existente is not None:
            return False, "Ya existe un empleado registrado con ese DNI."

        empleado = Empleado(
            id_empleado=None,
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            email=email,
            telefono=telefono,
            usuario=usuario,
            password=password,
            rol=rol,
            activo=True,
        )

        try:
            empleado_creado = EmpleadoRepository.crear(empleado)
            return True, empleado_creado

        except sqlite3.IntegrityError as e:
            msg = str(e).lower()
            # Asumimos que en la tabla hay UNIQUE(dni), UNIQUE(email), UNIQUE(usuario)
            if "dni" in msg:
                return False, "Ya existe un empleado con ese DNI en la base de datos."
            if "email" in msg:
                return False, "Ya existe un empleado con ese email en la base de datos."
            if "usuario" in msg:
                return False, "El nombre de usuario ya está en uso. Elegí otro."
            return False, "No se pudo crear el empleado por una restricción de la base de datos."

        except Exception as e:
            return False, f"Ocurrió un error al crear el empleado: {e}"

    # ================== LISTAR / OBTENER ==================

    @staticmethod
    def listar_empleados():
        try:
            empleados = EmpleadoRepository.listar()
            return True, empleados
        except Exception as e:
            return False, f"No se pudieron listar los empleados: {e}"

    @staticmethod
    def obtener_empleado_por_id(id_empleado):
        empleado = EmpleadoRepository.obtener_por_id(id_empleado)
        if empleado is None:
            return False, "No se encontró un empleado con ese ID."
        return True, empleado

    # ================== ACTUALIZAR ==================

    @staticmethod
    def actualizar_empleado(
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
        # Buscar empleado existente
        ok, empleado_o_msg = EmpleadoService.obtener_empleado_por_id(id_empleado)
        if not ok:
            return False, empleado_o_msg

        empleado = empleado_o_msg

        # Limpieza
        nombre = (nombre or "").strip()
        apellido = (apellido or "").strip()
        dni = (dni or "").strip()
        email = (email or "").strip()
        telefono = (telefono or "").strip()
        usuario = (usuario or "").strip()
        password = (password or "").strip()
        rol = (rol or "").strip().upper()

        # Validaciones
        if not nombre:
            return False, "El nombre no puede estar vacío."

        if not apellido:
            return False, "El apellido no puede estar vacío."

        if not dni:
            return False, "El DNI no puede estar vacío."

        if not dni.isdigit():
            return False, "El DNI debe contener solo números."

        if len(dni) < 7 or len(dni) > 10:
            return False, "El DNI debe tener entre 7 y 10 dígitos."

        if not email:
            return False, "El email no puede estar vacío."

        if not EmpleadoService._email_valido(email):
            return False, "El email no tiene un formato válido."

        if not usuario:
            return False, "El usuario no puede estar vacío."

        if " " in usuario:
            return False, "El usuario no puede contener espacios."

        if not password or len(password) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."

        if rol not in ("ADMIN", "EMPLEADO"):
            return False, "El rol debe ser ADMIN o EMPLEADO."

        # Si cambió el DNI, podemos chequear duplicado
        if dni != empleado.dni:
            otro = EmpleadoRepository.buscar_por_dni(dni)
            if otro is not None and otro.id_empleado != id_empleado:
                return False, "Ya existe otro empleado con ese DNI."

        # Actualizar campos
        empleado.nombre = nombre
        empleado.apellido = apellido
        empleado.dni = dni
        empleado.email = email
        empleado.telefono = telefono
        empleado.usuario = usuario
        empleado.password = password
        empleado.rol = rol
        empleado.activo = bool(activo)

        try:
            EmpleadoRepository.actualizar(empleado)
            return True, empleado
        except sqlite3.IntegrityError as e:
            msg = str(e).lower()
            if "dni" in msg:
                return False, "Ya existe un empleado con ese DNI en la base de datos."
            if "email" in msg:
                return False, "Ya existe un empleado con ese email en la base de datos."
            if "usuario" in msg:
                return False, "El nombre de usuario ya está en uso. Elegí otro."
            return False, "No se pudo actualizar el empleado por una restricción de la base de datos."
        except Exception as e:
            return False, f"Ocurrió un error al actualizar el empleado: {e}"

    # ================== BAJA LÓGICA ==================

    @staticmethod
    def inactivar_empleado(id_empleado):
        empleado = EmpleadoRepository.obtener_por_id(id_empleado)
        if empleado is None:
            return False, "No se encontró un empleado con ese ID."

        if not empleado.activo:
            return False, "El empleado ya está inactivo."

        EmpleadoRepository.inactivar(id_empleado)
        return True, "Empleado inactivado correctamente."
