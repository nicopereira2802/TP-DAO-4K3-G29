import sqlite3
import re

from src.domain.vehiculo import Vehiculo
from src.repositories.vehiculo_repository import VehiculoRepository
# --- IMPORTAMOS LA NUEVA FÁBRICA ---
from src.domain.vehiculo_factory import VehiculoFactory


class VehiculoService:

    TIPOS_VALIDOS = ["auto", "camioneta", "moto"]

    PATENTE_REGEX_VIEJA = r"^[A-Z]{3}[0-9]{3}$"
    PATENTE_REGEX_NUEVA = r"^[A-Z]{2}[0-9]{3}[A-Z]{2}$"

    # ---------------------------------------------------------------
    # Validación de formato de patente
    # ---------------------------------------------------------------
    @staticmethod
    def _patente_valida(patente):
        patente = (patente or "").strip().upper()

        if re.match(VehiculoService.PATENTE_REGEX_VIEJA, patente):
            return True

        if re.match(VehiculoService.PATENTE_REGEX_NUEVA, patente):
            return True

        return False

    # ---------------------------------------------------------------
    # Crear Vehículo (AHORA USA FACTORY METHOD)
    # ---------------------------------------------------------------
    @staticmethod
    def crear_vehiculo(
        usuario_actual,
        patente,
        marca,
        modelo,
        anio,
        tipo,
        precio_por_dia,
        km_actual,
        combustible_actual,
    ):

        # Validar rol
        if (usuario_actual.get("rol") or "").upper() != "ADMIN":
            return False, "Solo un administrador puede registrar vehículos."

        # Limpieza básica
        patente = (patente or "").strip().upper()
        marca = (marca or "").strip()
        modelo = (modelo or "").strip()
        
        # Validaciones de negocio
        if not VehiculoService._patente_valida(patente):
            return False, "La patente no tiene un formato válido (AAA123 o AA123AA)."

        if " " in patente:
            return False, "La patente no debe contener espacios."

        existente = VehiculoRepository.buscar_por_patente(patente)
        if existente is not None:
            return False, "Ya existe un vehículo con esa patente."

        if not marca or not modelo:
            return False, "La marca y el modelo son obligatorios."

        if not str(anio).isdigit():
            return False, "El año debe ser numérico."
        anio = int(anio)
        if anio < 1980 or anio > 2030:
            return False, "El año debe estar entre 1980 y 2030."

        # Conversiones numéricas
        try:
            precio_por_dia = float(precio_por_dia)
            km_actual = float(km_actual)
            combustible_actual = float(combustible_actual)
        except (TypeError, ValueError):
            return False, "Precio, KM y Combustible deben ser numéricos."

        if precio_por_dia <= 0: return False, "El precio debe ser mayor a cero."
        if km_actual < 0: return False, "El KM no puede ser negativo."
        if combustible_actual < 0: return False, "El combustible no puede ser negativo."

        # --- AQUI APLICAMOS EL PATRÓN FACTORY ---
        # Delegamos la creación del objeto a la fábrica en lugar de hacerlo directo
        try:
            vehiculo = VehiculoFactory.get_vehiculo(
                tipo=tipo,
                id_vehiculo=None,
                patente=patente,
                marca=marca,
                modelo=modelo,
                anio=anio,
                precio_por_dia=precio_por_dia,
                activo=True,
                estado="DISPONIBLE",
                km_actual=km_actual,
                combustible_actual=combustible_actual,
            )
        except ValueError as e:
            # Si la fábrica rechaza el tipo (ej: "avion"), capturamos el error aquí
            return False, str(e)

        # Persistencia
        try:
            vehiculo_creado = VehiculoRepository.crear(vehiculo)
            return True, vehiculo_creado
        except sqlite3.IntegrityError:
            return False, "Error al guardar el vehículo. Puede ser patente duplicada."

    # ---------------------------------------------------------------
    # Listar
    # ---------------------------------------------------------------
    @staticmethod
    def listar_vehiculos():
        vehiculos = VehiculoRepository.listar()
        return True, vehiculos

    # ---------------------------------------------------------------
    # Obtener por ID
    # ---------------------------------------------------------------
    @staticmethod
    def obtener_vehiculo_por_id(id_vehiculo):
        vehiculo = VehiculoRepository.obtener_por_id(id_vehiculo)
        if vehiculo is None:
            return False, "No se encontró un vehículo con ese ID."
        return True, vehiculo

    # ---------------------------------------------------------------
    # Actualizar
    # ---------------------------------------------------------------
    @staticmethod
    def actualizar_vehiculo(
        id_vehiculo,
        patente,
        marca,
        modelo,
        anio,
        tipo,
        precio_por_dia,
        km_actual,
        combustible_actual,
    ):

        ok, vehiculo = VehiculoService.obtener_vehiculo_por_id(id_vehiculo)
        if not ok:
            return False, vehiculo

        patente = (patente or "").strip().upper()
        marca = (marca or "").strip()
        modelo = (modelo or "").strip()
        tipo = (tipo or "").strip().lower()

        # Validaciones de actualización
        if not VehiculoService._patente_valida(patente):
            return False, "La patente no tiene un formato válido."

        existente = VehiculoRepository.buscar_por_patente(patente)
        if existente and existente.id_vehiculo != id_vehiculo:
            return False, "Ya existe otro vehículo con esa patente."

        if not marca or not modelo: return False, "Marca y modelo requeridos."
        
        try:
            anio = int(anio)
            precio_por_dia = float(precio_por_dia)
            km_actual = float(km_actual)
            combustible_actual = float(combustible_actual)
        except ValueError:
            return False, "Datos numéricos inválidos."

        if tipo not in VehiculoService.TIPOS_VALIDOS:
            return False, "Tipo de vehículo inválido."

        # Aplicar cambios
        vehiculo.patente = patente
        vehiculo.marca = marca
        vehiculo.modelo = modelo
        vehiculo.anio = anio
        vehiculo.tipo = tipo
        vehiculo.precio_por_dia = precio_por_dia
        vehiculo.km_actual = km_actual
        vehiculo.combustible_actual = combustible_actual

        try:
            VehiculoRepository.actualizar(vehiculo)
            return True, vehiculo
        except sqlite3.IntegrityError:
            return False, "Error al actualizar (posible patente duplicada)."

    # ---------------------------------------------------------------
    # Baja lógica
    # ---------------------------------------------------------------
    @staticmethod
    def inactivar_vehiculo(id_vehiculo):
        vehiculo = VehiculoRepository.obtener_por_id(id_vehiculo)
        if vehiculo is None:
            return False, "No se encontró el vehículo."

        if not vehiculo.activo:
            return False, "El vehículo ya está inactivo."

        VehiculoRepository.inactivar(id_vehiculo)
        return True, "Vehículo desactivado correctamente."