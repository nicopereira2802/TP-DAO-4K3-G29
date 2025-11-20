from datetime import datetime

from src.repositories.alquiler_repository import AlquilerRepository
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.vehiculo_repository import VehiculoRepository


class ReporteService:

    @staticmethod
    def _parsear_fecha(fecha_str):
        fecha_str = (fecha_str or "").strip()
        if not fecha_str:
            return False, "La fecha no puede estar vacía."
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            return True, fecha
        except ValueError:
            return False, "La fecha debe tener formato AAAA-MM-DD."

    @staticmethod
    def alquileres_por_cliente(id_cliente):
        try:
            id_cliente = int(id_cliente)
        except (TypeError, ValueError):
            return False, "El ID de cliente debe ser numérico."

        cliente = ClienteRepository.obtener_por_id(id_cliente)
        if cliente is None:
            return False, "No se encontró un cliente con ese ID."

        alquileres = AlquilerRepository.listar_por_cliente(id_cliente)
        return True, alquileres

    @staticmethod
    def alquileres_por_vehiculo(id_vehiculo):
        try:
            id_vehiculo = int(id_vehiculo)
        except (TypeError, ValueError):
            return False, "El ID de vehículo debe ser numérico."

        vehiculo = VehiculoRepository.obtener_por_id(id_vehiculo)
        if vehiculo is None:
            return False, "No se encontró un vehículo con ese ID."

        alquileres = AlquilerRepository.listar_por_vehiculo(id_vehiculo)
        return True, alquileres

    @staticmethod
    def alquileres_en_rango(fecha_desde_str, fecha_hasta_str):
        ok_desde, f_desde_o_msg = ReporteService._parsear_fecha(fecha_desde_str)
        if not ok_desde:
            return False, f_desde_o_msg

        ok_hasta, f_hasta_o_msg = ReporteService._parsear_fecha(fecha_hasta_str)
        if not ok_hasta:
            return False, f_hasta_o_msg

        fecha_desde = f_desde_o_msg
        fecha_hasta = f_hasta_o_msg

        if fecha_hasta < fecha_desde:
            return False, "La fecha hasta no puede ser anterior a la fecha desde."

        alquileres = AlquilerRepository.listar()
        resultado = []

        for a in alquileres:
            ok_ai, f_ai = ReporteService._parsear_fecha(a.fecha_inicio)
            if not ok_ai:
                continue
            if fecha_desde <= f_ai <= fecha_hasta:
                resultado.append(a)

        return True, resultado

    @staticmethod
    def total_facturado_en_rango(fecha_desde_str, fecha_hasta_str):
        ok, alquileres_o_msg = ReporteService.alquileres_en_rango(fecha_desde_str, fecha_hasta_str)
        if not ok:
            return False, alquileres_o_msg

        alquileres = alquileres_o_msg
        total = 0.0
        for a in alquileres:
            if a.estado == "CERRADO":
                try:
                    total += float(a.total)
                except (TypeError, ValueError):
                    continue

        return True, total
