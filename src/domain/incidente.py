class Incidente:
    def __init__(self, id_incidente, id_alquiler, tipo, descripcion, monto, estado="PENDIENTE"):
        self.id_incidente = id_incidente
        self.id_alquiler = id_alquiler
        self.tipo = tipo
        self.descripcion = descripcion
        self.monto = monto
        self.estado = estado

    def __str__(self):
        return (
            f"Incidente(id={self.id_incidente}, alquiler={self.id_alquiler}, "
            f"tipo={self.tipo}, monto={self.monto}, estado={self.estado})"
        )
