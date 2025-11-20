from datetime import date

from matplotlib.figure import Figure

from src.reports import reportes_tablas as rpt


def grafico_resumen_economico(fecha_desde: str, fecha_hasta: str):
    """
    Devuelve (ok, fig_o_msg).
    Gráfico de barras con:
      - total alquileres
      - total incidentes
      - total general
    """
    ok, data = rpt.obtener_resumen_economico(fecha_desde, fecha_hasta)
    if not ok:
        return False, data

    fig = Figure(figsize=(8, 10))
    ax = fig.add_subplot(111)

    etiquetas = ["Alquileres", "Incidentes", "Total"]
    valores = [
        data["total_alquileres"],
        data["total_incidentes"],
        data["total_general"],
    ]

    ax.bar(etiquetas, valores)
    ax.set_title(f"Resumen económico\n{fecha_desde} a {fecha_hasta}")
    ax.set_ylabel("Monto $")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    return True, fig


def grafico_top_vehiculos(fecha_desde: str, fecha_hasta: str, limite: int = 10):
    """
    Devuelve (ok, fig_o_msg).
    Gráfico de barras con cantidad de alquileres por vehículo.
    """
    ok, filas = rpt.obtener_top_vehiculos(fecha_desde, fecha_hasta, limite=limite)
    if not ok:
        return False, filas

    if not filas:
        return False, "No hay datos de vehículos en ese rango para graficar."

    etiquetas = [f["vehiculo"] for f in filas]
    valores = [f["cantidad"] for f in filas]

    # opcional: acortar etiquetas
    etiquetas_cortas = [
        e if len(e) <= 20 else e[:17] + "..."
        for e in etiquetas
    ]

    fig = Figure(figsize=(8, 200))
    ax = fig.add_subplot(111)

    x = list(range(len(etiquetas_cortas)))
    ax.bar(x, valores)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas_cortas, rotation=45, ha="right")
    ax.set_ylabel("Cantidad de alquileres")
    ax.set_title(f"Vehículos más alquilados\n{fecha_desde} a {fecha_hasta}")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    return True, fig


def grafico_top_clientes(fecha_desde: str, fecha_hasta: str, limite: int = 10):
    """
    Devuelve (ok, fig_o_msg).
    Gráfico de barras con cantidad de alquileres por cliente.
    """
    ok, filas = rpt.obtener_top_clientes(fecha_desde, fecha_hasta, limite=limite)
    if not ok:
        return False, filas

    if not filas:
        return False, "No hay datos de clientes en ese rango para graficar."

    etiquetas = [f["cliente"] or f"Cliente {i+1}" for i, f in enumerate(filas)]
    valores = [f["cantidad"] for f in filas]

    etiquetas_cortas = [
        e if len(e) <= 20 else e[:17] + "..."
        for e in etiquetas
    ]

    fig = Figure(figsize=(8, 20))
    ax = fig.add_subplot(111)

    x = list(range(len(etiquetas_cortas)))
    ax.bar(x, valores)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas_cortas, rotation=45, ha="right")
    ax.set_ylabel("Cantidad de alquileres")
    ax.set_title(f"Clientes con más alquileres\n{fecha_desde} a {fecha_hasta}")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    return True, fig


def grafico_estado_flota(fecha_ref: str | None = None):
    """
    Devuelve (ok, fig_o_msg).
    Gráfico de torta con:
      - disponibles
      - alquilados
      - mantenimiento
    """
    if not fecha_ref:
        fecha_ref = date.today().isoformat()

    ok, data = rpt.obtener_estado_flota(fecha_ref)
    if not ok:
        return False, data

    resumen = data["resumen"]
    disponibles = resumen.get("disponibles", 0)
    alquilados = resumen.get("alquilados", 0)
    mantenimiento = resumen.get("mantenimiento", 0)

    total = disponibles + alquilados + mantenimiento
    if total == 0:
        return False, "No hay vehículos activos para graficar el estado de la flota."

    valores = [disponibles, alquilados, mantenimiento]
    etiquetas = ["Disponibles", "Alquilados", "Mantenimiento"]

    fig = Figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)

    ax.pie(
        valores,
        labels=etiquetas,
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title(f"Estado de la flota\n{fecha_ref}")

    return True, fig
