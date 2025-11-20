from datetime import datetime

from src.domain.mantenimiento import Mantenimiento
from src.repositories.mantenimiento_repository import MantenimientoRepository
from src.repositories.vehiculo_repository import VehiculoRepository
from src.repositories.alquiler_repository import AlquilerRepository


class MantenimientoService:

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
    def _rango_se_solapa(desde1, hasta1, desde2, hasta2):
        return not (hasta1 < desde2 or hasta2 < desde1)

    @staticmethod
    def crear_mantenimiento(id_vehiculo, fecha_inicio_str, fecha_fin_str, descripcion):
        try:
            id_vehiculo = int(id_vehiculo)
        except (TypeError, ValueError):
            return False, "El ID de vehículo debe ser numérico."

        if id_vehiculo <= 0:
            return False, "El ID de vehículo debe ser mayor que cero."

        descripcion = (descripcion or "").strip()
        if not descripcion:
            return False, "La descripción no puede estar vacía."

        ok_ini, f_ini_o_msg = MantenimientoService._parsear_fecha(fecha_inicio_str)
        if not ok_ini:
            return False, f_ini_o_msg

        ok_fin, f_fin_o_msg = MantenimientoService._parsear_fecha(fecha_fin_str)
        if not ok_fin:
            return False, f_fin_o_msg

        fecha_inicio = f_ini_o_msg
        fecha_fin = f_fin_o_msg

        if fecha_fin < fecha_inicio:
            return False, "La fecha de fin no puede ser anterior a la fecha de inicio."

        vehiculo = VehiculoRepository.obtener_por_id(id_vehiculo)
        if vehiculo is None:
            return False, "No se encontró un vehículo con ese ID."
        if not vehiculo.activo:
            return False, "El vehículo está inactivo y no se le puede asignar mantenimiento."

        mantenimientos = MantenimientoRepository.listar_por_vehiculo(id_vehiculo)
        for m in mantenimientos:
            ok_m_ini, f_m_ini = MantenimientoService._parsear_fecha(m.fecha_inicio)
            ok_m_fin, f_m_fin = MantenimientoService._parsear_fecha(m.fecha_fin)
            if ok_m_ini and ok_m_fin:
                if MantenimientoService._rango_se_solapa(fecha_inicio, fecha_fin, f_m_ini, f_m_fin):
                    return False, "Ya existe un mantenimiento en ese rango de fechas para el vehículo."

        alquileres = AlquilerRepository.listar_por_vehiculo(id_vehiculo)
        for a in alquileres:
            if a.estado != "ABIERTO":
                continue
            ok_a_ini, f_a_ini = MantenimientoService._parsear_fecha(a.fecha_inicio)
            ok_a_fin, f_a_fin = MantenimientoService._parsear_fecha(a.fecha_fin)
            if ok_a_ini and ok_a_fin:
                if MantenimientoService._rango_se_solapa(fecha_inicio, fecha_fin, f_a_ini, f_a_fin):
                    return False, "El vehículo tiene alquileres activos en ese rango de fechas."

        mantenimiento = Mantenimiento(
            id_mantenimiento=None,
            id_vehiculo=id_vehiculo,
            fecha_inicio=fecha_inicio.isoformat(),
            fecha_fin=fecha_fin.isoformat(),
            descripcion=descripcion
        )

        mantenimiento_creado = MantenimientoRepository.crear(mantenimiento)
        return True, mantenimiento_creado

    @staticmethod
    def listar_mantenimientos():
        mantenimientos = MantenimientoRepository.listar()
        return True, mantenimientos

    @staticmethod
    def listar_mantenimientos_por_vehiculo(id_vehiculo):
        try:
            id_vehiculo = int(id_vehiculo)
        except (TypeError, ValueError):
            return False, "El ID de vehículo debe ser numérico."

        ms = MantenimientoRepository.listar_por_vehiculo(id_vehiculo)
        return True, ms

    @staticmethod
    def eliminar_mantenimiento(id_mantenimiento):
        try:
            id_mantenimiento = int(id_mantenimiento)
        except (TypeError, ValueError):
            return False, "El ID de mantenimiento debe ser numérico."

        existente = MantenimientoRepository.obtener_por_id(id_mantenimiento)
        if existente is None:
            return False, "No se encontró un mantenimiento con ese ID."

        MantenimientoRepository.eliminar(id_mantenimiento)
        return True, "Mantenimiento eliminado correctamente."
