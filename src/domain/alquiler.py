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
        total=0.0,
        km_inicial=0.0,
        km_final=None,
        combustible_inicial=0.0,
        combustible_final=None,
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
        self.km_inicial = km_inicial
        self.km_final = km_final
        self.combustible_inicial = combustible_inicial
        self.combustible_final = combustible_final

    def __str__(self):
        return (
            f"Alquiler(id={self.id_alquiler}, cliente={self.id_cliente}, "
            f"vehiculo={self.id_vehiculo}, desde={self.fecha_inicio}, "
            f"hasta={self.fecha_fin}, estado={self.estado}, total={self.total}, "
            f"km_inicial={self.km_inicial}, km_final={self.km_final}, "
            f"combustible_inicial={self.combustible_inicial}, "
            f"combustible_final={self.combustible_final})"
        )
