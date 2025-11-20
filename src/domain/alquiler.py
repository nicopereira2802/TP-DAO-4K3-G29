class Alquiler:
    def __init__(
        self,
        id_alquiler,
        id_cliente,
        id_vehiculo,
        id_empleado,
        fecha_inicio,
        fecha_fin,
        precio_por_dia,
        estado="ABIERTO",
        total=0.0
    ):
        self.id_alquiler = id_alquiler
        self.id_cliente = id_cliente
        self.id_vehiculo = id_vehiculo
        self.id_empleado = id_empleado
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.precio_por_dia = precio_por_dia
        self.estado = estado
        self.total = total

    def __str__(self):
        return (
            f"Alquiler(id={self.id_alquiler}, cliente={self.id_cliente}, "
            f"vehiculo={self.id_vehiculo}, desde={self.fecha_inicio}, "
            f"hasta={self.fecha_fin}, estado={self.estado}, total={self.total})"
        )
