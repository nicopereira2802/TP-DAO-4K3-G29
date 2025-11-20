from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from src.reports import reportes_tablas as rpt


def _titulo_y_encabezado(c, titulo, subtitulo):
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, 27 * cm, titulo)
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 26.2 * cm, subtitulo)
    c.line(2 * cm, 26 * cm, 19 * cm, 26 * cm)


def _nueva_linea(y_actual, salto=0.6):
    return y_actual - salto * cm


def export_resumen_economico_pdf(ruta_pdf, fecha_desde, fecha_hasta):
    ok, data = rpt.obtener_resumen_economico(fecha_desde, fecha_hasta)
    if not ok:
        return False, data

    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    _titulo_y_encabezado(
        c,
        "Resumen económico",
        f"Período: {fecha_desde} a {fecha_hasta}",
    )

    y = 25 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Concepto")
    c.drawString(12 * cm, y, "Monto $")
    y = _nueva_linea(y)

    c.setFont("Helvetica", 10)

    filas = [
        ("Alquileres", data["total_alquileres"]),
        ("Incidentes pagados", data["total_incidentes"]),
        ("TOTAL GENERAL", data["total_general"]),
    ]

    for concepto, monto in filas:
        if y < 2 * cm:
            c.showPage()
            y = 27 * cm
        if concepto == "TOTAL GENERAL":
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y, concepto)
        c.drawRightString(18 * cm, y, f"${monto:.2f}")
        y = _nueva_linea(y)

    c.showPage()
    c.save()
    return True, "PDF generado correctamente."


def export_top_vehiculos_pdf(ruta_pdf, fecha_desde, fecha_hasta, limite=20):
    ok, filas = rpt.obtener_top_vehiculos(fecha_desde, fecha_hasta, limite=limite)
    if not ok:
        return False, filas

    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    _titulo_y_encabezado(
        c,
        "Vehículos más alquilados",
        f"Período: {fecha_desde} a {fecha_hasta}",
    )

    y = 25 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Vehículo")
    c.drawString(11 * cm, y, "Cant.")
    c.drawString(14 * cm, y, "Total $")
    y = _nueva_linea(y)

    c.setFont("Helvetica", 10)

    for row in filas:
        if y < 2 * cm:
            c.showPage()
            y = 27 * cm
        vehiculo = row["vehiculo"]
        if len(vehiculo) > 40:
            vehiculo = vehiculo[:37] + "..."
        c.drawString(2 * cm, y, vehiculo)
        c.drawRightString(13 * cm, y, str(row["cantidad"]))
        c.drawRightString(18 * cm, y, f"{row['total']:.2f}")
        y = _nueva_linea(y)

    c.showPage()
    c.save()
    return True, "PDF generado correctamente."


def export_top_clientes_pdf(ruta_pdf, fecha_desde, fecha_hasta, limite=20):
    ok, filas = rpt.obtener_top_clientes(fecha_desde, fecha_hasta, limite=limite)
    if not ok:
        return False, filas

    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    _titulo_y_encabezado(
        c,
        "Clientes con más alquileres",
        f"Período: {fecha_desde} a {fecha_hasta}",
    )

    y = 25 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Cliente")
    c.drawString(9 * cm, y, "DNI")
    c.drawString(13 * cm, y, "Cant.")
    c.drawString(16 * cm, y, "Total $")
    y = _nueva_linea(y)

    c.setFont("Helvetica", 10)

    for row in filas:
        if y < 2 * cm:
            c.showPage()
            y = 27 * cm
        cliente = row["cliente"] or ""
        if len(cliente) > 30:
            cliente = cliente[:27] + "..."
        c.drawString(2 * cm, y, cliente)
        c.drawString(9 * cm, y, row["dni"])
        c.drawRightString(14.5 * cm, y, str(row["cantidad"]))
        c.drawRightString(18 * cm, y, f"{row['total']:.2f}")
        y = _nueva_linea(y)

    c.showPage()
    c.save()
    return True, "PDF generado correctamente."


def export_estado_flota_pdf(ruta_pdf, fecha_ref=None):
    if not fecha_ref:
        fecha_ref = date.today().isoformat()

    ok, data = rpt.obtener_estado_flota(fecha_ref)
    if not ok:
        return False, data

    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    _titulo_y_encabezado(
        c,
        "Estado de la flota",
        f"Fecha de referencia: {fecha_ref}",
    )

    res = data["resumen"]
    y = 25 * cm
    c.setFont("Helvetica", 10)
    c.drawString(
        2 * cm,
        y,
        f"Disponibles: {res['disponibles']}  |  Alquilados: {res['alquilados']}  |  En mantenimiento: {res['mantenimiento']}",
    )
    y = _nueva_linea(y, 1.0)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Vehículo")
    c.drawString(12 * cm, y, "Estado")
    y = _nueva_linea(y)

    c.setFont("Helvetica", 10)

    for row in data["detalle"]:
        if y < 2 * cm:
            c.showPage()
            y = 27 * cm
        veh = row["vehiculo"]
        if len(veh) > 40:
            veh = veh[:37] + "..."
        c.drawString(2 * cm, y, veh)
        c.drawString(12 * cm, y, row["estado"])
        y = _nueva_linea(y)

    c.showPage()
    c.save()
    return True, "PDF generado correctamente."
