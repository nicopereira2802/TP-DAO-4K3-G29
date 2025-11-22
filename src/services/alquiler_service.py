from datetime import datetime

from src.domain.alquiler import Alquiler
from src.repositories.alquiler_repository import AlquilerRepository
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.vehiculo_repository import VehiculoRepository
from src.repositories.empleado_repository import EmpleadoRepository
from src.repositories.mantenimiento_repository import MantenimientoRepository


class AlquilerService:

    @staticmethod
    def _parsear_fecha(fecha_str):
        """
        Intenta convertir una cadena 'AAAA-MM-DD' a date.
        Devuelve (True, date) o (False, mensaje_error).
        """
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
        """
        Recibe 4 date y devuelve True si los rangos [desde1, hasta1] y [desde2, hasta2] se solapan.
        """
        return not (hasta1 < desde2 or hasta2 < desde1)

    @staticmethod
    def crear_alquiler(id_cliente, id_vehiculo, id_empleado, fecha_inicio_str, fecha_fin_str):
        # Validar IDs (que sean enteros positivos)
        try:
            id_cliente = int(id_cliente)
            id_vehiculo = int(id_vehiculo)
            id_empleado = int(id_empleado)
        except (TypeError, ValueError):
            return False, "Los IDs de cliente, vehículo y empleado deben ser numéricos."

        if id_cliente <= 0 or id_vehiculo <= 0 or id_empleado <= 0:
            return False, "Los IDs de cliente, vehículo y empleado deben ser mayores que cero."

        # Validar fechas
        ok_ini, fecha_inicio_o_msg = AlquilerService._parsear_fecha(fecha_inicio_str)
        if not ok_ini:
            return False, fecha_inicio_o_msg

        ok_fin, fecha_fin_o_msg = AlquilerService._parsear_fecha(fecha_fin_str)
        if not ok_fin:
            return False, fecha_fin_o_msg

        fecha_inicio = fecha_inicio_o_msg
        fecha_fin = fecha_fin_o_msg

        if fecha_fin < fecha_inicio:
            return False, "La fecha de fin no puede ser anterior a la fecha de inicio."

        # Verificar existencia y estado de cliente
        cliente = ClienteRepository.obtener_por_id(id_cliente)
        if cliente is None:
            return False, "No se encontró un cliente con ese ID."
        if not cliente.activo:
            return False, "El cliente está inactivo y no puede realizar alquileres."

        # Verificar existencia y estado de vehículo
        vehiculo = VehiculoRepository.obtener_por_id(id_vehiculo)
        if vehiculo is None:
            return False, "No se encontró un vehículo con ese ID."
        if not vehiculo.activo:
            return False, "El vehículo está inactivo y no puede ser alquilado."

        # 🚫 Validar estado del vehículo según el TP
        estado_vehiculo = (getattr(vehiculo, "estado", None) or "DISPONIBLE").upper()

        if estado_vehiculo == "ALQUILADO":
            return False, "El vehículo ya se encuentra alquilado y no está disponible."

        if estado_vehiculo == "MANTENIMIENTO":
            return False, "El vehículo está en mantenimiento y no puede ser alquilado."

        # Verificar existencia y estado de empleado
        empleado = EmpleadoRepository.obtener_por_id(id_empleado)
        if empleado is None:
            return False, "No se encontró un empleado con ese ID."
        if not empleado.activo:
            return False, "El empleado está inactivo y no puede gestionar alquileres."

        # Chequear alquileres activos para el vehículo en el rango dado
        fecha_inicio_iso = fecha_inicio.isoformat()
        fecha_fin_iso = fecha_fin.isoformat()

        if AlquilerRepository.existe_alquiler_activo_en_rango(
            id_vehiculo, fecha_inicio_iso, fecha_fin_iso
        ):
            return False, "El vehículo ya tiene un alquiler activo en ese rango de fechas."

        # Chequear mantenimientos para el vehículo
        mantenimientos = MantenimientoRepository.listar_por_vehiculo(id_vehiculo)
        for m in mantenimientos:
            ok_m_ini, f_m_ini = AlquilerService._parsear_fecha(m.fecha_inicio)
            ok_m_fin, f_m_fin = AlquilerService._parsear_fecha(m.fecha_fin)
            if ok_m_ini and ok_m_fin:
                if AlquilerService._rango_se_solapa(fecha_inicio, fecha_fin, f_m_ini, f_m_fin):
                    return False, "El vehículo tiene un mantenimiento programado en ese rango de fechas."

        # Calcular días y precio estimado
        dias = (fecha_fin - fecha_inicio).days
        if dias <= 0:
            dias = 1  # mínimo 1 día de alquiler

        precio_por_dia = vehiculo.precio_por_dia
        costo_estimado = dias * precio_por_dia

        # ✅ KM / combustible iniciales desde el vehículo
        km_inicial = getattr(vehiculo, "km_actual", 0) or 0
        combustible_inicial = getattr(vehiculo, "combustible_actual", 0.0) or 0.0

        # Creamos objeto Alquiler
        alquiler = Alquiler(
            id_alquiler=None,
            id_cliente=id_cliente,
            id_vehiculo=id_vehiculo,
            id_empleado=id_empleado,
            fecha_inicio=fecha_inicio_iso,
            fecha_fin=fecha_fin_iso,
            precio_por_dia=precio_por_dia,
            estado="ABIERTO",
            total=costo_estimado,  # lo mantenemos como estimado, pero el cierre usará solo monto_extra
            km_inicial=km_inicial,
            km_final=None,
            combustible_inicial=combustible_inicial,
            combustible_final=None,
        )

        alquiler_creado = AlquilerRepository.crear(alquiler)

        # ✅ Marcar vehículo como ALQUILADO
        vehiculo.estado = "ALQUILADO"
        VehiculoRepository.actualizar(vehiculo)

        return True, alquiler_creado

    @staticmethod
    def listar_alquileres():
        alquileres = AlquilerRepository.listar()
        return True, alquileres

    @staticmethod
    def obtener_alquiler_por_id(id_alquiler):
        try:
            id_alquiler = int(id_alquiler)
        except (TypeError, ValueError):
            return False, "El ID de alquiler debe ser numérico."

        alquiler = AlquilerRepository.obtener_por_id(id_alquiler)
        if alquiler is None:
            return False, "No se encontró un alquiler con ese ID."
        return True, alquiler

    @staticmethod
    def cerrar_alquiler(id_alquiler, fecha_devolucion_str, km_final, combustible_final, monto_extra=0.0):
        # Buscar alquiler existente
        ok, alquiler_o_msg = AlquilerService.obtener_alquiler_por_id(id_alquiler)
        if not ok:
            return False, alquiler_o_msg

        alquiler = alquiler_o_msg

        if alquiler.estado != "ABIERTO":
            return False, "El alquiler ya está cerrado."

        # Validar fecha de devolución
        ok_dev, fecha_dev_o_msg = AlquilerService._parsear_fecha(fecha_devolucion_str)
        if not ok_dev:
            return False, fecha_dev_o_msg

        fecha_devolucion = fecha_dev_o_msg

        # Fecha de inicio en date
        ok_ini, fecha_ini_o_msg = AlquilerService._parsear_fecha(alquiler.fecha_inicio)
        if not ok_ini:
            return False, "La fecha de inicio almacenada del alquiler es inválida."

        fecha_inicio = fecha_ini_o_msg

        if fecha_devolucion < fecha_inicio:
            return False, "La fecha de devolución no puede ser anterior a la fecha de inicio."

        # --- CORRECCIÓN DE CÁLCULO DE PRECIO ---
        # 1. Calcular días reales
        dias_reales = (fecha_devolucion - fecha_inicio).days
        if dias_reales <= 0:
            dias_reales = 1 # Se cobra mínimo 1 día

        # 2. Obtener precio del vehículo
        vehiculo = VehiculoRepository.obtener_por_id(alquiler.id_vehiculo)
        if vehiculo is None:
            return False, "No se encontró el vehículo asociado al alquiler."

        # 3. Validar monto extra
        try:
            monto_extra = float(monto_extra)
        except (TypeError, ValueError):
            return False, "El monto extra debe ser numérico."
        if monto_extra < 0:
            return False, "El monto extra no puede ser negativo."

        # 4. CALCULAR TOTAL REAL (Días * Precio + Extra)
        costo_base = dias_reales * vehiculo.precio_por_dia
        total = costo_base + monto_extra
        # ---------------------------------------

        # Validar y parsear km_final / combustible_final
        try:
            km_final = float(km_final)
        except (TypeError, ValueError):
            return False, "El KM final debe ser numérico."

        try:
            combustible_final = float(combustible_final)
        except (TypeError, ValueError):
            return False, "El combustible final debe ser numérico."

        if km_final < 0:
            return False, "El KM final no puede ser negativo."

        km_inicial = getattr(alquiler, "km_inicial", 0) or 0
        if km_final < km_inicial:
            return False, f"El KM final ({km_final}) no puede ser menor al inicial ({km_inicial})."

        if combustible_final < 0:
            return False, "El combustible final no puede ser negativo."

        # Actualizar alquiler en la BD
        alquiler.km_final = km_final
        alquiler.combustible_final = combustible_final
        alquiler.total = total # Ahora sí guarda el total correcto
        alquiler.estado = "CERRADO"

        AlquilerRepository.actualizar_cierre(alquiler)

        # Actualizar vehículo
        vehiculo.km_actual = km_final
        vehiculo.combustible_actual = combustible_final
        vehiculo.estado = "DISPONIBLE"
        VehiculoRepository.actualizar(vehiculo)

        return True, alquiler
