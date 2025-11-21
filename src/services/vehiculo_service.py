import sqlite3
import re

from src.domain.vehiculo import Vehiculo
from src.repositories.vehiculo_repository import VehiculoRepository


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
    # Crear Vehículo
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

        # Validar rol (usuario_actual es dict)
        if (usuario_actual.get("rol") or "").upper() != "ADMIN":
            return False, "Solo un administrador puede registrar vehículos."

        # Limpieza
        patente = (patente or "").strip().upper()
        marca = (marca or "").strip()
        modelo = (modelo or "").strip()
        tipo = (tipo or "").strip().lower()

        # ---- Validación de patente ----
        if not VehiculoService._patente_valida(patente):
            return False, "La patente no tiene un formato válido (AAA123 o AA123AA)."

        if " " in patente:
            return False, "La patente no debe contener espacios."

        existente = VehiculoRepository.buscar_por_patente(patente)
        if existente is not None:
            return False, "Ya existe un vehículo con esa patente."

        # ---- Marca / Modelo ----
        if not marca:
            return False, "La marca no puede estar vacía."
        if not modelo:
            return False, "El modelo no puede estar vacío."

        # ---- Año ----
        if not str(anio).isdigit():
            return False, "El año debe ser numérico."

        anio = int(anio)
        if anio < 1980 or anio > 2030:
            return False, "El año debe estar entre 1980 y 2030."

        # ---- Tipo ----
        if tipo not in VehiculoService.TIPOS_VALIDOS:
            return False, f"Tipo inválido. Debe ser uno de: {', '.join(VehiculoService.TIPOS_VALIDOS)}."

        # ---- Precio ----
        try:
            precio_por_dia = float(precio_por_dia)
        except ValueError:
            return False, "El precio por día debe ser numérico."

        if precio_por_dia <= 0:
            return False, "El precio por día debe ser mayor que cero."

        if precio_por_dia > 500000:
            return False, "El precio por día es demasiado alto. Ingresá un valor razonable (menor a 500.000)."

        # ---- KM / Combustible ----
        try:
            km_actual = float(km_actual)
        except (TypeError, ValueError):
            return False, "El kilometraje actual debe ser numérico."

        try:
            combustible_actual = float(combustible_actual)
        except (TypeError, ValueError):
            return False, "El combustible actual debe ser numérico."

        if km_actual < 0:
            return False, "El kilometraje actual no puede ser negativo."

        if combustible_actual < 0:
            return False, "El combustible actual no puede ser negativo."

        # ---- Crear instancia Vehiculo ----
        vehiculo = Vehiculo(
            id_vehiculo=None,
            patente=patente,
            marca=marca,
            modelo=modelo,
            anio=anio,
            tipo=tipo,
            precio_por_dia=precio_por_dia,
            activo=True,
            # estado por defecto "DISPONIBLE" en el modelo
            km_actual=km_actual,
            combustible_actual=combustible_actual,
        )

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

        # ---- Validación de patente ----
        if not VehiculoService._patente_valida(patente):
            return False, "La patente no tiene un formato válido."

        if " " in patente:
            return False, "La patente no debe contener espacios."

        # Evitar duplicados si se cambia la patente
        existente = VehiculoRepository.buscar_por_patente(patente)
        if existente and existente.id_vehiculo != id_vehiculo:
            return False, "Ya existe otro vehículo con esa patente."

        # Marca / Modelo
        if not marca:
            return False, "La marca no puede estar vacía."
        if not modelo:
            return False, "El modelo no puede estar vacío."

        # Año
        if not str(anio).isdigit():
            return False, "El año debe ser numérico."

        anio = int(anio)
        if anio < 1980 or anio > 2030:
            return False, "El año debe estar entre 1980 y 2030."

        # Tipo
        if tipo not in VehiculoService.TIPOS_VALIDOS:
            return False, f"Tipo inválido. Debe ser uno de: {', '.join(VehiculoService.TIPOS_VALIDOS)}."

        # Precio
        try:
            precio_por_dia = float(precio_por_dia)
        except ValueError:
            return False, "El precio por día debe ser numérico."

        if precio_por_dia <= 0:
            return False, "El precio por día debe ser mayor que cero."

        if precio_por_dia > 500000:
            return False, "El precio por día es demasiado alto. Ingresá un valor razonable (menor a 500.000)."

        # ---- KM / Combustible ----
        try:
            km_actual = float(km_actual)
        except (TypeError, ValueError):
            return False, "El kilometraje actual debe ser numérico."

        try:
            combustible_actual = float(combustible_actual)
        except (TypeError, ValueError):
            return False, "El combustible actual debe ser numérico."

        if km_actual < 0:
            return False, "El kilometraje actual no puede ser negativo."

        if combustible_actual < 0:
            return False, "El combustible actual no puede ser negativo."

        # ---- Aplicar cambios ----
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
            return False, "Error al actualizar el vehículo. Puede ser patente duplicada."

    # ---------------------------------------------------------------
    # Baja lógica
    # ---------------------------------------------------------------
    @staticmethod
    def inactivar_vehiculo(id_vehiculo):
        vehiculo = VehiculoRepository.obtener_por_id(id_vehiculo)
        if vehiculo is None:
            return False, "No se encontró un vehículo con ese ID."

        if not vehiculo.activo:
            return False, "El vehículo ya está inactivo."

        VehiculoRepository.inactivar(id_vehiculo)
        return True, "Vehículo desactivado correctamente."
