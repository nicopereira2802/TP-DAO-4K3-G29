from collections import defaultdict

from src.repositories.alquiler_repository import AlquilerRepository
from src.repositories.incidente_repository import IncidenteRepository
from src.repositories.vehiculo_repository import VehiculoRepository
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.mantenimiento_repository import MantenimientoRepository


def _en_rango(fecha: str, desde: str, hasta: str) -> bool:
    """
    Compara fechas en formato 'AAAA-MM-DD' de forma inclusiva.
    Asume que todas vienen en ese formato.
    """
    if not fecha:
        return False
    return desde <= fecha <= hasta


# ---------------------------------------------------------------------
# 1) RESUMEN ECONÓMICO
# ---------------------------------------------------------------------
def obtener_resumen_economico(fecha_desde: str, fecha_hasta: str):
    if fecha_desde > fecha_hasta:
        return False, "La fecha DESDE no puede ser mayor que la fecha HASTA."

    alquileres = AlquilerRepository.listar()
    incidentes = IncidenteRepository.listar()

    alquiler_por_id = {a.id_alquiler: a for a in alquileres}

    total_alquileres = 0.0
    for a in alquileres:
        fecha_ini = getattr(a, "fecha_inicio", "") or ""
        estado = (getattr(a, "estado", "") or "").upper()
        if estado != "CERRADO":
            continue
        if not _en_rango(fecha_ini, fecha_desde, fecha_hasta):
            continue

        total = getattr(a, "total", 0.0) or 0.0
        try:
            total_alquileres += float(total)
        except (TypeError, ValueError):
            pass

    total_incidentes = 0.0
    for inc in incidentes:
        estado = (getattr(inc, "estado", "") or "").upper()
        if estado != "PAGADO":
            continue

        id_alq = getattr(inc, "id_alquiler", None)
        alq = alquiler_por_id.get(id_alq)
        if alq is None:
            continue

        fecha_ini = getattr(alq, "fecha_inicio", "") or ""
        if not _en_rango(fecha_ini, fecha_desde, fecha_hasta):
            continue

        monto = getattr(inc, "monto", 0.0) or 0.0
        try:
            total_incidentes += float(monto)
        except (TypeError, ValueError):
            pass

    total_general = total_alquileres + total_incidentes

    data = {
        "total_alquileres": round(total_alquileres, 2),
        "total_incidentes": round(total_incidentes, 2),
        "total_general": round(total_general, 2),
    }
    return True, data


# ---------------------------------------------------------------------
# 2) TOP VEHÍCULOS
# ---------------------------------------------------------------------
def obtener_top_vehiculos(fecha_desde: str, fecha_hasta: str, limite: int = 10):
    if fecha_desde > fecha_hasta:
        return False, "La fecha DESDE no puede ser mayor que la fecha HASTA."

    alquileres = AlquilerRepository.listar()
    vehiculos = VehiculoRepository.listar()
    veh_por_id = {v.id_vehiculo: v for v in vehiculos}

    stats = defaultdict(lambda: {"cantidad": 0, "total": 0.0})

    for a in alquileres:
        fecha_ini = getattr(a, "fecha_inicio", "") or ""
        estado = (getattr(a, "estado", "") or "").upper()
        if estado != "CERRADO":
            continue
        if not _en_rango(fecha_ini, fecha_desde, fecha_hasta):
            continue

        id_v = getattr(a, "id_vehiculo", None)
        if id_v is None:
            continue

        stats[id_v]["cantidad"] += 1
        total = getattr(a, "total", 0.0) or 0.0
        try:
            stats[id_v]["total"] += float(total)
        except (TypeError, ValueError):
            pass

    filas = []
    for id_v, info in stats.items():
        v = veh_por_id.get(id_v)
        if v is not None:
            texto_v = f"{v.patente} ({v.marca} {v.modelo})"
        else:
            texto_v = f"Vehículo {id_v}"

        filas.append(
            {
                "vehiculo": texto_v,
                "cantidad": info["cantidad"],
                "total": round(info["total"], 2),
            }
        )

    filas.sort(key=lambda x: x["cantidad"], reverse=True)
    if limite and limite > 0:
        filas = filas[:limite]

    return True, filas


# ---------------------------------------------------------------------
# 3) TOP CLIENTES
# ---------------------------------------------------------------------
def obtener_top_clientes(fecha_desde: str, fecha_hasta: str, limite: int = 10):
    """
    Devuelve lista de diccionarios con:
      - cliente (nombre legible)
      - dni
      - cantidad (alquileres)
      - total (facturado)
    """
    if fecha_desde > fecha_hasta:
        return False, "La fecha DESDE no puede ser mayor que la fecha HASTA."

    alquileres = AlquilerRepository.listar()
    clientes = ClienteRepository.listar()

    # Soportar Cliente con atributo id_cliente, id o incluso dict
    cli_por_id = {}
    for c in clientes:
        if isinstance(c, dict):
            cid = c.get("id_cliente") or c.get("id")
        else:
            cid = getattr(c, "id_cliente", None)
            if cid is None:
                cid = getattr(c, "id", None)
        if cid is None:
            continue
        cli_por_id[cid] = c

    stats = defaultdict(lambda: {"cantidad": 0, "total": 0.0})

    for a in alquileres:
        fecha_ini = getattr(a, "fecha_inicio", "") or ""
        estado = (getattr(a, "estado", "") or "").upper()
        if estado != "CERRADO":
            continue
        if not _en_rango(fecha_ini, fecha_desde, fecha_hasta):
            continue

        id_c = getattr(a, "id_cliente", None)
        if id_c is None:
            continue

        stats[id_c]["cantidad"] += 1
        total = getattr(a, "total", 0.0) or 0.0
        try:
            stats[id_c]["total"] += float(total)
        except (TypeError, ValueError):
            pass

    filas = []
    for id_c, info in stats.items():
        c = cli_por_id.get(id_c)

        if isinstance(c, dict):
            nombre = c.get("nombre", "")
            apellido = c.get("apellido", "")
            dni = c.get("dni", "")
        elif c is not None:
            nombre = getattr(c, "nombre", "") or ""
            apellido = getattr(c, "apellido", "") or ""
            dni = getattr(c, "dni", "") or ""
        else:
            nombre = ""
            apellido = ""
            dni = ""

        if c is not None:
            texto_c = f"{nombre} {apellido}".strip() or f"Cliente {id_c}"
        else:
            texto_c = f"Cliente {id_c}"

        filas.append(
            {
                "cliente": texto_c,
                "dni": dni,
                "cantidad": info["cantidad"],
                "total": round(info["total"], 2),
            }
        )

    filas.sort(key=lambda x: x["cantidad"], reverse=True)
    if limite and limite > 0:
        filas = filas[:limite]

    return True, filas


# ---------------------------------------------------------------------
# 4) ESTADO DE FLOTA EN UNA FECHA
# ---------------------------------------------------------------------
def obtener_estado_flota(fecha_ref: str):
    vehiculos = VehiculoRepository.listar()
    alquileres = AlquilerRepository.listar()
    mantenimientos = MantenimientoRepository.listar()

    alq_por_veh = defaultdict(list)
    for a in alquileres:
        alq_por_veh[getattr(a, "id_vehiculo", None)].append(a)

    mant_por_veh = defaultdict(list)
    for m in mantenimientos:
        mant_por_veh[getattr(m, "id_vehiculo", None)].append(m)

    detalle = []
    resumen = {"disponibles": 0, "alquilados": 0, "mantenimiento": 0}

    for v in vehiculos:
        if not v.activo:
            continue

        id_v = v.id_vehiculo
        texto_v = f"{v.patente} ({v.marca} {v.modelo})"

        estado_actual = "DISPONIBLE"

        # mantenimiento
        en_mant = False
        for m in mant_por_veh.get(id_v, []):
            f_ini = getattr(m, "fecha_inicio", "") or ""
            f_fin = getattr(m, "fecha_fin", "") or ""
            if f_ini and f_fin and f_ini <= fecha_ref <= f_fin:
                en_mant = True
                break

        if en_mant:
            estado_actual = "MANTENIMIENTO"
        else:
            # alquiler
            en_alquiler = False
            for a in alq_por_veh.get(id_v, []):
                estado_alq = (getattr(a, "estado", "") or "").upper()
                if estado_alq != "ABIERTO":
                    continue
                f_ini = getattr(a, "fecha_inicio", "") or ""
                f_fin = getattr(a, "fecha_fin", "") or ""
                if f_ini and f_fin and f_ini <= fecha_ref <= f_fin:
                    en_alquiler = True
                    break

            if en_alquiler:
                estado_actual = "ALQUILADO"

        if estado_actual == "MANTENIMIENTO":
            resumen["mantenimiento"] += 1
        elif estado_actual == "ALQUILADO":
            resumen["alquilados"] += 1
        else:
            resumen["disponibles"] += 1

        detalle.append(
            {
                "vehiculo": texto_v,
                "estado": estado_actual,
            }
        )

    data = {
        "resumen": resumen,
        "detalle": detalle,
    }
    return True, data


# ---------------------------------------------------------------------
# 5) ALQUILERES POR MES
# ---------------------------------------------------------------------
def obtener_alquileres_por_mes(fecha_desde: str, fecha_hasta: str):
    """
    Devuelve (ok, filas_o_msg).

    filas = [
      {
        "periodo": "AAAA-MM",
        "anio": 2025,
        "mes": 1,
        "cantidad": 5,
        "total": 123456.78,
      },
      ...
    ]
    """
    if fecha_desde > fecha_hasta:
        return False, "La fecha DESDE no puede ser mayor que la fecha HASTA."

    alquileres = AlquilerRepository.listar()
    stats = defaultdict(lambda: {"cantidad": 0, "total": 0.0})

    for a in alquileres:
        fecha_ini = getattr(a, "fecha_inicio", "") or ""
        estado = (getattr(a, "estado", "") or "").upper()
        if estado != "CERRADO":
            continue
        if not _en_rango(fecha_ini, fecha_desde, fecha_hasta):
            continue

        periodo = fecha_ini[:7]  # AAAA-MM
        stats[periodo]["cantidad"] += 1

        total = getattr(a, "total", 0.0) or 0.0
        try:
            stats[periodo]["total"] += float(total)
        except (TypeError, ValueError):
            pass

    filas = []
    for periodo, info in stats.items():
        try:
            anio = int(periodo[:4])
            mes = int(periodo[5:7])
        except Exception:
            continue

        filas.append(
            {
                "periodo": periodo,
                "anio": anio,
                "mes": mes,
                "cantidad": info["cantidad"],
                "total": round(info["total"], 2),
            }
        )

    filas.sort(key=lambda x: (x["anio"], x["mes"]))
    return True, filas


# ---------------------------------------------------------------------
# 6) ALQUILERES POR TRIMESTRE
# ---------------------------------------------------------------------
def obtener_alquileres_por_trimestre(fecha_desde: str, fecha_hasta: str):
    """
    Devuelve (ok, filas_o_msg).

    filas = [
      {
        "anio": 2025,
        "trimestre": 1,
        "cantidad": 12,
        "total": 345678.90,
      },
      ...
    ]
    """
    ok, filas_mes_o_msg = obtener_alquileres_por_mes(fecha_desde, fecha_hasta)
    if not ok:
        return False, filas_mes_o_msg

    filas_mes = filas_mes_o_msg
    stats = defaultdict(lambda: {"cantidad": 0, "total": 0.0})

    for fila in filas_mes:
        anio = fila["anio"]
        mes = fila["mes"]
        trimestre = (mes - 1) // 3 + 1
        clave = (anio, trimestre)

        stats[clave]["cantidad"] += fila["cantidad"]
        stats[clave]["total"] += fila["total"]

    filas_trim = []
    for (anio, trimestre), info in stats.items():
        filas_trim.append(
            {
                "anio": anio,
                "trimestre": trimestre,
                "cantidad": info["cantidad"],
                "total": round(info["total"], 2),
            }
        )

    filas_trim.sort(key=lambda x: (x["anio"], x["trimestre"]))
    return True, filas_trim
