from src.domain.incidente import Incidente
from src.repositories.incidente_repository import IncidenteRepository
from src.repositories.alquiler_repository import AlquilerRepository


class IncidenteService:

    TIPOS_VALIDOS = ["MULTA", "DANO", "OTRO"]

    @staticmethod
    def crear_incidente(id_alquiler, tipo, descripcion, monto):
        try:
            id_alquiler = int(id_alquiler)
        except (TypeError, ValueError):
            return False, "El ID de alquiler debe ser numérico."

        if id_alquiler <= 0:
            return False, "El ID de alquiler debe ser mayor que cero."

        tipo = (tipo or "").strip().upper()
        descripcion = (descripcion or "").strip()

        if not descripcion:
            return False, "La descripción no puede estar vacía."

        if tipo not in IncidenteService.TIPOS_VALIDOS:
            return False, f"Tipo inválido. Debe ser uno de: {', '.join(IncidenteService.TIPOS_VALIDOS)}."

        try:
            monto = float(monto)
        except (TypeError, ValueError):
            return False, "El monto debe ser numérico."

        if monto < 0:
            return False, "El monto no puede ser negativo."

        ok_alq, alq_o_msg = IncidenteService._obtener_alquiler_valido(id_alquiler)
        if not ok_alq:
            return False, alq_o_msg

        incidente = Incidente(
            id_incidente=None,
            id_alquiler=id_alquiler,
            tipo=tipo,
            descripcion=descripcion,
            monto=monto,
            estado="PENDIENTE"
        )

        incidente_creado = IncidenteRepository.crear(incidente)
        return True, incidente_creado

    @staticmethod
    def _obtener_alquiler_valido(id_alquiler):
        alquiler = AlquilerRepository.obtener_por_id(id_alquiler)
        if alquiler is None:
            return False, "No se encontró un alquiler con ese ID."
        return True, alquiler

    @staticmethod
    def listar_incidentes():
        incidentes = IncidenteRepository.listar()
        return True, incidentes

    @staticmethod
    def listar_incidentes_por_alquiler(id_alquiler):
        try:
            id_alquiler = int(id_alquiler)
        except (TypeError, ValueError):
            return False, "El ID de alquiler debe ser numérico."

        incidentes = IncidenteRepository.listar_por_alquiler(id_alquiler)
        return True, incidentes

    @staticmethod
    def marcar_incidente_como_pagado(id_incidente):
        try:
            id_incidente = int(id_incidente)
        except (TypeError, ValueError):
            return False, "El ID de incidente debe ser numérico."

        incidente = IncidenteRepository.obtener_por_id(id_incidente)
        if incidente is None:
            return False, "No se encontró un incidente con ese ID."

        if incidente.estado == "PAGADO":
            return False, "El incidente ya está marcado como pagado."

        incidente.estado = "PAGADO"
        IncidenteRepository.actualizar(incidente)
        return True, "Incidente marcado como pagado correctamente."
